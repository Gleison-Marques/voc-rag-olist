# Exemplos de perguntas e respostas

Gerado por `scripts/make_examples.py` · busca: tfidf · geração: `extractive`

## Quais são os principais problemas relatados pelos clientes em suas avaliações?

`status=ok` · filtros: nota 1–3 · recorte: 14,680 avaliações · relevantes: 12 · sustentam: 12 · cobertura: 100% · busca: tfidf + estratificada-por-tema

> ℹ️ intenção negativa → considerando notas 1–3

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 14680 avaliações; filtros: nota 1–3).

**Padrões identificados:**
- **Produto não recebido / entrega incompleta** (3 das 12 evidências — ~27.8% do recorte): [R1] "Meu pedido chegou faltando um produto."; [R2] "Não recebi. Não chegou não chegou"; [R3] "Pedido incompleto. Meu pedido chegou faltando um item."
- **Troca, devolução, cancelamento ou reembolso** (3 das 12 evidências — ~12.4% do recorte): [R4] "Troca / devolução. a experiência de compra on-line e a entrega foram boas, porém o produto não atendeu às expe…"; [R5] "Recebi o produtos errado, e não consigo fazer a troca ou devolução"; [R6] "Foto diferente do produto, quero a troca ou a devolução do dinheiro"
- **Atraso / demora na entrega** (3 das 12 evidências — ~12.1% do recorte): [R7] "Demora na entrega e ainda atrasou."; [R8] "não do 5 estrela pois atrasou pedido"; [R9] "Passou do prazo de entrega, demorou."
- **Qualidade / defeito do produto** (3 das 12 evidências — ~11.3% do recorte): [R10] "Defeito produto. Recebi o pingente com defeito, quebrado."; [R11] "VEIO COM DEFEITO, O TECLADO NÃO FUNCIONA."; [R12] "Recebi o produto danificado"
- **Produto diferente do anunciado** (2 das 12 evidências — ~9.0% do recorte): [R5] "Recebi o produtos errado, e não consigo fazer a troca ou devolução"; [R6] "Foto diferente do produto, quero a troca ou a devolução do dinheiro"

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {1: 5, 2: 2, 3: 5}.

<details><summary>Evidências</summary>

- **[R1]** ⭐2 · `esporte_lazer` · 2018-03-20 · `review_id=030883ae6b53796dcd2a4c323da8ae1d` — “Meu pedido chegou faltando um produto.”
- **[R2]** ⭐1 · `automotivo` · 2018-08-30 · `review_id=ea666426d5ba15968bcb7ae61d5f82d5` — “Não recebi. Não chegou não chegou”
- **[R3]** ⭐2 · `utilidades_domesticas` · 2018-07-21 · `review_id=d100adcddcef25bfa83bb819d562211c` — “Pedido incompleto. Meu pedido chegou faltando um item.”
- **[R4]** ⭐3 · `relogios_presentes` · 2018-05-15 · `review_id=73825c944419be59995fdf5755400ba0` — “Troca / devolução. a experiência de compra on-line e a entrega foram boas, porém o produto não atendeu às expectativas e estou tendo dificuldades com a troca /devolução.”
- **[R5]** ⭐1 · `fashion_roupa_masculina` · 2017-09-26 · `review_id=ca95fa3ceed2ad933c1b8da7068d0efb` — “Recebi o produtos errado, e não consigo fazer a troca ou devolução”
- **[R6]** ⭐1 · `automotivo` · 2018-07-28 · `review_id=70b246f4e335731bdb18890a03682ed7` — “Foto diferente do produto, quero a troca ou a devolução do dinheiro”
- **[R7]** ⭐3 · `esporte_lazer` · 2018-03-22 · `review_id=6964442cd4b5a5a0c5bbfa8d6fb914ef` — “Demora na entrega e ainda atrasou.”
- **[R8]** ⭐3 · `informatica_acessorios` · 2018-03-23 · `review_id=69ee18728c863f8d237988b098a461cc` — “não do 5 estrela pois atrasou pedido”
- **[R9]** ⭐1 · `esporte_lazer` · 2018-01-18 · `review_id=2c74e9b846eeb175c36f4e5fd9f92eb3` — “Passou do prazo de entrega, demorou.”
- **[R10]** ⭐1 · `fashion_bolsas_e_acessorios` · 2018-08-25 · `review_id=5b14c151dac1c3e27a55c5c512a684b0` — “Defeito produto. Recebi o pingente com defeito, quebrado.”
- **[R11]** ⭐3 · `desconhecida` · 2017-12-21 · `review_id=9494016ad206d7f6893c03421d3b38fd` — “VEIO COM DEFEITO, O TECLADO NÃO FUNCIONA.”
- **[R12]** ⭐3 · `beleza_saude` · 2018-05-19 · `review_id=4a404516ca62f52dade7b00eb2accf72` — “Recebi o produto danificado”

