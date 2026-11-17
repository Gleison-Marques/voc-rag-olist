from __future__ import annotations

import json
import os
from collections import Counter

from .config import settings
from .retriever import Evidence
from .text import THEMES

INSUFFICIENT_TOKEN = "EVIDENCIAS_INSUFICIENTES"

SYSTEM_PROMPT = f"""Você é um analista de Voice of Customer de um e-commerce brasileiro.
Responda à pergunta do gestor usando EXCLUSIVAMENTE:
(a) as avaliações de clientes fornecidas, identificadas como [R1], [R2], …;
(b) as "Estatísticas do recorte", calculadas sobre todas as avaliações que atendem aos filtros.

Regras obrigatórias:
1. Toda afirmação sobre clientes deve citar ao menos uma avaliação no formato [R#]. Use só os identificadores fornecidos.
2. Não invente números. Percentuais e contagens só podem vir das Estatísticas do recorte (diga que são aproximados, pois os temas são detectados por palavras-chave).
3. Não generalize além do que as evidências mostram; diferencie "aparece em várias avaliações" de "aparece em uma avaliação".
4. Se as avaliações não tratam do que foi perguntado, ou a pergunta está fora do escopo (avaliações de clientes do e-commerce), responda começando com a linha {INSUFFICIENT_TOKEN} e explique em 1–2 frases o que falta.
5. Responda em português do Brasil, de forma objetiva.

Formato:
**Resposta direta:** 2–3 frases.
**Padrões identificados:** 3–6 tópicos, cada um com citações [R#].
**Limitações:** 1–2 frases sobre o alcance das evidências."""


def build_user_prompt(question: str, evidences: list[Evidence], stats: dict, filters: str) -> str:
    ctx = "\n\n".join(e.as_context_line(settings.max_review_chars) for e in evidences)
    st = json.dumps(stats, ensure_ascii=False)
    return (
        f"Pergunta: {question}\n\nFiltros aplicados: {filters}\n\n"
        f"Estatísticas do recorte (corpus completo filtrado): {st}\n\n"
        f"Avaliações recuperadas ({len(evidences)}):\n{ctx}"
    )


class BaseGenerator:
    name = "base"

    def generate(self, question: str, evidences: list[Evidence], stats: dict, filters: str) -> str:
        raise NotImplementedError


class AnthropicGenerator(BaseGenerator):
    name = "anthropic"

    def __init__(self, model: str | None = None):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model or settings.llm_model or "claude-sonnet-5-5"

    def generate(self, question, evidences, stats, filters):
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_prompt(question, evidences, stats, filters)}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


class OpenAICompatibleGenerator(BaseGenerator):
    name = "openai"

    def __init__(self, model: str | None = None, base_url: str | None = None):
        from openai import OpenAI

        base_url = base_url or settings.llm_base_url or None
        api_key = os.getenv("OPENAI_API_KEY") or ("ollama" if base_url else None)
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model or settings.llm_model or "gpt-4o-mini"

    def generate(self, question, evidences, stats, filters):
        r = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, evidences, stats, filters)},
            ],
        )
        return r.choices[0].message.content or ""


class ExtractiveGenerator(BaseGenerator):
    name = "extractive"

    def generate(self, question, evidences, stats, filters):
        if not evidences:
            return f"{INSUFFICIENT_TOKEN}\nNenhuma avaliação relevante foi encontrada."
        by_theme: dict[str, list[Evidence]] = {}
        for e in evidences:
            for t in e.themes or ["outros"]:
                by_theme.setdefault(t, []).append(e)
        ranked = sorted(by_theme.items(), key=lambda kv: -len(kv[1]))
        pct = stats.get("temas_pct", {})
        lines = ["**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo "
                 f"(recorte com {stats.get('n', 0)} avaliações; filtros: {filters})."]
        lines.append("\n**Padrões identificados:**")
        for theme, evs in ranked[:5]:
            label = THEMES.get(theme, {}).get("label", "Outros assuntos")
            share = f" — ~{pct[label]}% do recorte" if label in pct else ""
            quotes = "; ".join(f"[{e.ref}] \"{e.text[:110]}{'…' if len(e.text) > 110 else ''}\"" for e in evs[:3])
            lines.append(f"- **{label}** ({len(evs)} das {len(evidences)} evidências{share}): {quotes}")
        notas = Counter(e.score for e in evidences)
        lines.append(
            "\n**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. "
            f"Notas das evidências: {dict(sorted(notas.items()))}."
        )
        return "\n".join(lines)


def get_generator(provider: str | None = None) -> BaseGenerator:
    provider = (provider or settings.llm_provider).lower()
    if provider == "auto":
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("OPENAI_API_KEY") or settings.llm_base_url:
            provider = "openai"
        else:
            provider = "extractive"
    try:
        if provider == "anthropic":
            return AnthropicGenerator()
        if provider == "openai":
            return OpenAICompatibleGenerator()
    except Exception as exc:  # pacote ausente / chave ausente
        print(f"[aviso] gerador '{provider}' indisponível ({exc}); usando modo extrativo.")
    return ExtractiveGenerator()
