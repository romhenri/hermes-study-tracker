#!/usr/bin/env python3
"""Memória acadêmica do Study Tracker. SQLite, só stdlib.

Uso (o agente Hermes chama isto pelo terminal):
  study.py add      "Cálculo I" "Integrais/Substituição"
  study.py status   "Cálculo I" "Integrais" done        # todo | doing | done
  study.py log      "Cálculo I" "Integrais" --min 120 --correct 7 --total 10 \
                    --mistakes "sinal,constante" --notes "travei em trigonométricas"
  study.py map      ["Cálculo I"]
  study.py report   ["Cálculo I"]
  study.py review   [--subject "Cálculo I"] [--n 5]
  study.py compare  "Cálculo I" [--days 14]
  study.py history  "Cálculo I" ["Integrais"] [--n 10]
"""
import argparse
import os
import sqlite3
import sys
from collections import Counter
from datetime import date, timedelta

DB = os.environ.get("STUDY_DB", os.path.expanduser("~/.hermes/study-tracker.db"))
STATUS = {"todo": "não iniciado", "doing": "estudando", "done": "concluído"}

# Domínio: olha só as últimas sessões com exercícios, para refletir o nível atual.
RECENT_SESSIONS = 3
MASTERED_ACC, MASTERED_MIN_Q = 0.8, 10
STRUGGLE_ACC, STRUGGLE_MIN_Q = 0.6, 5