</details>

## O que os clientes relatam sobre problemas relacionados à entrega?

`status=ok` · filtros: nota 1–3 · recorte: 14,680 avaliações · relevantes: 12 · sustentam: 7 · cobertura: 100% · busca: tfidf

> ℹ️ intenção negativa → considerando notas 1–3

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 14680 avaliações; filtros: nota 1–3).

**Padrões identificados:**
- **Atraso / demora na entrega** (10 das 12 evidências — ~12.1% do recorte): [R1] "Aguardando a entrega. Entrega em atraso."; [R2] "'produto bom, só chegou com atraso."; [R3] "demora no correios. eu nao posso falar se nao recebi o produto"
- **Produto não recebido / entrega incompleta** (3 das 12 evidências — ~27.8% do recorte): [R3] "demora no correios. eu nao posso falar se nao recebi o produto"; [R5] "Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam u…"; [R6] "erro na entrega. a entrega nao chegou correta completa"
- **Troca, devolução, cancelamento ou reembolso** (1 das 12 evidências — ~12.4% do recorte): [R5] "Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam u…"
- **Preço / frete / custo-benefício** (1 das 12 evidências — ~6.2% do recorte): [R5] "Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam u…"

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {1: 10, 2: 1, 3: 1}.

<details><summary>Evidências</summary>

- **[R1]** ⭐1 · `moveis_escritorio` · 2018-08-08 · `review_id=364e74a2d89a35fa3fad2beaf96d8f17` — “Aguardando a entrega. Entrega em atraso.”
- **[R2]** ⭐3 · `utilidades_domesticas` · 2018-01-07 · `review_id=39dbf0879c36fcf4578aac195d4f5582` — “'produto bom, só chegou com atraso.”
- **[R3]** ⭐1 · `beleza_saude` · 2018-04-22 · `review_id=7fba3f71c35a8ebffbdca7953aeb7943` — “demora no correios. eu nao posso falar se nao recebi o produto”
- **[R5]** ⭐1 · `utilidades_domesticas` · 2018-08-19 · `review_id=e69e0d8d1a8062ba01b76e2f684a61ee` — “Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam usar os Correios como transportadora.”
- **[R6]** ⭐1 · `beleza_saude` · 2018-06-22 · `review_id=249f0e6fef00a6e6dd15aeaad6c0afcc` — “erro na entrega. a entrega nao chegou correta completa”

</details>

## Quais aspectos da experiência de compra são mais elogiados pelos clientes?

`status=ok` · filtros: nota 4–5 · recorte: 24,389 avaliações · relevantes: 12 · sustentam: 12 · cobertura: 100% · busca: tfidf + estratificada-por-tema

> ℹ️ intenção positiva → considerando notas 4–5

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 24389 avaliações; filtros: nota 4–5).

**Padrões identificados:**
- **Satisfação / recomendação** (9 das 12 evidências — ~62.0% do recorte): [R1] "Ótimo. Excelente"; [R2] "Ótimo.. Excelente"; [R3] "Ubirajara. Eu recomendo ótimo!!"
- **Qualidade / defeito do produto** (5 das 12 evidências — ~10.0% do recorte): [R7] "super recomendo. Muito bom o prazo da entrega... Apenas o CD de instalação chegou danificado(quebrado), mais e…"; [R8] "Entrega rápida e produto embalado perfeitamente pra não ser danificado."; [R9] "Boa qualidade, funciona perfeitamente."
- **Entrega rápida / antes do prazo** (4 das 12 evidências — ~40.3% do recorte): [R4] "Entrega muito rapida, muito antes do prazo"; [R5] "Entrega rápida. Antes do prazo."; [R6] "Entrega rápida antes do prazo"
- **Embalagem** (4 das 12 evidências — ~4.9% do recorte): [R8] "Entrega rápida e produto embalado perfeitamente pra não ser danificado."; [R10] "Gostei do produto, porém veio mau embalado na caixa"; [R11] "recomendo. chegou, obrigada mas a caixa, a embalagem amassada e é um presente."

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {4: 2, 5: 10}.

