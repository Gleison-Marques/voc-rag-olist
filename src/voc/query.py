"""Processamento da pergunta: intenção, filtros de metadados e expansão de consulta."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .text import THEMES, content_terms, fold

NEG_RX = re.compile(
    r"problem|reclam|insatisf|negativ|ruim|pessim|defeit|critic|falh|queix|frustr|nota(s)? baixa|decepc"
)
POS_RX = re.compile(r"elogi|positiv|(?<!in)satisf|gost|valoriz|nota(s)? alta|bem avaliad|ponto(s)? forte|encant")

# termos da pergunta -> termos extras para o índice lexical (o denso dispensa)
EXPANSIONS = {
    r"entreg": "entrega prazo chegou atraso demora correios transportadora recebi",
    r"prazo": "prazo atraso demorou antes do prazo",
    r"qualidad": THEMES["qualidade_produto"]["expand"],
    r"atendiment|suporte|comunica": THEMES["atendimento"]["expand"],
    r"troca|devolu|reembols|cancel": THEMES["troca_reembolso"]["expand"],
    r"embala": THEMES["embalagem"]["expand"],
    r"preco|frete|custo": THEMES["preco_custo"]["expand"],
    r"elogi|positiv|gost|valoriz": THEMES["satisfacao"]["expand"],
    r"diferente|anunci|errad": THEMES["produto_divergente"]["expand"],
}

# termos de assunto do domínio (e-commerce). "cliente"/"avaliação" ficam de fora de propósito:
# aparecem em quase toda pergunta e não indicam que o ASSUNTO pertence à base.
DOMAIN_RX = re.compile(
    r"compr|pedid|produt|entreg|prazo|frete|loja|vendedor|atendiment|qualidad|embala|devolu|"
    r"troca|reembols|olist|e-?commerce|categori|recebi|chegou|atras|defeit|preco|correio|transport"
)

# termos de intenção/meta da pergunta: não precisam aparecer no texto das evidências
META_PREFIXES = (
    "problem", "reclam", "elogi", "insatisf", "satisf", "positiv", "negativ", "padro", "padra",
    "recorr", "tema", "motiv", "frequen", "nota", "baix", "alt", "avali", "relat", "relaciona",
    "mencion", "destac", "valoriz", "gost", "aspect", "ponto", "opini", "diz", "dizem", "fal",
    "comum", "comun", "identific", "sustent", "conclus", "evidenc", "exist", "aparec", "maior",
    "melhor", "pior", "tipo", "geral", "mais", "consumid", "compra", "experien", "investig",
    "acha", "acham", "pens", "percep", "sent", "costum", "principa",
    # substantivos genéricos do domínio: aparecem em tudo e não definem o assunto
    "loja", "produt", "pedid", "site", "empresa", "client", "marketplace",
)

# assunto da pergunta -> temas (usados no rerank)
TOPIC_THEMES = {
    r"entreg": ["entrega_atraso", "nao_recebido", "entrega_rapida"],
    r"prazo|atras|demor": ["entrega_atraso", "entrega_rapida"],
    r"receb|cheg": ["nao_recebido", "entrega_atraso", "entrega_rapida"],
    r"qualidad|defeit|quebr": ["qualidade_produto"],
    r"atendiment|suporte|comunica": ["atendimento"],
    r"troca|devolu|reembols|cancel": ["troca_reembolso"],
    r"embala": ["embalagem"],
    r"preco|frete|custo": ["preco_custo"],
    r"diferente|anunci|errad": ["produto_divergente"],
    r"elogi|positiv": ["satisfacao", "entrega_rapida"],
}

CATEGORY_ALIASES = {
    "celular": ["telefonia"], "celulares": ["telefonia"], "smartphone": ["telefonia"],
    "computador": ["informatica_acessorios", "pcs"], "notebook": ["informatica_acessorios", "pcs"],
    "perfume": ["perfumaria"], "perfumes": ["perfumaria"], "relogio": ["relogios_presentes"],
    "relogios": ["relogios_presentes"], "brinquedo": ["brinquedos"], "bebe": ["bebes"],
    "moveis": ["moveis_decoracao", "moveis_escritorio", "moveis_sala", "moveis_quarto",
               "moveis_cozinha_area_de_servico_jantar_e_pizzaria", "moveis_colchao_e_estofado"],
    "eletronicos": ["eletronicos"], "eletrodomesticos": ["eletrodomesticos", "eletrodomesticos_2"],
    "esporte": ["esporte_lazer"], "esportes": ["esporte_lazer"], "beleza": ["beleza_saude"],
    "saude": ["beleza_saude"], "cama": ["cama_mesa_banho"], "banho": ["cama_mesa_banho"],
    "automotivo": ["automotivo"], "carro": ["automotivo"], "pet": ["pet_shop"],
    "livros": ["livros_interesse_geral", "livros_tecnicos", "livros_importados"],
    "ferramentas": ["ferramentas_jardim", "construcao_ferramentas_construcao"],
    "jardim": ["ferramentas_jardim"], "utilidades": ["utilidades_domesticas"],
    "papelaria": ["papelaria"], "games": ["consoles_games"], "jogos": ["consoles_games"],
    "fashion": ["fashion_bolsas_e_acessorios"], "bolsas": ["fashion_bolsas_e_acessorios"],
}


@dataclass
class QueryPlan:
    question: str
    folded: str
    intent: str = "neutra"  # negativa | positiva | neutra
    score_range: tuple[int, int] | None = None
    categories: list[str] = field(default_factory=list)
    years: list[int] = field(default_factory=list)
    delivered_late: bool | None = None
    lexical_query: str = ""
    focus_themes: list[str] = field(default_factory=list)
    target_themes: list[str] = field(default_factory=list)
    key_terms: list[str] = field(default_factory=list)
    in_domain: bool = True
    notes: list[str] = field(default_factory=list)

    def filters_description(self) -> str:
        parts = []
        if self.score_range:
            a, b = self.score_range
            parts.append(f"nota {a}" if a == b else f"nota {a}–{b}")
        if self.categories:
            parts.append("categoria ∈ {" + ", ".join(self.categories) + "}")
        if self.years:
            parts.append("ano ∈ {" + ", ".join(map(str, self.years)) + "}")
        if self.delivered_late is not None:
            parts.append("entregue com atraso" if self.delivered_late else "entregue no prazo")
        return "; ".join(parts) or "nenhum"


def plan_query(question: str, known_categories: list[str], use_intent_filter: bool = True,
               overrides: dict | None = None) -> QueryPlan:
    f = fold(question)
    p = QueryPlan(question=question, folded=f)

    # 1) Intenção (sentimento buscado)
    neg, pos = bool(NEG_RX.search(f)), bool(POS_RX.search(f))
    if neg and not pos:
        p.intent = "negativa"
    elif pos and not neg:
        p.intent = "positiva"

    # 2) Nota explícita > nota implícita pela intenção
    m = re.search(r"notas? (\d)(?:\s*(?:a|e|ou|-)\s*(\d))?", f)
    if m:
        a = int(m.group(1)); b = int(m.group(2) or a)
        if 1 <= a <= 5 and 1 <= b <= 5:
            p.score_range = (min(a, b), max(a, b))
    elif re.search(r"nota(s)? baixa|insatisfeit|1 estrela|detrator", f):
        p.score_range = (1, 2)
    elif re.search(r"nota(s)? alta|5 estrelas|promotor|muito satisfeit", f):
        p.score_range = (4, 5)
    elif use_intent_filter and p.intent == "negativa":
        p.score_range = (1, 3)
        p.notes.append("intenção negativa → considerando notas 1–3")
    elif use_intent_filter and p.intent == "positiva":
        p.score_range = (4, 5)
        p.notes.append("intenção positiva → considerando notas 4–5")

    # 3) Categoria (nome da categoria ou alias)
    cats: list[str] = []
    cat_terms: set[str] = set()
    words = set(re.findall(r"[a-z]{2,}", f))
    # (a) categoria específica: todos os tokens relevantes do nome aparecem na pergunta
    for c in known_categories:
        toks = [t for t in c.split("_") if len(t) > 2 and t not in {"e", "de", "do", "da"}]
        if c and c != "desconhecida" and toks and all(t in words for t in toks):
            cats.append(c)
            cat_terms.update(toks)
    # (b) alias genérico só se nenhuma categoria específica casou
    if not cats:
        for term in words:
            if term in CATEGORY_ALIASES:
                cats += CATEGORY_ALIASES[term]
                cat_terms.add(term)
    p.categories = sorted({c for c in cats if c in known_categories})

    # 4) Período e atraso
    p.years = sorted({int(y) for y in re.findall(r"\b(20\d\d)\b", f)})
    if re.search(r"(pedidos|entregas|compras) (entregues )?(com )?atras|entregues? (com )?atras", f):
        p.delivered_late = True

    # 5) Overrides vindos da interface (filtros escolhidos pelo usuário)
    for k, v in (overrides or {}).items():
        if v is not None and hasattr(p, k):
            setattr(p, k, v)

    # 6) Expansão lexical + temas em foco
    extra = [exp for rx, exp in EXPANSIONS.items() if re.search(rx, f)]
    p.lexical_query = " ".join([" ".join(content_terms(question))] + extra)
    p.focus_themes = [k for k, t in THEMES.items() if re.search(t["pattern"], f)]
    p.target_themes = sorted({t for rx, ts in TOPIC_THEMES.items() if re.search(rx, f) for t in ts}
                             | set(p.focus_themes))
    # termos de assunto que as evidências precisam cobrir (checagem anti-alucinação)
    p.key_terms = [t for t in dict.fromkeys(content_terms(question))
                   if not t.startswith(META_PREFIXES) and t not in cat_terms and not t.isdigit()]
    p.in_domain = bool(DOMAIN_RX.search(f)) or bool(p.categories)
    return p
