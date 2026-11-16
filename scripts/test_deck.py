"""python3 scripts/test_deck.py"""
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(__file__))
import deck  # noqa: E402
import study  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

study.SIGLAS = Path(tempfile.mkdtemp()) / "Siglas.md"  # isola das siglas reais do vault

today = date(2026, 11, 15)
assert deck.parse_day("09/11 à 08/12", today) == date(2026, 12, 8)  # intervalo sem ano: fim
assert deck.parse_day("04/01", today) == date(2027, 1, 4)  # sem ano e longe no passado: ano que vem
assert deck.parse_day("01/12/2026", today) == date(2026, 12, 1)
for name, acr in [("Linguagem de Programação II", "LP2"), ("CALCULO NUMERICO", "CN"), ("Cálculo 1", "C1"),
                  ("Sistemas Baseados em Conhecimento", "SBC"), ("Introdução ao Processamento Digital de Imagens", "IPDI")]:
    assert deck.acronym(name) == acr, (name, deck.acronym(name))

data = {
    "unread": 3,
    "news": [(datetime(2026, 11, 11, 9), "Cálculo Numérico", "Aula   remarcada\npara sexta"),
             (datetime(2026, 11, 2, 9), "Teste de Software", "Notas da Unidade 1")],
    "dates": [("2026-11-24", "Sistemas Baseados em Conhecimento", "Segunda Avaliação", "prova"),
              ("24/11/2026", "Sistemas Baseados em Conhecimento", "Segunda Avaliação", "avaliacao"),  # duplicata
              ("10/12/2026", "Cálculo Numérico", "Reposição", "avaliacao"),  # condicional: fora
              ("09/11 à 20/11", "Teste de Software", "APS", "atividade"),
              ("01/01/2027", "Cálculo Numérico", "Muito longe", "avaliacao")],  # fora da janela
    "absences": [("Teste de Software", 2, 15), ("Cálculo Numérico", 16, 15)],
    "errors": [],
}
out = deck.render(data, today, datetime(2026, 11, 15, 19, 0))
assert not any("  " in l for l in out), out  # texto corrido: nada alinhado por espaços (fonte proporcional)
assert not any(c in l for l in out for c in "║═╔╗╚╝╠╣╦╩╬█░"), out  # sem bordas nem blocos de terminal: feios no Telegram
text = "\n".join(out)
assert out[0] == "FLIGHT DECK · dom 15/11 19:00" and "NOTÍCIAS · 3 não lidas" in text, text
assert "11/11 · CN · Aula remarcada para sexta" in text, text  # espaços do SIGAA colapsados
assert text.count("Segunda Avaliação") == 1 and "Reposição" not in text and "Muito longe" not in text, text
assert "20/11 sex · em 5d · TS · APS\n" in text, text  # atividade sem "*"
assert "24/11 ter · em 9d · SBC · Segunda Avaliação *" in text, text
assert "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 107% · CN 16/15 !" in text, text  # estourou o limite
assert "🟦⬜⬜⬜⬜⬜⬜⬜⬜⬜ 13% · TS 2/15" in text, text
assert "Menor margem: CN, 0 faltas" in text, text
assert "Total: 18/30 faltas" in text and "TOT" not in text, text  # rótulos nunca abreviados
assert "⬜ margem" not in text and not any(c in text for c in "⬛🟫🟥🟨🟩"), text  # binário, sem legenda nem preto
study.SIGLAS.write_text("# Siglas\n\n- Cálculo Numérico: NUM\n")
s2 = "\n".join(deck.render(data, today, datetime(2026, 11, 15)))
assert "11/11 · NUM · Aula" in s2 and "· NUM 16/15 !" in s2 and "Menor margem: NUM" in s2 and "· TS " in s2, s2
print("ok")
