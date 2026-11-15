"""python3 study-tracker/scripts/test_study.py"""
import contextlib
import io
import os
import sys

os.environ["STUDY_TODAY"] = "2026-11-14"
sys.path.insert(0, os.path.dirname(__file__))
import study  # noqa: E402


def run(db, *argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        study.main(list(argv), db=db)
    return out.getvalue()


db = study.connect(":memory:")
run(db, "add", "Cálculo I", "Limites")
run(db, "log", "Cálculo I", "Integrais", "--min", "120", "--correct", "4", "--total", "10",
    "--mistakes", "sinal,constante", "--date", "2026-10-20")
run(db, "log", "cálculo i", "integrais", "--min", "60", "--correct", "3", "--total", "10",
    "--mistakes", "sinal", "--date", "2026-10-25")
run(db, "log", "Cálculo I", "Derivadas", "--min", "90", "--correct", "9", "--total", "10", "--date", "2026-11-10")
run(db, "status", "Cálculo I", "Derivadas", "done")

m = run(db, "map")
assert m.count("Integrais") == 1, m  # case-insensitive, sem duplicar
assert "Integrais: [estudando] | dificuldade" in m, m
assert "erros recorrentes: sinal" in m, m
assert "Derivadas: [concluído] | dominado" in m, m
assert "Limites: [não iniciado]" in m, m

r = run(db, "report", "Cálculo I")
assert "Dominados: Derivadas" in r and "Dificuldades: Integrais" in r, r
assert "Prioridades de revisão: Integrais" in r, r
assert "acerto geral: 53% (30 exercícios)" in r, r

assert run(db, "review").splitlines()[0].endswith("erros: sinal"), run(db, "review")

c = run(db, "compare", "Cálculo I", "--days", "14")
assert "Últimos 14 dias: 1 sessões" in c and "Variação de acerto: +55 p.p. (melhora)" in c, c

assert "2026-10-25  Integrais: 1h00, 3/10" in run(db, "history", "Cálculo I", "Integrais")
print("ok")
