"""Normalização de texto, stopwords e taxonomia de temas da Voz do Cliente."""
from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_REPEAT = re.compile(r"([!?.])\1{2,}")


def clean_text(text: object) -> str:
    """Limpeza conservadora: preserva o texto do cliente (é a evidência exibida)."""
    if text is None or (isinstance(text, float) and text != text):
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = _REPEAT.sub(r"\1\1\1", s)  # "!!!!!!!" -> "!!!"
    s = _WS.sub(" ", s).strip()
    return s


def fold(text: str) -> str:
    """Forma canônica para busca lexical/regex: minúsculas e sem acentos."""
    s = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


STOPWORDS = set(
    fold(w)
    for w in """
a o as os um uma uns umas de do da dos das no na nos nas em por para pra pro com sem sobre
e ou mas que se ja nao sim muito mais menos como quando onde qual quais quem porque pois
eu voce ele ela nos eles elas meu minha seu sua seus suas isso isto esse essa este esta aquilo
ser estar ter foi era sao esta estao tem tinha fui ao aos a as pelo pela pelos pelas entre ate
clientes cliente avaliacoes avaliacao relatam relatados relatadas relatado relatos mencionam
principais principal existem existe padroes padrao aparecem aparece frequencia maior
sao quais o que os as compra compras experiencia experiencias aspectos sustentam conclusao
""".split()
)


def content_terms(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]{3,}", fold(text)) if t not in STOPWORDS]


# Taxonomia de temas (regex sobre texto `fold`). Usada para:
#  1) metadado de cada documento (theme flags),
#  2) estatísticas agregadas no contexto (quantificar padrões no corpus inteiro),
#  3) expansão de consulta no índice lexical.
THEMES: dict[str, dict] = {
    "entrega_atraso": {
        "label": "Atraso / demora na entrega",
        "pattern": r"atras|demor|fora do prazo|passou do prazo|prazo (de entrega )?(vencido|expirou|estourado)|ainda nao (chegou|recebi)|nao chegou no prazo",
        "expand": "atraso atrasou demora demorou prazo entrega",
    },
    "nao_recebido": {
        "label": "Produto não recebido / entrega incompleta",
        "pattern": r"nao (recebi|chegou|foi entregue)|nunca chegou|ainda nao (recebi|chegou)|faltou|veio faltando|faltando|incomplet|so (recebi|chegou|veio) (um|uma|1)",
        "expand": "nao recebi nao chegou faltando incompleto",
    },
    "entrega_rapida": {
        "label": "Entrega rápida / antes do prazo",
        "pattern": r"antes do prazo|dentro do prazo|no prazo|rapid|chegou antes|super rapido|entrega (foi )?(rapida|otima|excelente)|bem antes",
        "expand": "rapido rapida antes do prazo entrega",
    },
    "qualidade_produto": {
        "label": "Qualidade / defeito do produto",
        "pattern": r"qualidade|defeit|quebrad|danificad|estragad|amassad|nao funciona|parou de funcionar|falsificad|pirata|material (ruim|fraco)|fragil|riscad",
        "expand": "qualidade defeito quebrado danificado nao funciona",
    },
    "produto_divergente": {
        "label": "Produto diferente do anunciado",
        "pattern": r"diferente|errad|nao (e|era) o (mesmo|que)|outro produto|cor (diferente|errada)|tamanho (errado|diferente)|nao corresponde|anuncio",
        "expand": "diferente errado anuncio outro produto",
    },
    "atendimento": {
        "label": "Atendimento / comunicação",
        "pattern": r"atendiment|suporte (ao cliente|tecnico)|\bsac\b|entr(ei|ar|amos) em contato|sem contato|respond|resposta|retorno|ninguem|descaso|e-?mail",
        "expand": "atendimento contato resposta retorno sac",
    },
    "troca_reembolso": {
        "label": "Troca, devolução, cancelamento ou reembolso",
        "pattern": r"troca|devolu|devolv|reembols|estorn|cancel|dinheiro de volta",
        "expand": "troca devolucao reembolso estorno cancelamento",
    },
    "embalagem": {
        "label": "Embalagem",
        "pattern": r"embala|caixa|pacote|lacrad",
        "expand": "embalagem caixa embalado",
    },
    "preco_custo": {
        "label": "Preço / frete / custo-benefício",
        "pattern": r"preco|barat|caro|custo|frete|valor",
        "expand": "preco frete custo beneficio valor",
    },
    "satisfacao": {
        "label": "Satisfação / recomendação",
        "pattern": r"(?<!nao )recomend|(?<!nao )(?<!nada )otim|excelent|(?<!nao )perfeit|(?<!nao )(?<!in)satisfeit|(?<!nao )gostei|(?<!nao )adorei|amei|(?<!nao e )muito bom|\btop\b|parabens|nota 10",
        "expand": "recomendo otimo excelente satisfeito gostei",
    },
}
_THEME_RX = {k: re.compile(v["pattern"]) for k, v in THEMES.items()}


def detect_themes(folded_text: str) -> list[str]:
    return [k for k, rx in _THEME_RX.items() if rx.search(folded_text)]
