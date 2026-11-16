#!/usr/bin/env python3
"""Flight deck do semestre: notícias, datas importantes e faltas em texto corrido, sem depender de fonte monoespaçada.

Uso:
  deck.py            notícias e prazos da base local do SIGAA + faltas ao vivo
  deck.py --sync     roda `sigaa sync` antes (~40s) para trazer notícias e prazos novos

Fontes: CLI `sigaa` (sigaa-tools) e Datas/Provas.md do Study Tracker. Só stdlib.
"""
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import study

W = 44                       # títulos cortados aqui; linhas curtas não quebram no celular
NEWS_ROWS, DATE_ROWS = 4, 8
BAR = 10                     # quadrados por barra de faltas
# Binário, em quadrados do mesmo tamanho: emoji renderiza bem em fonte proporcional (Telegram).
USED, FREE = "🟦", "⬜"
SKIP_DATES = re.compile(r"reposi|exame final", re.I)  # condicionais: só poluem o painel
WEEKDAY = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def sigaa(*args, timeout=90):
    r = subprocess.run(["sigaa", *args, "--json"], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError((r.stderr.strip().splitlines() or ["erro desconhecido"])[-1])
    return json.loads(r.stdout)


def cut(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def fit(s, n):
    """Campo de texto: colapsa espaços e quebras vindos do SIGAA, depois corta."""
    return cut(" ".join(str(s).split()), n)


def parse_day(text, today):
    """Última data do texto ("09/11 à 08/12" → 08/12); sem ano, a mais próxima de hoje."""
    found = re.findall(r"(\d{2})/(\d{2})(?:/(\d{4}))?", text or "")
    if not found:
        return None
    d, m, y = found[-1]
    day = date(int(y or today.year), int(m), int(d))
    if not y and day < today - timedelta(days=180):
        day = day.replace(year=day.year + 1)
    return day


SMALL = {"a", "o", "e", "de", "da", "do", "das", "dos", "ao", "aos", "em", "na", "no", "para"}
ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}


def acronym(name):
    """Iniciais das palavras relevantes, romano vira número: "Linguagem de Programação II" → "LP2"."""
    words = [w for w in study.norm(name).split() if w not in SMALL]
    return "".join(ROMAN.get(w) or (w if w.isdigit() else w[0].upper()) for w in words) or "?"


def display_names(classes):
    """Código → nome: o título da nota do tracker quando bate, senão o nome do SIGAA capitalizado."""
    notes = {study.slug(d.title): d.title for d in study.all_disciplines()} if study.DIR.exists() else {}
    small = {"a", "o", "e", "de", "da", "do", "das", "dos", "ao", "em"}
    out = {}
    for c in classes:
        words = c["name"].lower().split()
        pretty = " ".join(w if w in small and i else (w.upper() if w in {"ii", "iii", "iv"} else w.capitalize())
                          for i, w in enumerate(words))
        out[c["code"]] = notes.get(study.slug(c["name"]), pretty)
    return out


def collect(sync=False):
    data = {"news": [], "unread": 0, "dates": [], "absences": [], "errors": []}
    try:
        if sync:
            subprocess.run(["sigaa", "sync"], capture_output=True, timeout=300)
        classes = sigaa("classes")
    except Exception as e:  # sem sigaa ou sem login: o painel mostra só o que vem do tracker
        data["errors"].append(f"SIGAA indisponível: {e}")
        classes = []
    names = display_names(classes)

    with ThreadPoolExecutor(max_workers=6) as pool:
        att = dict(zip(names, pool.map(lambda c: _try(sigaa, "attendance", "--class", c), names)))
    turma = {}  # id_turma → código; só a frequência devolve o id interno da turma
    for code, a in att.items():
        if isinstance(a, dict):
            turma[a["class_id"]] = code
            data["absences"].append((names[code], a["total_absences"], a["max_absences"]))
        else:
            data["errors"].append(f"faltas de {names[code]}: {a}")

    if classes:
        news = _try(sigaa, "news") or []
        unread = _try(sigaa, "news", "--unread")
        data["unread"] = len(unread) if isinstance(unread, list) else 0
        for n in news if isinstance(news, list) else []:
            when = datetime.strptime(n["date"], "%d/%m/%Y %H:%M") if n.get("date") else datetime.min
            data["news"].append((when, names.get(turma.get(n["id_turma"]), "?"), n["title"]))
        deadlines = _try(sigaa, "deadlines")
        for d in deadlines if isinstance(deadlines, list) else []:
            data["dates"].append((d["date"], names.get(turma.get(d["id_turma"]), "?"), d["title"], d["kind"]))
    for e in study.load_exams():
        data["dates"].append((e["day"], e["subject"], e["name"], "prova"))
    return data


def _try(fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        return str(e)


def render(data, today, now):
    # Texto corrido (mensagem do Telegram, fonte proporcional): nada depende de espaços para alinhar.
    acr = acronym
    out = [f"FLIGHT DECK · {WEEKDAY[now.weekday()]} {now:%d/%m %H:%M}", ""]

    out.append(f"NOTÍCIAS · {data['unread']} não lidas")
    news = sorted(data["news"], reverse=True)[:NEWS_ROWS]
    out += [f"{w:%d/%m} · {acr(c)} · {fit(t, W)}" for w, c, t in news] or ["nenhuma notícia"]

    out += ["", f"DATAS · próximos {study.URGENT_DAYS} dias"]
    rows = {}
    for raw, subj, title, kind in data["dates"]:
        day = date.fromisoformat(raw) if re.match(r"\d{4}-", raw) else parse_day(raw, today)
        if day and today <= day <= today + timedelta(days=study.URGENT_DAYS) and not SKIP_DATES.search(title):
            rows.setdefault((day, study.slug(subj), study.norm(title)), (day, subj, title, kind))
    upcoming = sorted(rows.values(), key=lambda r: r[0])
    for day, subj, title, kind in upcoming[:DATE_ROWS]:
        left = "hoje" if day == today else f"em {(day - today).days}d"
        tag = " *" if kind in ("avaliacao", "prova") else ""
        out.append(f"{day:%d/%m} {WEEKDAY[day.weekday()]} · {left} · {acr(subj)} · {fit(title, W)}{tag}")
    if len(upcoming) > DATE_ROWS:
        out.append(f"+ {len(upcoming) - DATE_ROWS} datas depois dessas")
    if not upcoming:
        out.append("nada nos próximos dias")

    out += ["", "FALTAS"]
    tight = None
    for name, f, mx in sorted(data["absences"], key=lambda a: -a[1] / max(a[2], 1)):
        n = min(BAR, round(f / mx * BAR)) if mx else 0
        pct = f"{f / mx:>4.0%}" if mx else "   —"
        out.append(f"{USED * n}{FREE * (BAR - n)} {pct.strip()} · {acr(name)} {f}/{mx}" + (" !" if f >= mx else ""))
        if mx and (tight is None or mx - f < tight[1]):
            tight = (name, mx - f)
    if not data["absences"]:
        out.append("sem dados")
    tf, tm = sum(a[1] for a in data["absences"]), sum(a[2] for a in data["absences"])
    out.append(f"Total: {tf}/{tm} faltas")

    out.append("")
    if tight:
        out.append(f"Menor margem: {acr(tight[0])}, {max(tight[1], 0)} faltas")
    out.append("* = prova")
    out += data["errors"]
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description="Flight deck do semestre")
    p.add_argument("--sync", action="store_true", help="roda sigaa sync antes (~40s)")
    a = p.parse_args(argv)
    now = datetime.now()
    print("\n".join(render(collect(a.sync), now.date(), now)))


if __name__ == "__main__":
    sys.exit(main())
