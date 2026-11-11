"""Orquestração do RAG: pergunta → plano → recuperação → guardrails → geração → validação."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .config import settings
from .generator import INSUFFICIENT_TOKEN, BaseGenerator, ExtractiveGenerator, get_generator
from .prep import load_documents
from .query import QueryPlan, plan_query
from .retriever import Evidence, Retriever
from .text import fold

CITATION_RX = re.compile(r"\[(R\d+)\]")


def term_coverage(key_terms: list[str], evidences: list[Evidence]) -> tuple[float, list[str], int]:
    """Checagem de suporte textual (anti-alucinação).

    - cobertura: fração dos termos de assunto da pergunta presentes em ALGUMA evidência;
    - suporte: nº de evidências que, SOZINHAS, contêm ao menos metade dos termos de assunto.
      Evita aceitar "aplicativo de realidade virtual" só porque "virtual" aparece em
      "loja virtual" numa avaliação e "realidade" em outra.
    Usa radical de 5 letras sobre texto sem acento.
    """
    if not key_terms:
        return 1.0, [], len(evidences)
    stems = [t[:5] for t in key_terms]
    folded = [fold(e.text) for e in evidences]
    missing = [t for t, st in zip(key_terms, stems) if not any(st in f for f in folded)]
    need = max(1, -(-len(stems) // 2))  # teto(n/2)
    support = sum(sum(st in f for st in stems) >= need for f in folded)
    return 1 - len(missing) / len(key_terms), missing, support


@dataclass
class Answer:
    question: str
    status: str  # ok | evidencia_insuficiente | fora_do_escopo | sem_dados_no_filtro
    answer: str
    evidences: list[Evidence]
    cited_refs: list[str] = field(default_factory=list)
    filters: str = ""
    plan_notes: list[str] = field(default_factory=list)
    n_filtered: int = 0
    n_relevant: int = 0
    coverage: float = 1.0
    missing_terms: list[str] = field(default_factory=list)
    n_supporting: int = 0
    stats: dict = field(default_factory=dict)
    generator: str = ""
    backends: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def cited_evidences(self) -> list[Evidence]:
        refs = set(self.cited_refs)
        return [e for e in self.evidences if e.ref in refs]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidences"] = [asdict(e) for e in self.evidences]
        return d


class VoCRAG:
    def __init__(self, backend: str | None = None, generator: BaseGenerator | str | None = None):
        self.docs = load_documents()
        self.retriever = Retriever.load(self.docs, backend)
        self.generator = generator if isinstance(generator, BaseGenerator) else get_generator(generator)

    def plan(self, question: str, overrides: dict | None = None, use_intent_filter: bool = True) -> QueryPlan:
        return plan_query(question, self.retriever.categories, use_intent_filter, overrides)

    def ask(self, question: str, overrides: dict | None = None, use_intent_filter: bool = True,
            top_k: int | None = None) -> Answer:
        p = self.plan(question, overrides, use_intent_filter)
        r = self.retriever.retrieve(p, top_k)
        relevant = [e for e in r.evidences if e.relevant]
        coverage, missing, support = term_coverage(p.key_terms, relevant)
        base = dict(coverage=round(coverage, 2), missing_terms=missing, n_supporting=support, question=question, evidences=r.evidences, filters=p.filters_description(),
                    plan_notes=p.notes, n_filtered=r.n_filtered, n_relevant=len(relevant),
                    stats=r.stats, generator=self.generator.name, backends=r.backends)

        # ---------------- Guardrails ANTES da geração (não gasta LLM e não deixa alucinar)
        if r.n_filtered == 0:
            return Answer(status="sem_dados_no_filtro", answer=(
                "Não há avaliações com texto que atendam aos filtros identificados "
                f"({p.filters_description()}). Tente ampliar o recorte."), **base)
        weak = (len(relevant) < settings.min_evidence or coverage < settings.min_coverage
                or support < settings.min_evidence)
        if weak and not p.in_domain:
            return Answer(status="fora_do_escopo", answer=(
                "A pergunta parece estar fora do escopo da base, que contém apenas avaliações de "
                "clientes do e-commerce Olist (2016–2018). Não encontrei avaliações que tratem de "
                f"{', '.join(missing) or 'o assunto perguntado'}, então não vou gerar uma resposta."),
                **{**base, "evidences": r.evidences[:5]})
        if coverage < settings.min_coverage or support < settings.min_evidence:
            return Answer(status="evidencia_insuficiente", answer=(
                "As avaliações recuperadas não tratam do assunto central da pergunta "
                f"({', '.join(missing or p.key_terms)}): só {support} avaliação(ões) o mencionam "
                f"de forma direta (mínimo: {settings.min_evidence}). Para não gerar conclusões sem "
                "suporte, não vou responder; "
                "as avaliações mais próximas estão listadas abaixo."),
                **{**base, "evidences": r.evidences[:5]})
        if len(relevant) < settings.min_evidence:
            return Answer(status="evidencia_insuficiente", answer=(
                f"Encontrei apenas {len(relevant)} avaliação(ões) com relevância suficiente "
                f"(mínimo exigido: {settings.min_evidence}). As evidências não bastam para uma "
                "conclusão confiável; as avaliações mais próximas estão listadas abaixo para consulta."),
                **{**base, "evidences": r.evidences[:5]})

        # ---------------- Geração apenas com evidências relevantes
        warnings: list[str] = []
        try:
            text = self.generator.generate(question, relevant, r.stats, p.filters_description())
        except Exception as exc:  # falha de rede/chave: degrada para o modo extrativo
            warnings.append(f"LLM indisponível ({type(exc).__name__}: {exc}); usando modo extrativo.")
            text = ExtractiveGenerator().generate(question, relevant, r.stats, p.filters_description())
            base["generator"] = "extractive (fallback)"

        if text.strip().startswith(INSUFFICIENT_TOKEN):
            return Answer(status="evidencia_insuficiente",
                          answer=text.replace(INSUFFICIENT_TOKEN, "").strip(), warnings=warnings,
                          **{**base, "evidences": relevant})

        # ---------------- Validação DEPOIS da geração (rastreabilidade)
        valid = {e.ref for e in relevant}
        cited = list(dict.fromkeys(CITATION_RX.findall(text)))
        invalid = [c for c in cited if c not in valid]
        if invalid:
            warnings.append(f"Citações inexistentes removidas: {invalid}")
            for c in invalid:
                text = text.replace(f"[{c}]", "")
        cited = [c for c in cited if c in valid]
        if not cited:
            warnings.append("Resposta sem citações: substituída pela versão extrativa fundamentada.")
            text = ExtractiveGenerator().generate(question, relevant, r.stats, p.filters_description())
            cited = list(dict.fromkeys(CITATION_RX.findall(text)))
        return Answer(status="ok", answer=text, cited_refs=cited, warnings=warnings,
                      **{**base, "evidences": relevant})