<details><summary>Evidências</summary>

- **[R1]** ⭐5 · `telefonia` · 2018-08-25 · `review_id=f88878e3ca297d5d9975551cc85c9192` — “Ótimo. Excelente”
- **[R2]** ⭐5 · `bebidas` · 2018-08-28 · `review_id=a51fc12bf3505714e2b47cd453184e1d` — “Ótimo.. Excelente”
- **[R3]** ⭐5 · `instrumentos_musicais` · 2018-05-30 · `review_id=a9a0af31f1529ffb90c0d1234b4aee6e` — “Ubirajara. Eu recomendo ótimo!!”
- **[R4]** ⭐5 · `ferramentas_jardim` · 2017-02-16 · `review_id=8a24b9108e492e22e16764ce68fe3111` — “Entrega muito rapida, muito antes do prazo”
- **[R5]** ⭐5 · `eletronicos` · 2018-01-11 · `review_id=453f00dd360f142fe31eaf0842fecaeb` — “Entrega rápida. Antes do prazo.”
- **[R6]** ⭐5 · `livros_interesse_geral` · 2018-03-08 · `review_id=2b8725e08e79c9377bad95ef1150014b` — “Entrega rápida antes do prazo”
- **[R7]** ⭐5 · `automotivo` · 2018-08-03 · `review_id=e412221e8514988d3719b5647d4b14bf` — “super recomendo. Muito bom o prazo da entrega... Apenas o CD de instalação chegou danificado(quebrado), mais está tudo certo, pois já tinha o APP intalado.”
- **[R8]** ⭐5 · `utilidades_domesticas` · 2017-11-01 · `review_id=edecd29f2f7f80e5c30e63d4c81d6ea0` — “Entrega rápida e produto embalado perfeitamente pra não ser danificado.”
- **[R9]** ⭐5 · `eletronicos` · 2017-11-08 · `review_id=90f2f078dfc0ab0db41e5a0736bf989d` — “Boa qualidade, funciona perfeitamente.”
- **[R10]** ⭐4 · `moveis_decoracao` · 2018-05-16 · `review_id=90c7d15a2e8b60d31c8d0d14856b06a0` — “Gostei do produto, porém veio mau embalado na caixa”
- **[R11]** ⭐4 · `construcao_ferramentas_iluminacao` · 2018-08-15 · `review_id=b46e9ea6cd78b7b167c866332d9db6a0` — “recomendo. chegou, obrigada mas a caixa, a embalagem amassada e é um presente.”

</details>

## Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

`status=ok` · filtros: nota 1–3 · recorte: 14,680 avaliações · relevantes: 12 · sustentam: 8 · cobertura: 100% · busca: tfidf

> ℹ️ intenção negativa → considerando notas 1–3

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 14680 avaliações; filtros: nota 1–3).

**Padrões identificados:**
- **Atraso / demora na entrega** (10 das 12 evidências — ~12.1% do recorte): [R1] "'produto bom, só chegou com atraso."; [R2] "Aguardando a entrega. Entrega em atraso."; [R3] "Atraso Entrega. A entrega ainda não foi efetuada."
- **Produto não recebido / entrega incompleta** (5 das 12 evidências — ~27.8% do recorte): [R4] "O prazo de entrega finalizou e nao recebi o produto"; [R5] "demora no correios. eu nao posso falar se nao recebi o produto"; [R10] "Atraso entrega. Não recebi o produto"
- **Entrega rápida / antes do prazo** (1 das 12 evidências — ~6.3% do recorte): [R11] "Atraso. Produto não chegou no prazo"
- **Troca, devolução, cancelamento ou reembolso** (1 das 12 evidências — ~12.4% do recorte): [R12] "Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam u…"
- **Preço / frete / custo-benefício** (1 das 12 evidências — ~6.2% do recorte): [R12] "Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam u…"

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {1: 9, 2: 2, 3: 1}.

<details><summary>Evidências</summary>

