# Dicas de melhoria — `compressores.pdf`

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

## Checklist resumido

- [ ] Corrigir célula da Nomenclatura (p. 15) — colisão símbolo/significado
- [ ] Quebrar/encurtar título da subseção 5.5 (overfull 56,7 pt)
- [ ] Ajustar tabelas "Matriz de falhas" largas (overfull 37,4 pt e similares)
- [ ] Revisar overfulls remanescentes após as correções acima
- [ ] `\setlength{\headheight}{15pt}` (warnings do fancyhdr)
- [ ] `\texorpdfstring` em títulos com matemática (bookmarks)
- [ ] Preencher metadados do PDF via `\hypersetup`
