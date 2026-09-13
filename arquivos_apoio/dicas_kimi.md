# Dicas de melhoria — `compressores.pdf`

> **STATUS: ENCERRADO — checklist inteiro implementado em 01/08/2026**
> (commits `27997b6` e `3417919`), reverificado em 13/09/2026 contra o `.tex`
> atual. Não há pendência aberta aqui.
>
> ⚠️ **Não confundir com o `dicas_kimi.md` da raiz**, que é um relatório
> *diferente*, de 16/08/2026, sobre o documento já com 151 páginas. Este aqui é
> o de 31/07/2026, sobre a versão de 133 páginas.
>
> **Achado de calibração registrado no `CONTEXTO.md`:** este relatório acertou o
> diagnóstico mas **subestimou a extensão** — relatou 1 tabela "Matriz de
> falhas" com overfull grave (37,4 pt); a varredura completa achou **5**, a pior
> com 56,7 pt. Vale como lembrete de que a contagem de um revisor externo é
> ponto de partida, não escopo fechado.

Avaliação de qualidade do documento (133 páginas, A4, compilado em 31/07/2026).
Diagnóstico geral: documento em bom nível técnico-editorial; os itens abaixo são
ajustes finos para uma versão final.

## 1. Defeitos visuais reais (prioridade alta)

### 1.1 Colisão na Nomenclatura (página 15 do PDF)
- Na tabela "Psicrometria e Trocadores de Calor", a célula de símbolo
  `$C_{\min}, C_{\max}, C_r$` transborda para a coluna "Significado",
  imprimindo algo como "C_rCapacidades térmicas".
- **Correção sugerida:** alargar a coluna de símbolos (ex.: `p{2.8cm}`),
  quebrar os símbolos em duas linhas ou usar `tabularx` com coluna flexível.

### 1.2 Overfull hbox grave — título da subseção 5.5 (`compressores.tex:1942`)
- `\subsection{\textbf{Razão Volumétrica Interna ($V_i$) e Perdas por Sub/Sobrecompressão}}`
  ultrapassa **56,7 pt** da margem (≈ 2 cm).
- **Correção sugerida:** remover o `\textbf{}` (a classe já aplica negrito nos
  títulos) e/ou encurtar o título; "Sub/Sobrecompressão" pode virar
  "Sub- e Sobrecompressão" para permitir hifenização.

### 1.3 Overfull hbox grave — tabela de matriz de falhas (`compressores.tex:785`)
- Tabela `tabular` com 37,4 pt além da textwidth (uma das "Matriz de falhas").
- **Correção sugerida:** envolver em `\resizebox{\textwidth}{!}{...}`,
  migrar para `tabularx`, ou reduzir com `\small`/`\footnotesize`.
- Verificar as demais tabelas "Matriz de diagnóstico/falhas" — o padrão se
  repete em vários capítulos.

## 2. Overfulls menores

- 44 overfull hboxes no total no log; além dos dois graves acima, há ~10 com
  excesso entre 2 pt e 32 pt (linhas 296, 908, 1294, 1423, 2352, 2510, 265,
  2792, 3034, 3152...).
- **Correção sugerida:** após corrigir os graves, revisar os restantes no log
  (`grep "Overfull" compressores.log | sort -t'(' -k2 -rn`). Muitos se resolvem
  com `\emergencystretch=1em` no preâmbulo ou microtype já ativo.

## 3. Warnings cosméticos (prioridade baixa)

- **11× `hyperref: Token not allowed in PDF string`** — fórmulas/acentos em
  títulos de seção quebram os bookmarks do PDF.
  - Correção: usar `\texorpdfstring{$V_i$}{Vi}` nos títulos com matemática.
- **4× `fancyhdr: \headheight is too small (14.5pt)`**
  - Correção: `\setlength{\headheight}{15pt}` (ou o valor indicado no log) no
    preâmbulo, com `\addtolength{\topmargin}{-0.5pt}` se quiser manter o layout.
- **1× `destination with the same identifier (name{page.1})`** — efeito típico
  da mistura de numeração romana/arábica; inofensivo.
- **11× float `!h` promovido para `!ht`** — considerar trocar `[!h]` por
  `[!htbp]` nas figuras/tabelas.
- **3 underfull hboxes** — insignificantes.

## 4. Metadados do PDF

- `Subject` e `Keywords` vazios; documento não *tagged* (acessibilidade).
- **Correção sugerida:** no preâmbulo:
  ```latex
  \hypersetup{
    pdftitle={Gêmeo Digital de Sistemas de Compressão Offshore},
    pdfauthor={Marcelo Moreira Mejias},
    pdfsubject={Diretrizes Técnicas, Modelagem e Implementação},
    pdfkeywords={compressor de parafuso, offshore, gêmeo digital, PIML, EKF, MPC}
  }
  ```

## 5. Observações sem necessidade de ação

- Página 119 (PDF) quase vazia: fim natural do capítulo 24 na classe `book`.
- O que parecia "da plant a" na p. 59 era artefato de renderização em baixa
  resolução — o texto está correto no PDF.
- Capa: data "31 de julho de 2026" vs "Rev. 26/07/2026" — coerente; apenas
  confirmar se a Rev. deve acompanhar a data de compilação.

## Checklist resumido — todos concluídos

Verificações reconferidas em 13/09/2026, com o comando de cada uma:

- [x] Célula da Nomenclatura (p. 15) — coluna Símbolo alargada de 2,0 cm para
      2,8 cm nas 8 tabelas de Nomenclatura, compensada encolhendo Significado.
- [x] Título da subseção 5.5 — "Sub/Sobrecompressão" virou "Sub- e
      Sobrecompressão", permitindo hifenização. (O `\textbf{}` no título foi
      **mantido de propósito**: é o padrão do documento inteiro, 105
      subseções — não era o defeito.)
- [x] Tabelas "Matriz de falhas" largas — **5** convertidas para
      `\resizebox{\textwidth}{!}{...}`, não 1 como o relatório supunha.
- [x] Overfulls remanescentes — `\emergencystretch=1em` no preâmbulo resolveu a
      maior parte. Hoje: **36 overfulls, o maior com 2,01 pt** (linhas de
      Nomenclatura com a palavra "adimensional"), classificados como
      cosmeticamente insignificantes e estáveis há meses.
- [x] `headheight` — `\geometry{margin=2.5cm, headheight=15pt}`, linha 42.
- [x] `\texorpdfstring` em títulos com matemática — 4 ocorrências; as 11
      warnings de bookmark do hyperref foram a zero.
- [x] Metadados do PDF — `pdfsubject` e `pdfkeywords` preenchidos no
      `\hypersetup`.

**Item que o relatório classificou como "sem necessidade de ação" e vale
registrar:** a observação sobre a capa (data automática × "Rev.") continua
resolvida pela convenção de revisão manual já estabelecida.

## 6. Aprendizados das sessões do Volume I (12/09/2026)

- Nomear arquivos com o nome definitivo desde o início; nomes de trabalho
  temporários geram duplicatas (`teorias`, `theorias`, cópias datadas) que
  confundem o autor.
- Verificar sempre o estado real do repositório por clone fresco; índices e
  leituras locais podem divergir do remoto.
- Comandos de stage seguros quando o índice local é suspeito:
  `git hash-object -w <arquivo>`, `git update-index --cacheinfo`,
  `git commit-tree` (mensagem com `-F <arquivo>`), `git update-ref`,
  depois `git push`.
