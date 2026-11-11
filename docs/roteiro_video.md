# Roteiro do vídeo (até 7 minutos)

Sugestão de divisão para 3 pessoas (A, B, C). Tempos aproximados; ensaie com cronômetro. Grave a tela do Streamlit (`streamlit run app.py`) e do README/diagrama.

| Tempo | Quem | Tela | Fala (resumo) |
|---|---|---|---|
| 0:00–0:40 | A | Slide/título + README §1 | **Problema:** e-commerce com ~100 mil avaliações; a nota mostra *se* o cliente está insatisfeito, mas o *porquê* está no texto livre. Ler manualmente não escala. Objetivo: o gestor pergunta em linguagem natural e recebe uma resposta **com as avaliações que a sustentam**. |
| 0:40–1:50 | A | Diagrama mermaid (README §2) | **Arquitetura:** duas fases. *Offline:* CSVs → seleção/limpeza → join com pedidos, itens e produtos (categoria, atraso) → temas → índice TF-IDF + embeddings multilíngues no FAISS. *Online:* planejador → busca híbrida com filtros → fusão RRF → guardrails → LLM com citações → validação. |
| 1:50–2:50 | B | README §3 (tabela) + `build_stats.json` | **Base:** de 100 mil para 39 mil documentos. Explicar: só avaliações com texto; título ausente em 88% → usa a mensagem; descarte de textos com menos de 2 palavras; 304 duplicatas; **sem chunking** (mediana de 54 caracteres, cada avaliação é atômica); texto exibido preservado e normalização só na cópia de busca; metadado de atraso = entrega real − prazo estimado. |
| 2:50–3:50 | B | README §4.1–4.2 | **Recuperação:** planejador extrai intenção ("problemas" → notas 1–3), categoria, ano e atraso, e expande a consulta lexical. Híbrido: lexical pega termos exatos ("correios", "estorno"), denso pega paráfrases; RRF une sem calibrar scores. Rerank por tema e polaridade ("entrega sem problemas" não é problema). Para perguntas panorâmicas, **estratificação por tema**. |
| 3:50–5:30 | C | **Demo no Streamlit** | 1) "Quais são os principais problemas…?" → mostrar filtro inferido, estatísticas do recorte (gráfico), resposta com [R#] e abrir 2 evidências com `review_id`. 2) "Quais avaliações sustentam … prazo de entrega?" → evidências com "atrasou Xd". 3) "O que os clientes mais elogiam em produtos de beleza e saúde?" → filtro de categoria + nota 4–5. |
| 5:30–6:20 | C | Demo das recusas | 4) "Qual é a capital da França?" → **fora do escopo**. 5) "O que acham do aplicativo de realidade virtual da loja?" → **evidência insuficiente**: palavras soltas existem ("loja virtual", "na realidade"), mas nenhuma avaliação trata do assunto, e o sistema explica por quê. 6) "avaliações de 2015" → sem dados no filtro. |
| 6:20–7:00 | A | README §7 e §10 | **Avaliação e desafios:** 17 perguntas, 100% na decisão responder/recusar, precisão temática 0,93, 100% de citações válidas (com a ressalva de que o conjunto também serviu para calibrar). Desafios: falsos positivos do léxico ("suporte", "não gostei"), viés de frequência do RAG (resolvido com estatísticas do recorte) e alucinação (guardrails antes e validação de citações depois). Próximos passos: self-query com LLM, BERTopic, conjunto rotulado maior. |

## Dicas de gravação
- Rode `python scripts/build_kb.py` antes e abra o app já carregado (o primeiro carregamento demora alguns segundos).
- Deixe o `.env` com `ANTHROPIC_API_KEY` para mostrar a geração com LLM; mencione que sem chave o sistema cai no modo extrativo.
- Mostre a barra lateral com os filtros: dá para provar que os metadados funcionam alterando a categoria ao vivo.
- Na demo, **leia em voz alta uma evidência citada** e mostre que ela confirma a frase da resposta. É o critério principal da avaliação.
