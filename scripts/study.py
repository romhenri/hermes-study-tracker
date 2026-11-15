#!/usr/bin/env python3
"""Memória acadêmica do Study Tracker. Um arquivo Markdown por disciplina, só stdlib.

Uso (o agente Hermes chama isto pelo terminal):
  study.py setup    "Cálculo I" "Limites" "Derivadas/Regra da cadeia" "Integrais"
  study.py add      "Cálculo I" "Integrais/Por partes"
  study.py status   "Cálculo I" "Limites" done              # todo | doing | done
  study.py log      "Cálculo I" "Integrais" --correct 7 --total 10 \
                    --mistakes "erro de sinal,constante" --notes "travei em trigonométricas"
  study.py map      ["Cálculo I"]
  study.py report   ["Cálculo I"]
  study.py review   [--subject "Cálculo I"] [--n 5]
  study.py compare  "Cálculo I" [--days 14]
  study.py history  "Cálculo I" ["Integrais"] [--n 10]
  study.py exam     "Cálculo I" 2026-12-02 [--name P1] [--topics "Limites,Derivadas"]
  study.py exams    [--subject "Cálculo I"]

Formato de cada arquivo (editável à mão):
  # Cálculo I
  ## Assuntos
  - [ ] Limites                       [ ] não iniciado, [/] estudando, [x] concluído
  - [/] Derivadas
    - [x] Regra da cadeia             subassunto = 2 espaços de recuo
  ## Registro
  - 2026-11-14 | Derivadas | 7/10 | erros: erro de sinal | nota: texto livre
  - 2026-11-15 | Limites | —         sessão sem exercícios

Datas/Provas.md:
  - 2026-12-02 | Cálculo I | P1 | assuntos: Limites, Derivadas     sem "assuntos:" = ementa inteira
"""
import argparse
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

# A raiz do vault é o repo; resolve() segue o symlink de instalação.
ROOT = Path(os.environ.get("STUDY_ROOT") or Path(__file__).resolve().parents[1]).expanduser()
DIR = ROOT / "Disciplinas"
EXAMS = ROOT / "Datas" / "Provas.md"
MARK = {" ": "todo", "/": "doing", "~": "doing", "x": "done"}  # "~" aceito por compatibilidade
SYMBOL = {"todo": " ", "doing": "/", "done": "x"}
STATUS = {"todo": "não iniciado", "doing": "estudando", "done": "concluído"}
TOPIC_RE = re.compile(r"^(\s*)- \[([ /~xX])\] (.+?)\s*$")
LOG_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) \| (.+?) \| (?:(\d+)/(\d+)|—)(?: \| (.*))?$")
EXAM_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) \| (.+?) \| (.+?)(?: \| assuntos: (.*))?$")

# Prova a até URGENT_DAYS dias puxa seus assuntos não dominados para o topo da revisão.
URGENT_DAYS = 21

# Domínio: olha só as últimas sessões com exercícios, para refletir o nível atual.
RECENT_SESSIONS = 3
MASTERED_ACC, MASTERED_MIN_Q = 0.8, 10
STRUGGLE_ACC, STRUGGLE_MIN_Q = 0.6, 5


def norm(s):
    """Sem acento, minúsculo, espaços colapsados: "Integráis " == "integrais"."""
    return " ".join(unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().casefold().split())


def key(path):
    return "/".join(norm(p) for p in path.split("/") if p.strip())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")


def clean(s):
    return " ".join(s.replace("|", "/").split())