- **[R1]** ⭐3 · `utilidades_domesticas` · 2018-01-07 · `review_id=39dbf0879c36fcf4578aac195d4f5582` — “'produto bom, só chegou com atraso.”
- **[R2]** ⭐1 · `moveis_escritorio` · 2018-08-08 · `review_id=364e74a2d89a35fa3fad2beaf96d8f17` — “Aguardando a entrega. Entrega em atraso.”
- **[R3]** ⭐1 · `esporte_lazer` · 2018-06-01 · `review_id=e6c1e9984a83ff62446ccb64ada34f53` — “Atraso Entrega. A entrega ainda não foi efetuada.”
- **[R4]** ⭐1 · `cama_mesa_banho` · 2018-04-19 · `review_id=6acb3cb2736d034e09778d4d2ebb5129` — “O prazo de entrega finalizou e nao recebi o produto”
- **[R5]** ⭐1 · `beleza_saude` · 2018-04-22 · `review_id=7fba3f71c35a8ebffbdca7953aeb7943` — “demora no correios. eu nao posso falar se nao recebi o produto”
- **[R10]** ⭐1 · `automotivo` · 2018-06-06 · `review_id=9d6c1f490b2b4bfef33820b5679e2d82` — “Atraso entrega. Não recebi o produto”
- **[R11]** ⭐2 · `eletronicos` · 2018-06-08 · `review_id=48b3ce236ea9d35a4850ea94ca9ca38f` — “Atraso. Produto não chegou no prazo”
- **[R12]** ⭐1 · `utilidades_domesticas` · 2018-08-19 · `review_id=e69e0d8d1a8062ba01b76e2f684a61ee` — “Paguei frete e não recebi o produto. Fui até os Correios, tinham devolvido. Muito chateada. Vcs não deveriam usar os Correios como transportadora.”

</details>

## Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

`status=ok` · filtros: nenhum · recorte: 39,069 avaliações · relevantes: 12 · sustentam: 12 · cobertura: 100% · busca: tfidf

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 39069 avaliações; filtros: nenhum).

**Padrões identificados:**
- **Qualidade / defeito do produto** (12 das 12 evidências — ~10.5% do recorte): [R1] "Recomendo. Produtos de qualidade"; [R2] "Produtos de qualidade e entrega rápida."; [R3] "Produto entregue corretamente e com muito boa qualidade em seus produtos"
- **Satisfação / recomendação** (6 das 12 evidências — ~41.0% do recorte): [R1] "Recomendo. Produtos de qualidade"; [R5] "Estão de parabéns pela pontualidade e qualidade dos produtos."; [R6] "Produtos de qualidade... recomendadíssimo"
- **Entrega rápida / antes do prazo** (5 das 12 evidências — ~27.5% do recorte): [R2] "Produtos de qualidade e entrega rápida."; [R4] "Produtos de qualidade, e chegou antes do prazo estipulado."; [R8] "Muito bom!. Produtos de qualidade e chegou antes do prazo."

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {4: 3, 5: 9}.

<details><summary>Evidências</summary>

- **[R1]** ⭐5 · `utilidades_domesticas` · 2018-06-15 · `review_id=3d2e151da275e5a6c1eba0d887bd8414` — “Recomendo. Produtos de qualidade”
- **[R2]** ⭐5 · `fashion_bolsas_e_acessorios` · 2018-03-23 · `review_id=b68e08e8010c57a676b984b777bbd91a` — “Produtos de qualidade e entrega rápida.”
- **[R3]** ⭐5 · `cama_mesa_banho` · 2018-02-09 · `review_id=600193c5944d1c002925a92455b1b9cd` — “Produto entregue corretamente e com muito boa qualidade em seus produtos”
- **[R4]** ⭐5 · `ferramentas_jardim` · 2017-08-29 · `review_id=da511ef83ea67dddfa9a0d8d38371083` — “Produtos de qualidade, e chegou antes do prazo estipulado.”
- **[R5]** ⭐5 · `informatica_acessorios` · 2018-04-14 · `review_id=dcebfef07ae5bad804471747a19338e0` — “Estão de parabéns pela pontualidade e qualidade dos produtos.”
- **[R6]** ⭐5 · `cama_mesa_banho` · 2017-09-29 · `review_id=c899c8813995b5e0620eda0120294e91` — “Produtos de qualidade... recomendadíssimo”
- **[R8]** ⭐5 · `telefonia` · 2018-08-14 · `review_id=7cb88b964d47e604925892fe80d2e207` — “Muito bom!. Produtos de qualidade e chegou antes do prazo.”

</details>

## O que os clientes mais elogiam em produtos de beleza e saúde?

