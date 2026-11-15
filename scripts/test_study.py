"""python3 scripts/test_study.py"""
import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

os.environ["STUDY_TODAY"] = "2026-11-14"
sys.path.insert(0, os.path.dirname(__file__))
import study  # noqa: E402

study.ROOT = Path(tempfile.mkdtemp())
study.DIR, study.EXAMS = study.ROOT / "Disciplinas", study.ROOT / "Datas" / "Provas.md"


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        study.main(list(argv))
    return out.getvalue()


def fails(*argv):
    try:
        run(*argv)
    except SystemExit as e:
        return str(e)
    raise AssertionError(f"deveria falhar: {argv}")


# Setup define a ementa; log sem setup é recusado.
assert "não cadastrada" in fails("log", "Física I", "Cinemática", "--correct", "1", "--total", "2")
run("setup", "Cálculo I", "Limites", "Derivadas/Regra da cadeia", "Integrais")
assert "0 novos" in run("setup", "calculo i", "limites")  # sem acento/maiúscula não duplica

run("log", "Cálculo I", "integrais", "--correct", "4", "--total", "10", "--mistakes", "sinal,constante", "--date", "2026-10-20")
run("log", "CALCULO I", "Integráis", "--correct", "3", "--total", "10", "--mistakes", "Sinal", "--date", "2026-10-25")
run("log", "Cálculo I", "Derivadas/Regra da cadeia", "--correct", "9", "--total", "10", "--date", "2026-11-10")
run("status", "Cálculo I", "derivadas/regra da cadeia", "done")
assert "não estava na ementa" in run("log", "Cálculo I", "Séries", "--date", "2026-11-12")

md = (study.DIR / "Cálculo I.md").read_text()
assert "- [/] Integrais\n" in md and "  - [x] Regra da cadeia\n" in md and "- [/] Séries\n" in md, md
assert "- 2026-10-20 | Integrais | 4/10 | erros: sinal, constante\n" in md, md
assert "- 2026-11-12 | Séries | —\n" in md, md
assert md.index("- [/] Séries") < md.index("## Registro"), md

m = run("map")
assert "Integrais: [estudando] | dificuldade" in m and "erros recorrentes: sinal" in m, m
assert "Regra da cadeia: [concluído] | dominado" in m, m
assert "Limites: [não iniciado] | sem exercícios" in m, m

r = run("report", "Cálculo I")
assert "Ementa: 5 assuntos | concluídos 1 (20%) | estudando 2 | não iniciados 2" in r, r
assert "Dominados: Derivadas/Regra da cadeia" in r and "Dificuldades: Integrais" in r, r
assert "Prioridades de revisão: Integrais" in r, r

assert run("review").splitlines()[0].endswith("erros: sinal"), run("review")
c = run("compare", "Cálculo I", "--days", "14")
assert "Últimos 14 dias: 2 sessões em 2 assuntos" in c and "+55 p.p. (melhora)" in c, c
assert "2026-10-25  Integrais, 3/10 | erros: Sinal" in run("history", "Cálculo I", "Integrais")
assert "maior que" in fails("log", "Cálculo I", "Limites", "--correct", "5", "--total", "2")

# Arquivo editado à mão: seções extras e anotações são preservadas.
(study.DIR / "Física I.md").write_text(
    "# Física I\n\nProf. Ana, P1 em 02/12\n\n## Assuntos\n- [x] Cinemática\n  - [~] MRUV\n\n## Provas\n- P1: 02/12\n")
run("add", "Física I", "Cinemática/Lançamento")
run("log", "Física I", "MRUV", "--correct", "8", "--total", "10")
f = (study.DIR / "Física I.md").read_text()
assert "Prof. Ana, P1 em 02/12" in f and "## Provas\n- P1: 02/12" in f, f
assert "  - [~] MRUV\n  - [ ] Lançamento\n" in f, f  # "MRUV" achou o subassunto; [~] legado = estudando
assert f.rstrip().endswith("## Registro\n- 2026-11-14 | Cinemática/MRUV | 8/10"), f  # seção criada
run("add", "Física I", "Dinâmica/MRUV")
assert "ambíguo" in fails("log", "Física I", "MRUV")

# Provas: Datas/Provas.md, escopo por assunto, prioridade na revisão.
assert "Nenhuma prova futura" in run("exams")
assert "não está na ementa" in fails("exam", "Cálculo I", "2026-11-24", "--topics", "Séries de Fourier")
run("exam", "Cálculo I", "2026-11-24", "--name", "P1", "--topics", "limites,derivadas")
p = study.EXAMS.read_text()
assert p == "# Provas\n\n- 2026-11-24 | Cálculo I | P1 | assuntos: Limites, Derivadas\n", p

e = run("exams")
assert "P1 de Cálculo I em 2026-11-24 (10 dias) | URGENTE" in e, e
# Folhas no escopo: Limites (não iniciado) e Regra da cadeia (dominado); "Derivadas" é pai.
assert "Escopo: 2 assuntos (Limites, Derivadas) | dominados 1 | pendentes 1 (não iniciados 1)" in e, e
assert "Pendentes: Limites (sem exercícios)" in e, e

rv = run("review").splitlines()
assert rv[0].endswith("Cálculo I › Limites: P1 em 10d, ainda não iniciado"), rv  # nunca estudado, mas prova chegando
assert any(l.startswith(" 0.49  Cálculo I › Derivadas/Regra da cadeia") for l in rv), rv  # dominado: sem bônus
assert not any("› Derivadas:" in l for l in rv), rv  # pai não entra

# Mesma prova de novo = atualiza a linha (nome original mantido); escopo vazio = ementa inteira.
assert "Atualizada" in run("exam", "calculo i", "2026-11-26", "--name", "p1")
assert study.EXAMS.read_text().count("P1") == 1 and "- 2026-11-26 | Cálculo I | P1\n" in study.EXAMS.read_text()
assert "Próxima prova: P1 em 2026-11-26 (12 dias)" in run("report", "Cálculo I")
assert "Escopo: 4 assuntos (ementa inteira)" in run("exams", "--subject", "Cálculo I")

# Prova passada some de exams; linhas escritas à mão no Provas.md são preservadas.
study.EXAMS.write_text(study.EXAMS.read_text() + "\nLembrar: P1 com consulta\n")
run("exam", "Física I", "2026-11-01", "--name", "P0")
assert "Nenhuma prova futura" in run("exams", "--subject", "Física I")
assert "Lembrar: P1 com consulta" in study.EXAMS.read_text()

print("ok")