class Discipline:
    def __init__(self, file):
        self.file = file
        self.lines = file.read_text(encoding="utf-8").splitlines()
        self.parse()

    def parse(self):
        self.title = next((l[2:].strip() for l in self.lines if l.startswith("# ")), self.file.stem)
        self.topics, self.logs, self.sections = [], [], {}
        section, stack = None, []
        for i, l in enumerate(self.lines):
            if l.startswith("## "):
                section = norm(l[3:])
                self.sections[section] = i
            elif section == "assuntos" and (m := TOPIC_RE.match(l)):
                stack = stack[: len(m[1].expandtabs(2)) // 2] + [m[3]]
                self.topics.append({"path": "/".join(stack), "status": MARK[m[2].lower()], "line": i})
            elif section == "registro" and (m := LOG_RE.match(l)):
                log = {"day": m[1], "path": m[2], "correct": int(m[3] or 0), "total": int(m[4] or 0),
                       "mistakes": [], "notes": ""}
                for field in (m[5] or "").split(" | "):
                    label, _, value = field.partition(":")
                    if norm(label) == "erros":
                        log["mistakes"] = [x.strip() for x in value.split(",") if x.strip()]
                    elif norm(label) == "nota":
                        log["notes"] = value.strip()
                self.logs.append(log)
        keys = [key(t["path"]) for t in self.topics]
        for t, k in zip(self.topics, keys):
            t["leaf"] = not any(o.startswith(k + "/") for o in keys)

    def find(self, path):
        """Caminho completo, ou só o nome de um subassunto ("MRUV" acha "Cinemática/MRUV") se for único."""
        k = key(path)
        if t := next((t for t in self.topics if key(t["path"]) == k), None):
            return t
        if "/" in k:
            return None
        leaves = [t for t in self.topics if key(t["path"]).rsplit("/", 1)[-1] == k]
        if len(leaves) > 1:
            sys.exit(f"Erro: '{path}' é ambíguo em {self.title}: " + ", ".join(t["path"] for t in leaves))
        return leaves[0] if leaves else None

    def section_end(self, name):
        """Índice logo após a última linha não vazia da seção (cria a seção se faltar)."""
        if norm(name) not in self.sections:
            self.lines += ["", f"## {name}"]
            self.parse()
        end = start = self.sections[norm(name)]
        for i in range(start + 1, len(self.lines)):
            if self.lines[i].startswith("## "):
                break
            if self.lines[i].strip():
                end = i
        return end + 1

    def add_topic(self, path):
        """Insere sem reescrever o resto do arquivo. Devolve (tópico, criado?)."""
        parts = [p.strip() for p in path.split("/") if p.strip()]
        if not parts:
            sys.exit("Erro: assunto vazio.")
        if t := self.find("/".join(parts)):
            return t, False
        if len(parts) > 1:
            parent, _ = self.add_topic("/".join(parts[:-1]))
            pk = key(parent["path"])
            idx = 1 + max(t["line"] for t in self.topics if key(t["path"]) == pk or key(t["path"]).startswith(pk + "/"))
            new_path = parent["path"] + "/" + parts[-1]
        else:
            idx, new_path = self.section_end("Assuntos"), parts[0]
        self.lines.insert(idx, "  " * (len(parts) - 1) + f"- [ ] {parts[-1]}")
        self.parse()
        return self.find(new_path), True

    def set_status(self, topic, status):
        self.lines[topic["line"]] = re.sub(r"\[[ /~xX]\]", f"[{SYMBOL[status]}]", self.lines[topic["line"]], count=1)
        self.parse()

    def add_log(self, day, path, correct, total, mistakes, notes):
        line = f"- {day} | {path} | " + (f"{correct}/{total}" if total else "—")
        if mistakes:
            line += " | erros: " + ", ".join(clean(m) for m in mistakes)
        if notes:
            line += " | nota: " + clean(notes)
        self.lines.insert(self.section_end("Registro"), line)
        self.parse()

    def save(self):
        self.file.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def all_disciplines():
    return [Discipline(f) for f in sorted(DIR.glob("*.md"))]


def get(name):
    for d in all_disciplines():
        if slug(d.title) == slug(name) or d.file.stem == slug(name):
            return d
    known = ", ".join(d.title for d in all_disciplines()) or "nenhuma"
    sys.exit(f"Erro: disciplina '{name}' não cadastrada (cadastradas: {known}). Use: study.py setup \"{name}\" ...")


def stats(d, t, today):
    logs = sorted((l for l in d.logs if key(l["path"]) == key(t["path"])), key=lambda l: l["day"])
    ex = [l for l in logs if l["total"]][-RECENT_SESSIONS:]
    correct, total = sum(l["correct"] for l in ex), sum(l["total"] for l in ex)
    acc = correct / total if total else None
    if acc is None:
        level = "sem exercícios"
    elif acc >= MASTERED_ACC and total >= MASTERED_MIN_Q:
        level = "dominado"
    elif acc < STRUGGLE_ACC and total >= STRUGGLE_MIN_Q:
        level = "dificuldade"
    else:
        level = "em consolidação"
    last = logs[-1]["day"] if logs else None
    mistakes = Counter(norm(m) for l in logs for m in l["mistakes"])
    return {
        "sessions": len(logs),
        "acc": acc,
        "recent_q": total,
        "level": level,
        "last": last,
        "days_since": (today - date.fromisoformat(last)).days if last else None,
        "recurring": [m for m, n in mistakes.most_common() if n >= 2],
    }


def load_exams():
    if not EXAMS.exists():
        return []
    exams = []
    for i, l in enumerate(EXAMS.read_text(encoding="utf-8").splitlines()):
        if m := EXAM_RE.match(l):
            exams.append({"day": m[1], "subject": m[2].strip(), "name": m[3].strip(), "line": i,
                          "topics": [x.strip() for x in (m[4] or "").split(",") if x.strip()]})
    return sorted(exams, key=lambda e: e["day"])


def upcoming(exams, d, today):
    return [e for e in exams if slug(e["subject"]) == slug(d.title) and e["day"] >= today.isoformat()]


def in_scope(e, t):
    k = key(t["path"])
    return not e["topics"] or any(k == key(x) or k.startswith(key(x) + "/") for x in e["topics"])


def exam_for(exams, d, t, today):
    """(dias, prova) da prova mais próxima, dentro de URGENT_DAYS, que cobre o assunto."""
    for e in upcoming(exams, d, today):
        days = (date.fromisoformat(e["day"]) - today).days
        if days <= URGENT_DAYS and in_scope(e, t):
            return days, e
    return None


def review_score(t, s, exam=None):
    """Maior = revisar antes. ponytail: heurística linear, troque por SM-2 se quiser repetição espaçada de verdade."""
    boost = (URGENT_DAYS - exam[0]) / 7 + 1 if exam and s["level"] != "dominado" else 0
    if not s["sessions"]:
        # Nunca estudado só entra com prova chegando, e só a folha (o pai é coberto pelos filhos).
        return round(boost + 1, 2) if boost and t["leaf"] else None
    score = min(s["days_since"] / 14, 1.5)
    score += 2 * (1 - s["acc"]) if s["acc"] is not None else 0.5
    score += 0.3 * len(s["recurring"])
    if t["status"] == "done" and s["level"] != "dominado":
        score += 0.5  # "concluído" sem domínio comprovado
    return round(score + boost, 2)


def fmt_acc(acc):
    return "—" if acc is None else f"{acc:.0%}"


def pct(n, total):
    return f"{n / total:.0%}" if total else "—"


def line(t, s):
    bits = [f"[{STATUS[t['status']]}]", s["level"]]
    if s["sessions"]:
        bits += [f"acerto recente {fmt_acc(s['acc'])} ({s['recent_q']}q)", f"{s['sessions']} sessões",
                 f"último estudo {s['last']} ({s['days_since']}d atrás)"]
    if s["recurring"]:
        bits.append("erros recorrentes: " + ", ".join(s["recurring"]))
    return "  " * t["path"].count("/") + f"  {t['path'].rsplit('/', 1)[-1]}: " + " | ".join(bits)


def chosen(subject):
    return [get(subject)] if subject else all_disciplines()


def cmd_map(a, today):
    ds = chosen(a.subject)
    if not ds:
        print("Nenhuma disciplina cadastrada ainda. Use: study.py setup \"Disciplina\" \"Assunto 1\" ...")
    for d in ds:
        print(f"\n## {d.title}  ({d.file})")
        for t in d.topics:
            print(line(t, stats(d, t, today)))
        if not d.topics:
            print("  (ementa vazia)")


def cmd_report(a, today):
    ds = chosen(a.subject)
    exams = load_exams()
    if not ds:
        print("Nenhuma disciplina cadastrada ainda.")
    for d in ds:
        ts = [(t, stats(d, t, today)) for t in d.topics]
        nxt = upcoming(exams, d, today)
        n = len(ts)
        c = Counter(t["status"] for t, _ in ts)
        levels = Counter(s["level"] for _, s in ts)
        q = sum(l["total"] for l in d.logs)
        print(f"\n## {d.title}")
        if nxt:
            print(f"  Próxima prova: {nxt[0]['name']} em {nxt[0]['day']} "
                  f"({(date.fromisoformat(nxt[0]['day']) - today).days} dias)")
        print(f"  Ementa: {n} assuntos | concluídos {c['done']} ({pct(c['done'], n)}) | estudando {c['doing']} | "
              f"não iniciados {c['todo']}")
        print(f"  Domínio: {levels['dominado']} de {n} dominados ({pct(levels['dominado'], n)}) | "
              f"acerto geral {pct(sum(l['correct'] for l in d.logs), q)} em {q} exercícios")
        for label, level in (("Dominados", "dominado"), ("Dificuldades", "dificuldade")):
            print(f"  {label}: {', '.join(t['path'] for t, s in ts if s['level'] == level) or 'nenhum'}")
        fake = [t["path"] for t, s in ts if t["status"] == "done" and s["level"] != "dominado"]
        if fake:
            print(f"  Concluídos sem domínio comprovado: {', '.join(fake)}")
        scored = ((review_score(t, s, exam_for(exams, d, t, today)), t["path"]) for t, s in ts)
        prio = sorted((x for x in scored if x[0] is not None), reverse=True)
        print(f"  Prioridades de revisão: {', '.join(p for _, p in prio[:3]) or 'nenhuma'}")
        todo = [t["path"] for t, _ in ts if t["status"] == "todo"]
        if todo:
            print(f"  Ainda não iniciados: {', '.join(todo)}")


def cmd_review(a, today):
    ranked, exams = [], load_exams()
    for d in chosen(a.subject):
        for t in d.topics:
            s, exam = stats(d, t, today), exam_for(exams, d, t, today)
            if (score := review_score(t, s, exam)) is not None:
                ranked.append((score, d, t, s, exam))
    ranked.sort(key=lambda x: x[0], reverse=True)
    if not ranked:
        print("Sem histórico suficiente para recomendar revisões.")
    for score, d, t, s, exam in ranked[: a.n]:
        why = [f"{exam[1]['name']} em {exam[0]}d"] if exam else []
        if s["sessions"]:
            why += [s["level"], f"acerto {fmt_acc(s['acc'])}", f"{s['days_since']}d sem estudar"]
        else:
            why.append("ainda não iniciado")
        if s["recurring"]:
            why.append("erros: " + ", ".join(s["recurring"]))
        print(f"{score:>5}  {d.title} › {t['path']}: " + ", ".join(why))


def cmd_exams(a, today):
    exams = load_exams()
    shown = False
    for d in chosen(a.subject):
        for e in upcoming(exams, d, today):
            shown = True
            days = (date.fromisoformat(e["day"]) - today).days
            scope = [(t, stats(d, t, today)) for t in d.topics if t["leaf"] and in_scope(e, t)]
            pending = [(t, s) for t, s in scope if s["level"] != "dominado"]
            untouched = [t["path"] for t, s in pending if not s["sessions"]]
            print(f"\n{e['name']} de {d.title} em {e['day']} ({days} dias)"
                  + (" | URGENTE" if days <= URGENT_DAYS else ""))
            print(f"  Escopo: {len(scope)} assuntos ({', '.join(e['topics']) or 'ementa inteira'}) | "
                  f"dominados {len(scope) - len(pending)} | pendentes {len(pending)} (não iniciados {len(untouched)})")
            if pending:
                print(f"  Ritmo: {len(pending) / max(days, 1):.1f} assuntos/dia para cobrir os pendentes até a prova")
                print("  Pendentes: " + ", ".join(f"{t['path']} ({s['level']})" for t, s in pending))
    if not shown:
        print("Nenhuma prova futura cadastrada." + (f" Datas ficam em {EXAMS}." if not EXAMS.exists() else ""))


def add_exam(subject, day, name, topics):
    d = get(subject)
    date.fromisoformat(day)  # valida formato
    paths = []
    for x in topics:
        t = d.find(x) or sys.exit(f"Erro: assunto '{x}' não está na ementa de {d.title}.")
        paths.append(t["path"])
    EXAMS.parent.mkdir(parents=True, exist_ok=True)
    if not EXAMS.exists():
        EXAMS.write_text("# Provas\n\n", encoding="utf-8")
    lines = EXAMS.read_text(encoding="utf-8").splitlines()
    same = next((e for e in load_exams() if slug(e["subject"]) == slug(d.title) and norm(e["name"]) == norm(name)), None)
    name = same["name"] if same else clean(name)
    line = f"- {day} | {d.title} | {name}" + (f" | assuntos: {', '.join(paths)}" if paths else "")
    if same:
        lines[same["line"]] = line  # mesma prova: atualiza data/assuntos
    else:
        lines.append(line)
    EXAMS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d, bool(same)


def cmd_compare(a, today):
    d = get(a.subject)

    def window(start, end):
        ls = [l for l in d.logs if start.isoformat() < l["day"] <= end.isoformat()]
        q = sum(l["total"] for l in ls)
        return {"n": len(ls), "topics": len({key(l["path"]) for l in ls}), "q": q,
                "acc": sum(l["correct"] for l in ls) / q if q else None}

    cur = window(today - timedelta(days=a.days), today)
    prev = window(today - timedelta(days=2 * a.days), today - timedelta(days=a.days))
    for label, w in ((f"Últimos {a.days} dias", cur), (f"{a.days} dias anteriores", prev)):
        print(f"{label}: {w['n']} sessões em {w['topics']} assuntos, acerto {fmt_acc(w['acc'])} ({w['q']}q)")
    if cur["acc"] is not None and prev["acc"] is not None:
        diff = (cur["acc"] - prev["acc"]) * 100
        print(f"Variação de acerto: {diff:+.0f} p.p. ({'melhora' if diff > 2 else 'queda' if diff < -2 else 'estável'})")


def cmd_history(a, today):
    d = get(a.subject)
    k = key(a.path) if a.path else None
    logs = [l for l in d.logs if not k or key(l["path"]) == k or key(l["path"]).startswith(k + "/")]
    for l in sorted(logs, key=lambda l: l["day"], reverse=True)[: a.n]:
        extra = f", {l['correct']}/{l['total']}" if l["total"] else ""
        extra += f" | erros: {', '.join(l['mistakes'])}" if l["mistakes"] else ""
        extra += f" | nota: {l['notes']}" if l["notes"] else ""
        print(f"{l['day']}  {l['path']}{extra}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Study Tracker")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup"); s.add_argument("subject"); s.add_argument("topics", nargs="*")
    s = sub.add_parser("add"); s.add_argument("subject"); s.add_argument("path")
    s = sub.add_parser("status"); s.add_argument("subject"); s.add_argument("path"); s.add_argument("status", choices=STATUS)
    s = sub.add_parser("log")
    s.add_argument("subject"); s.add_argument("path")
    s.add_argument("--correct", type=int, default=0); s.add_argument("--total", type=int, default=0)
    s.add_argument("--mistakes", default=""); s.add_argument("--notes", default=""); s.add_argument("--date", default=None)
    for name in ("map", "report"):
        s = sub.add_parser(name); s.add_argument("subject", nargs="?")
    s = sub.add_parser("review"); s.add_argument("--subject"); s.add_argument("--n", type=int, default=5)
    s = sub.add_parser("compare"); s.add_argument("subject"); s.add_argument("--days", type=int, default=14)
    s = sub.add_parser("history"); s.add_argument("subject"); s.add_argument("path", nargs="?"); s.add_argument("--n", type=int, default=10)
    s = sub.add_parser("exam"); s.add_argument("subject"); s.add_argument("date")
    s.add_argument("--name", default="Prova"); s.add_argument("--topics", default="")
    s = sub.add_parser("exams"); s.add_argument("--subject")
    a = p.parse_args(argv)
    today = date.fromisoformat(os.environ.get("STUDY_TODAY", date.today().isoformat()))

    if a.cmd == "setup":
        if not slug(a.subject):
            sys.exit("Erro: nome de disciplina inválido.")
        DIR.mkdir(parents=True, exist_ok=True)
        existing = next((d.file for d in all_disciplines() if slug(d.title) == slug(a.subject)), None)
        # Nome do arquivo = nome da disciplina, sem os caracteres que o Obsidian não aceita em links.
        f = existing or DIR / (re.sub(r'[\\/:*?"<>|#^\[\]]', "", clean(a.subject)).strip() + ".md")
        if not f.exists():
            f.write_text(f"# {clean(a.subject)}\n\n## Assuntos\n\n## Registro\n", encoding="utf-8")
        d = Discipline(f)
        added = [t["path"] for t, new in (d.add_topic(clean(x)) for x in a.topics) if new]
        d.save()
        print(f"{d.title}: {len(d.topics)} assuntos na ementa ({len(added)} novos) em {f}")
    elif a.cmd == "add":
        d = get(a.subject)
        t, new = d.add_topic(clean(a.path))
        d.save()
        print(f"{'Adicionado' if new else 'Já existia'}: {d.title} › {t['path']}")
    elif a.cmd == "status":
        d = get(a.subject)
        t = d.find(a.path) or sys.exit(f"Erro: assunto '{a.path}' não está na ementa de {d.title}.")
        d.set_status(t, a.status)
        d.save()
        print(f"{d.title} › {t['path']}: {STATUS[a.status]}")
    elif a.cmd == "log":
        if a.correct > a.total:
            sys.exit("Erro: --correct maior que --total.")
        day = a.date or today.isoformat()
        date.fromisoformat(day)  # valida formato
        d = get(a.subject)
        t, new = d.add_topic(clean(a.path))
        if t["status"] == "todo":
            d.set_status(t, "doing")
            t = d.find(t["path"])
        d.add_log(day, t["path"], a.correct, a.total, [m for m in a.mistakes.split(",") if m.strip()], a.notes)
        d.save()
        if new:
            print(f"Atenção: '{t['path']}' não estava na ementa e foi adicionado.")
        print("Sessão registrada.\n" + line(d.find(t["path"]), stats(d, d.find(t["path"]), today)))
    elif a.cmd == "exam":
        d, updated = add_exam(a.subject, a.date, a.name, [x for x in a.topics.split(",") if x.strip()])
        print(f"{'Atualizada' if updated else 'Cadastrada'}: {a.name} de {d.title} em {a.date} ({EXAMS})")
    else:
        {"map": cmd_map, "report": cmd_report, "review": cmd_review, "compare": cmd_compare,
         "history": cmd_history, "exams": cmd_exams}[a.cmd](a, today)


if __name__ == "__main__":
    main()