`status=ok` · filtros: nota 4–5; categoria ∈ {beleza_saude} · recorte: 2,092 avaliações · relevantes: 12 · sustentam: 12 · cobertura: 100% · busca: tfidf + estratificada-por-tema

> ℹ️ intenção positiva → considerando notas 4–5

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 2092 avaliações; filtros: nota 4–5; categoria ∈ {beleza_saude}).

**Padrões identificados:**
- **Satisfação / recomendação** (10 das 12 evidências — ~63.0% do recorte): [R1] "Ótimo. Excelente atendimento entrega antes do prazo"; [R2] "Recomendo ótimo produto"; [R3] "Muito satisfeito"
- **Entrega rápida / antes do prazo** (6 das 12 evidências — ~45.7% do recorte): [R1] "Ótimo. Excelente atendimento entrega antes do prazo"; [R4] "Entrega super rápida, antes do prazo"; [R5] "Entrega rápida, antes da data prevista."
- **Embalagem** (5 das 12 evidências — ~5.1% do recorte): [R6] "Entrega rápida, muito antes do prazo. Produto bem embalado. Recomendo a loja."; [R7] "Muito bom. Chegou muito rápido e bem embalado, o que dificulta que o produto fique danificado."; [R10] "Tudo certo.. O produto foi bem embalado, gostei da preocupação para que não ficasse solto na caixa e pudesse v…"
- **Qualidade / defeito do produto** (3 das 12 evidências — ~6.6% do recorte): [R7] "Muito bom. Chegou muito rápido e bem embalado, o que dificulta que o produto fique danificado."; [R8] "O produto é bom, a qualidade não é excepcional, mas o produto funciona perfeitamente."; [R9] "Produto de ótima qualidade"
- **Atendimento / comunicação** (1 das 12 evidências — ~3.1% do recorte): [R1] "Ótimo. Excelente atendimento entrega antes do prazo"

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {4: 2, 5: 10}.

<details><summary>Evidências</summary>

- **[R1]** ⭐5 · `beleza_saude` · 2018-07-31 · `review_id=cba8182bc48095edddbb53695babdfde` — “Ótimo. Excelente atendimento entrega antes do prazo”
- **[R2]** ⭐5 · `beleza_saude` · 2018-03-14 · `review_id=9e6bbfd1b9997320e7d2d9dd765681c5` — “Recomendo ótimo produto”
- **[R3]** ⭐5 · `beleza_saude` · 2017-12-12 · `review_id=da40bf302bf459c9f36672d7ecb75c92` — “Muito satisfeito”
- **[R4]** ⭐5 · `beleza_saude` · 2018-04-12 · `review_id=9b9f2f534826695f04e5b7985c4384cd` — “Entrega super rápida, antes do prazo”
- **[R5]** ⭐5 · `beleza_saude` · 2017-08-03 · `review_id=4a225c31abbd6a1d9ea3ea2c132257b5` — “Entrega rápida, antes da data prevista.”
- **[R6]** ⭐4 · `beleza_saude` · 2017-03-29 · `review_id=609805afc75edb8cabef5a1e8ac2721c` — “Entrega rápida, muito antes do prazo. Produto bem embalado. Recomendo a loja.”
- **[R7]** ⭐5 · `beleza_saude` · 2018-05-19 · `review_id=f549131fc3d9f30d5deb47b65de158f0` — “Muito bom. Chegou muito rápido e bem embalado, o que dificulta que o produto fique danificado.”
- **[R8]** ⭐4 · `beleza_saude` · 2017-08-12 · `review_id=371b6c28d9300cbf4787ae5af1516fb8` — “O produto é bom, a qualidade não é excepcional, mas o produto funciona perfeitamente.”
- **[R9]** ⭐5 · `beleza_saude` · 2017-12-05 · `review_id=e36166cca20f917430ef21ce433e3c3f` — “Produto de ótima qualidade”
- **[R10]** ⭐5 · `beleza_saude` · 2018-06-20 · `review_id=f254877707c1658c8ab529a2ca69b75f` — “Tudo certo.. O produto foi bem embalado, gostei da preocupação para que não ficasse solto na caixa e pudesse vazar.”

</details>

## Quais problemas aparecem em móveis de escritório em 2018?

`status=ok` · filtros: nota 1–3; categoria ∈ {moveis_escritorio}; ano ∈ {2018} · recorte: 168 avaliações · relevantes: 12 · sustentam: 12 · cobertura: 100% · busca: tfidf + estratificada-por-tema