def connect(path=DB):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            subject TEXT NOT NULL COLLATE NOCASE,
            path TEXT NOT NULL COLLATE NOCASE,
            status TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo','doing','done')),
            UNIQUE (subject, path));
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            topic_id INTEGER NOT NULL REFERENCES topics(id),
            day TEXT NOT NULL,
            minutes INTEGER NOT NULL DEFAULT 0 CHECK (minutes >= 0),
            correct INTEGER NOT NULL DEFAULT 0 CHECK (correct >= 0),
            total INTEGER NOT NULL DEFAULT 0 CHECK (total >= correct),
            mistakes TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '');
    """)
    return db


def topic_id(db, subject, path):
    path = "/".join(p.strip() for p in path.split("/") if p.strip())
    db.execute("INSERT OR IGNORE INTO topics (subject, path) VALUES (?, ?)", (subject.strip(), path))
    return db.execute("SELECT id FROM topics WHERE subject = ? AND path = ?", (subject.strip(), path)).fetchone()[0]


def topics(db, subject=None):
    q = "SELECT * FROM topics" + (" WHERE subject = ?" if subject else "") + " ORDER BY subject, path"
    return db.execute(q, (subject,) if subject else ()).fetchall()


def stats(db, tid, today):
    rows = db.execute("SELECT * FROM sessions WHERE topic_id = ? ORDER BY day, id", (tid,)).fetchall()
    ex = [r for r in rows if r["total"]][-RECENT_SESSIONS:]
    correct, total = sum(r["correct"] for r in ex), sum(r["total"] for r in ex)
    acc = correct / total if total else None
    if acc is None:
        level = "sem exercícios"
    elif acc >= MASTERED_ACC and total >= MASTERED_MIN_Q:
        level = "dominado"
    elif acc < STRUGGLE_ACC and total >= STRUGGLE_MIN_Q:
        level = "dificuldade"
    else:
        level = "em consolidação"
    last = rows[-1]["day"] if rows else None
    mistakes = Counter(m.strip().lower() for r in rows for m in r["mistakes"].split(",") if m.strip())
    return {
        "sessions": len(rows),
        "minutes": sum(r["minutes"] for r in rows),
        "acc": acc,
        "recent_q": total,
        "level": level,
        "last": last,
        "days_since": (today - date.fromisoformat(last)).days if last else None,
        "recurring": [m for m, n in mistakes.most_common() if n >= 2],
    }


def review_score(t, s):
    """Maior = revisar antes. ponytail: heurística linear, troque por SM-2 se quiser repetição espaçada de verdade."""
    if not s["sessions"]:
        return None
    score = min(s["days_since"] / 14, 1.5)
    score += 2 * (1 - s["acc"]) if s["acc"] is not None else 0.5
    score += 0.3 * len(s["recurring"])
    if t["status"] == "done" and s["level"] != "dominado":
        score += 0.5  # "concluído" sem domínio comprovado
    return round(score, 2)


def fmt_acc(acc):
    return "—" if acc is None else f"{acc:.0%}"


def fmt_min(m):
    return f"{m // 60}h{m % 60:02d}" if m >= 60 else f"{m}min"


def line(t, s):
    bits = [f"[{STATUS[t['status']]}]", s["level"], f"acerto recente {fmt_acc(s['acc'])} ({s['recent_q']}q)",
            f"{fmt_min(s['minutes'])} em {s['sessions']} sessões"]
    if s["last"]:
        bits.append(f"último estudo {s['last']} ({s['days_since']}d atrás)")
    if s["recurring"]:
        bits.append("erros recorrentes: " + ", ".join(s["recurring"]))
    return f"  {t['path']}: " + " | ".join(bits)


def cmd_map(db, a, today):
    cur = None
    for t in topics(db, a.subject):
        if t["subject"] != cur:
            cur = t["subject"]
            print(f"\n## {cur}")
        print(line(t, stats(db, t["id"], today)))
    if cur is None:
        print("Nenhum conteúdo cadastrado ainda.")


def cmd_report(db, a, today):
    subjects = sorted({t["subject"] for t in topics(db, a.subject)})
    if not subjects:
        print("Nenhum conteúdo cadastrado ainda.")
    for subj in subjects:
        ts = [(t, stats(db, t["id"], today)) for t in topics(db, subj)]
        sess = [s for _, s in ts]
        c = Counter(t["status"] for t, _ in ts)
        q = db.execute("SELECT SUM(correct), SUM(total) FROM sessions JOIN topics ON topics.id = topic_id "
                       "WHERE subject = ?", (subj,)).fetchone()
        print(f"\n## {subj}")
        print(f"  Conteúdos: {len(ts)} | concluídos {c['done']} | estudando {c['doing']} | não iniciados {c['todo']}")
        print(f"  Tempo total: {fmt_min(sum(s['minutes'] for s in sess))} | "
              f"acerto geral: {fmt_acc(q[0] / q[1] if q[1] else None)} ({q[1] or 0} exercícios)")
        for label, level in (("Dominados", "dominado"), ("Dificuldades", "dificuldade")):
            names = [t["path"] for t, s in ts if s["level"] == level]
            print(f"  {label}: {', '.join(names) or 'nenhum'}")
        fake = [t["path"] for t, s in ts if t["status"] == "done" and s["level"] != "dominado"]
        if fake:
            print(f"  Concluídos sem domínio comprovado: {', '.join(fake)}")
        prio = sorted(((review_score(t, s), t["path"]) for t, s in ts if review_score(t, s) is not None), reverse=True)
        print(f"  Prioridades de revisão: {', '.join(p for _, p in prio[:3]) or 'nenhuma'}")
        todo = [t["path"] for t, _ in ts if t["status"] == "todo"]
        if todo:
            print(f"  Ainda não iniciados: {', '.join(todo)}")


def cmd_review(db, a, today):
    ranked = []
    for t in topics(db, a.subject):
        s = stats(db, t["id"], today)
        score = review_score(t, s)
        if score is not None:
            ranked.append((score, t, s))
    ranked.sort(key=lambda x: x[0], reverse=True)
    if not ranked:
        print("Sem histórico suficiente para recomendar revisões.")
    for score, t, s in ranked[: a.n]:
        print(f"{score:>5}  {t['subject']} › {t['path']}: {s['level']}, acerto {fmt_acc(s['acc'])}, "
              f"{s['days_since']}d sem estudar" + (f", erros: {', '.join(s['recurring'])}" if s["recurring"] else ""))


def cmd_compare(db, a, today):
    def window(start, end):
        r = db.execute("SELECT SUM(minutes), SUM(correct), SUM(total), COUNT(*) FROM sessions "
                       "JOIN topics ON topics.id = topic_id WHERE subject = ? AND day > ? AND day <= ?",
                       (a.subject, start.isoformat(), end.isoformat())).fetchone()
        return {"min": r[0] or 0, "acc": r[1] / r[2] if r[2] else None, "q": r[2] or 0, "n": r[3]}

    cur = window(today - timedelta(days=a.days), today)
    prev = window(today - timedelta(days=2 * a.days), today - timedelta(days=a.days))
    for label, w in ((f"Últimos {a.days} dias", cur), (f"{a.days} dias anteriores", prev)):
        print(f"{label}: {w['n']} sessões, {fmt_min(w['min'])}, acerto {fmt_acc(w['acc'])} ({w['q']}q)")
    if cur["acc"] is not None and prev["acc"] is not None:
        d = (cur["acc"] - prev["acc"]) * 100
        print(f"Variação de acerto: {d:+.0f} p.p. ({'melhora' if d > 2 else 'queda' if d < -2 else 'estável'})")


def cmd_history(db, a, today):
    q = ("SELECT day, path, minutes, correct, total, mistakes, notes FROM sessions JOIN topics ON topics.id = topic_id "
         "WHERE subject = ?" + (" AND (path = ? OR path LIKE ?)" if a.path else "") + " ORDER BY day DESC, sessions.id DESC LIMIT ?")
    args = [a.subject] + ([a.path, a.path + "/%"] if a.path else []) + [a.n]
    for r in db.execute(q, args):
        ex = f", {r['correct']}/{r['total']}" if r["total"] else ""
        extra = "".join(f" | {k}: {r[k]}" for k in ("mistakes", "notes") if r[k])
        print(f"{r['day']}  {r['path']}: {fmt_min(r['minutes'])}{ex}{extra}")


def main(argv=None, db=None):
    p = argparse.ArgumentParser(description="Study Tracker")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add"); s.add_argument("subject"); s.add_argument("path")
    s = sub.add_parser("status"); s.add_argument("subject"); s.add_argument("path"); s.add_argument("status", choices=STATUS)
    s = sub.add_parser("log")
    s.add_argument("subject"); s.add_argument("path")
    s.add_argument("--min", type=int, default=0); s.add_argument("--correct", type=int, default=0)
    s.add_argument("--total", type=int, default=0); s.add_argument("--mistakes", default="")
    s.add_argument("--notes", default=""); s.add_argument("--date", default=None)
    for name in ("map", "report"):
        s = sub.add_parser(name); s.add_argument("subject", nargs="?")
    s = sub.add_parser("review"); s.add_argument("--subject"); s.add_argument("--n", type=int, default=5)
    s = sub.add_parser("compare"); s.add_argument("subject"); s.add_argument("--days", type=int, default=14)
    s = sub.add_parser("history"); s.add_argument("subject"); s.add_argument("path", nargs="?"); s.add_argument("--n", type=int, default=10)
    a = p.parse_args(argv)

    db = db or connect()
    today = date.fromisoformat(os.environ.get("STUDY_TODAY", date.today().isoformat()))
    if a.cmd == "add":
        topic_id(db, a.subject, a.path)
        print(f"Cadastrado: {a.subject} › {a.path}")
    elif a.cmd == "status":
        db.execute("UPDATE topics SET status = ? WHERE id = ?", (a.status, topic_id(db, a.subject, a.path)))
        print(f"{a.subject} › {a.path}: {STATUS[a.status]}")
    elif a.cmd == "log":
        if a.correct > a.total:
            sys.exit("Erro: --correct maior que --total.")
        day = a.date or today.isoformat()
        date.fromisoformat(day)  # valida formato
        tid = topic_id(db, a.subject, a.path)
        db.execute("INSERT INTO sessions (topic_id, day, minutes, correct, total, mistakes, notes) VALUES (?,?,?,?,?,?,?)",
                   (tid, day, a.min, a.correct, a.total, a.mistakes, a.notes))
        db.execute("UPDATE topics SET status = 'doing' WHERE id = ? AND status = 'todo'", (tid,))
        t = db.execute("SELECT * FROM topics WHERE id = ?", (tid,)).fetchone()
        print("Sessão registrada.\n" + line(t, stats(db, tid, today)))
    else:
        {"map": cmd_map, "report": cmd_report, "review": cmd_review,
         "compare": cmd_compare, "history": cmd_history}[a.cmd](db, a, today)
    db.commit()


if __name__ == "__main__":
    main()
