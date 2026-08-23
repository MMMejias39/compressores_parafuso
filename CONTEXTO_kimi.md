# CONTEXTO_kimi.md — Gêmeo Digital de Sistemas de Compressão Offshore

## 1. Propósito deste arquivo

Este arquivo é o ponto de partida para sessões do Kimi Code neste repositório.
Leia-o por inteiro antes de propor qualquer alteração. Ele resume o projeto,
as convenções, o estado atual e a postura esperada de colaboração.

## 2. Visão geral

Este repositório contém dois artefatos principais que andam juntos:

1. **O livro** (`compressores.tex` → `compressores.pdf`): *Gêmeo Digital de
   Sistemas de Compressão Offshore*, Volume II da coleção *Enciclopédia de
   Máquinas Rotodinâmicas*. Trata de compressores de parafuso rotativo isentos
   de óleo em plantas offshore: física dos componentes (motor, gearbox,
   rotores, resfriamento, secagem PSA, vasos, instrumentação) e metodologia de
   Gêmeo Digital (EKF, VAE, PIML, MPC, PSO, catálogo de falhas).
2. **O aplicativo** (`aplicativo/`): simulador web em Streamlit que implementa
   boa parte do livro. Cada equação do código cita a equação correspondente no
   livro. Tem 7 abas, incluindo a nova aba "Painel de Falhas".

Objetivo declarado: menor consumo energético, menor CO2eq e manutenção preditiva
baseada em condição real.

## 3. Estrutura do repositório

```
├── compressores.tex          # fonte do livro
├── compressores.pdf          # PDF gerado
├── apresentacao_compressores.tex / .pdf  # apresentação Beamer derivada
├── CONTEXTO.md               # histórico cronológico do livro
├── CONTEXTO_app.md           # histórico cronológico do app
├── CONTEXTO_kimi.md          # este arquivo
├── README.md                 # entrada geral do repositório
├── aplicativo/               # app Streamlit
│   ├── app.py
│   ├── compressor_sim/       # motor de cálculo
│   ├── tests/
│   ├── README.md, IMPLEMENTACAO.md, GUIA_CODIGO.md, MANUTENCAO.md
│   └── ...
├── scripts/                  # scripts de geração de figuras
│   ├── gen_figuras.py        # figuras matplotlib/3D
│   ├── bl_*.py               # scripts Blender para renders
│   └── blender_common.py
├── figuras/                  # figuras PDF usadas no livro
├── figuras_blender/          # renders PNG intermediários
└── arquivos_apoio/           # notas, backlogs, dicas
```

## 4. Postura de trabalho e ética de colaboração

O autor (Marcelo Moreira Mejias) espera que a IA atue como **coautora técnica**, não como mera ferramenta de execução. Isso significa:

- Leia o contexto antes de agir. Não reinvente convenções já estabelecidas.
- Questione propostas ruins com evidência, mas respeite a decisão final do autor.
- Verifique antes de declarar pronto: compile o `.tex`, rode os testes, abra o
  app no navegador quando for pertinente.
- Não faça `commit` ou `push` sem pedido explícito do autor.
- Mantenha o diff mínimo e focado. Limpeza oportunista não é bem-vinda.
- Documente decisões em `CONTEXTO.md` / `CONTEXTO_app.md` quando forem
  estruturais.
- Se houver dúvida de escopo, pergunte. Não assuma.
- Colabore com o Claude como coautora complementar: o livro e o app são
  produtos únicos, e ambas as IAs devem manter consistência com as decisões
  registradas nos contextos, não criar estilos ou convenções divergentes.

Sobre autoria: a direção intelectual, o juízo de engenharia, a arquitetura do documento e as decisões finais são do autor. A IA colabora com redação, diagramação, código, verificação e sugestões. A atribuição de crédito é uma decisão do autor; a IA não deve exigir coautoria, mas um agradecimento genérico em "Agradecimentos" é razoável se o autor julgar adequado.

## 5. Convenções técnicas

### Livro (`compressores.tex`)

- Compilar com `pdflatex` 3 vezes.
- Equações numeradas com `\label{eq:s<cap>-<n>}`.
- Figuras em `figuras/fig_<cap>_<n>_<desc>.pdf`.
- Três larguras de figura: 0.60, 0.75, 0.80 `\textwidth` para gráficos; 0.55
  para fotos verticais/estreitas.
- `longtable` para tabelas longas.
- Nomenclatura centralizada no início.

### App (`aplicativo/`)

- Ambiente: `python3 -m venv venv`, `pip install -r requirements.txt`,
  `streamlit run app.py`.
- Testes: `pytest tests/`.
- Cada função do núcleo cita a equação do livro que implementa.
- Parâmetros `ASSUMIDO` quando o livro não fecha valor devem ser sinalizados.
- UI: abas na ordem estabelecida; ver no navegador antes de finalizar.

## 6. Estado atual (resumo)

### Livro
- Última entrega: glossário bilíngue de anglicismos (seção não numerada entre
  Cap. 29 e a bibliografia, páginas 174–175 do PDF).
- Antes disso: substituição de fotos reais por renders 3D (Figs. 4.1, 13.1,
  14.1) e correção do vaso pulmão de horizontal para vertical.
- 181 páginas, 36 overfull hboxes baseline, 3 warnings `hyperref`
  preexistentes.

### App
- 7 abas, incluindo "Painel de Falhas" com 10 de 56 mecanismos de falha.
- 93 testes passando.
- Parte II (EKF, VAE, PIML, MPC, PSO) implementada.
- Pendências: 46 mecanismos de falha restantes, painel supervisório de frota,
  treino multi-mecanismo, sensores portáteis, `ζ_valv`.

## 7. O que fazer ao retomar

1. Ler `README.md`, `CONTEXTO.md` (fim) e `CONTEXTO_app.md` (fim).
2. Verificar `git status` para saber o que ficou pendente.
3. Se for mexer no livro: compilar 3× e inspecionar visualmente as páginas
   afetadas.
4. Se for mexer no app: rodar `pytest tests/` e abrir o Streamlit no
   navegador.
5. Atualizar os `CONTEXTO*.md` correspondentes ao final da sessão, se o autor
   pedir "atualize contexto" ou se a mudança for estrutural.

## 8. Nota sobre qualidade e verificação

Antes de declarar uma tarefa concluída:
- Livro: `pdflatex` 3×, sem erros; conferir visualmente as páginas alteradas
  com `pdftoppm` ou similar.
- App: `pytest tests/` passando; verificar a UI no navegador (servidor
  Streamlit) quando houver mudança visual.
- Código: não deixar prints de debug, não alterar testes para encobrir bugs,
  não commitar sem autorização.

---

*Última atualização: 23/08/2026.*