> ℹ️ intenção negativa → considerando notas 1–3

**Resposta direta:** As avaliações recuperadas concentram-se nos temas abaixo (recorte com 168 avaliações; filtros: nota 1–3; categoria ∈ {moveis_escritorio}; ano ∈ {2018}).

**Padrões identificados:**
- **Troca, devolução, cancelamento ou reembolso** (5 das 12 evidências — ~12.5% do recorte): [R3] "Produto Incompleto. Infelizmente, a embalagem do produto chegou violada. Estou aguardando reembolso ou envio d…"; [R4] "Veio na cor errada , riscado muito danificado e sujo,!! Horrível , já abri a solicitação para devolução"; [R7] "Péssimo o retorno. Solicito o cancelamento."
- **Qualidade / defeito do produto** (5 das 12 evidências — ~13.7% do recorte): [R4] "Veio na cor errada , riscado muito danificado e sujo,!! Horrível , já abri a solicitação para devolução"; [R5] "Produto chegou com um pequeno defeito."; [R6] "Insatisfeita. A cadeira veio com defeito de fabrica, uma solta para encaixar as partes em um lugar totalmente …"
- **Produto não recebido / entrega incompleta** (4 das 12 evidências — ~31.0% do recorte): [R1] "produto incompleto. a montagem esta muito dificil e o produto veio incompleto, esta faltando peça. Não gostei …"; [R2] "Faltando produto. Veio faltando uma cadeira"; [R3] "Produto Incompleto. Infelizmente, a embalagem do produto chegou violada. Estou aguardando reembolso ou envio d…"
- **Atraso / demora na entrega** (3 das 12 evidências — ~11.9% do recorte): [R10] "Nao tem boa avaliação por atraso na entrega"; [R11] "Aguardando a entrega. Entrega em atraso."; [R12] "insatisfeita. ja passou o prazo de entrega e ainda nao recebi o pedido"
- **Embalagem** (2 das 12 evidências — ~7.1% do recorte): [R3] "Produto Incompleto. Infelizmente, a embalagem do produto chegou violada. Estou aguardando reembolso ou envio d…"; [R6] "Insatisfeita. A cadeira veio com defeito de fabrica, uma solta para encaixar as partes em um lugar totalmente …"

**Limitações:** resposta extrativa (sem LLM); temas detectados por palavras-chave. Notas das evidências: {1: 11, 2: 1}.

<details><summary>Evidências</summary>

- **[R1]** ⭐1 · `moveis_escritorio` · 2018-08-21 · `review_id=599c761fc58ffdfe15e274dec9536c88` — “produto incompleto. a montagem esta muito dificil e o produto veio incompleto, esta faltando peça. Não gostei .”
- **[R2]** ⭐1 · `moveis_escritorio` · 2018-07-06 · `review_id=f9e24b292db472d101af0508ac4c019d` — “Faltando produto. Veio faltando uma cadeira”
- **[R3]** ⭐1 · `moveis_escritorio` · 2018-05-18 · `review_id=bc0f603d79a9fc5a6c2c8c426ec2c4a6` — “Produto Incompleto. Infelizmente, a embalagem do produto chegou violada. Estou aguardando reembolso ou envio do restante do produto adquirido.”
- **[R4]** ⭐1 · `moveis_escritorio` · 2018-04-16 · `review_id=e9900aab8cd7d3235400acefceab61c5` — “Veio na cor errada , riscado muito danificado e sujo,!! Horrível , já abri a solicitação para devolução”
- **[R5]** ⭐2 · `moveis_escritorio` · 2018-07-04 · `review_id=f6bc2b7fb670edc173862b9d84fd12c5` — “Produto chegou com um pequeno defeito.”
- **[R6]** ⭐1 · `moveis_escritorio` · 2018-06-15 · `review_id=5d4beea8e2c71baee7f55c7ae3ae3313` — “Insatisfeita. A cadeira veio com defeito de fabrica, uma solta para encaixar as partes em um lugar totalmente errado. E fora isso um pe veio com um pedacinho quebrado e a capa plastica branca do pistao veio rsagada”
- **[R7]** ⭐1 · `moveis_escritorio` · 2018-05-16 · `review_id=cf7d19695af62fbfa2cf1da2c1d797ec` — “Péssimo o retorno. Solicito o cancelamento.”
- **[R10]** ⭐1 · `moveis_escritorio` · 2018-03-22 · `review_id=045d330f147f09c3bd2426266ec5d414` — “Nao tem boa avaliação por atraso na entrega”
- **[R11]** ⭐1 · `moveis_escritorio` · 2018-08-08 · `review_id=364e74a2d89a35fa3fad2beaf96d8f17` — “Aguardando a entrega. Entrega em atraso.”
- **[R12]** ⭐1 · `moveis_escritorio` · 2018-08-08 · `review_id=31bccb8a92ef436bff3b116af68ca0f7` — “insatisfeita. ja passou o prazo de entrega e ainda nao recebi o pedido”

</details>

## Qual é a capital da França?

`status=fora_do_escopo` · filtros: nenhum · recorte: 39,069 avaliações · relevantes: 3 · sustentam: 3 · cobertura: 50% · busca: tfidf

A pergunta parece estar fora do escopo da base, que contém apenas avaliações de clientes do e-commerce Olist (2016–2018). Não encontrei avaliações que tratem de franca, então não vou gerar uma resposta.

<details><summary>Evidências</summary>

- **[R1]** ⭐1 · `cama_mesa_banho` · 2018-06-20 · `review_id=a6321e9034baf0a93e2a75c8236b2d86` — “péssimo. Não recebi o produto no meu endereço que é a rua negreiros lobato 30 804 lagoa rio de janeiro capital, cep 22471130”
- **[R2]** ⭐1 · `moveis_decoracao` · 2018-04-22 · `review_id=eade9034437b6986904e7f5ed42f2db7` — “Produto ainda nao foi entregue e consta para retirada nos correios, no Paraná. Uma vez que moro em São Paulo, capital, fico me perguntando como farei essa proeza! Preciso duma posição urgente!”
- **[R3]** ⭐1 · `moveis_decoracao` · 2018-04-05 · `review_id=02e5d591a55c27f6b272867ec4c3f92d` — “Não entregaram o produto e agora estão alegando que há dificuldade na entrega. Uma simples capa de máquina de lavar que deveria ser entregue em um bairro da capital do estado com toda infraestrutura.”

</details>

## O que os clientes acham do aplicativo de realidade virtual da loja?

`status=evidencia_insuficiente` · filtros: nenhum · recorte: 39,069 avaliações · relevantes: 12 · sustentam: 0 · cobertura: 100% · busca: tfidf

As avaliações recuperadas não tratam do assunto central da pergunta (aplicativo, realidade, virtual): só 0 avaliação(ões) o mencionam de forma direta (mínimo: 3). Para não gerar conclusões sem suporte, não vou responder; as avaliações mais próximas estão listadas abaixo.

<details><summary>Evidências</summary>

- **[R1]** ⭐1 · `brinquedos` · 2018-01-12 · `review_id=a0e385162107a3914c88a57eb8c3e96f` — “Estou esperando a agora. O q acham?”
- **[R2]** ⭐5 · `brinquedos` · 2017-10-06 · `review_id=348204e59743419ef79f2401e7098bae` — “Super recomendo o aplicativo lannister.com”
- **[R3]** ⭐5 · `cool_stuff` · 2018-01-17 · `review_id=27ac0cb30fed410de402d2293492348a` — “fui muito bem atendido,tanto virtual com por telefone”
- **[R4]** ⭐1 · `cama_mesa_banho` · 2017-12-22 · `review_id=035e2d533db834aca6bf6cac019ea05d` — “Vcs colocam um produto para venda sem ter em estoque, vcs acham que sou palhaço!!!”
- **[R5]** ⭐5 · `beleza_saude` · 2018-05-04 · `review_id=29f0553ef5b2a26bfe73dad354ca6e09` — “Recomendo para todos que eu conheço !! Ótima loja virtual !! Vocês estão de parabéns!!”

</details>

## Quais os problemas relatados em avaliações de 2015?

`status=sem_dados_no_filtro` · filtros: nota 1–3; ano ∈ {2015} · recorte: 0 avaliações · relevantes: 0 · sustentam: 0 · cobertura: 100% · busca: 

> ℹ️ intenção negativa → considerando notas 1–3

Não há avaliações com texto que atendam aos filtros identificados (nota 1–3; ano ∈ {2015}). Tente ampliar o recorte.

<details><summary>Evidências</summary>


</details>
