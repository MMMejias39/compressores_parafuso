# Backlog de melhorias — `Volume_0_Notacoes_e_Calculo.tex`

**Origem:** auditoria de conteúdo e de conformidade do Volume 0 (24/09/2026
estimada pela data de edição; base = 29 páginas compiladas), pedida pelo autor
("podemos continuar a melhorar o volume 0?") com a instrução de priorizar por
**criticidade** e desenvolver na ordem.

**Critério de criticidade:** o quanto a ausência do item bloqueia ou degrada a
leitura dos Volumes I e II — que são o destino declarado deste volume
("reunir, num único percurso curto, exatamente o que os Volumes I e II usam").
Cada item cita os pontos exatos dos volumes seguintes onde o conteúdo é
exigido. Defeitos de conformidade com as convenções da coleção precedem o
conteúdo (já resolvidos — ver "Concluídos" ao fim).

**Status:** ✅ **IMPLEMENTADO — 8/8 itens na sessão de 12/09/2026.** Este
arquivo fica como registro do planejamento; as descrições abaixo referem-se
ao estado do volume **antes** da implementação. Estado pós-implementação:
42 páginas, 36 equações, 7 figuras, 7 tabelas, 18 exercícios resolvidos,
compilação 3× com 0 erros / 0 overfulls / 0 referências indefinidas, 0
violações de auto-referência. Nada commitado sem pedido explícito do autor.

---

## P1 — Crítico: bloqueia a leitura dos volumes seguintes

### B0-01 — Números complexos e fasores
- **Onde é exigido:** Cap. 7 do Vol. I (Fundamentos de Eletricidade) inteiro —
  `\subsection{Regime permanente senoidal e fasores}` (`sub:v1-c7-fasores`,
  Eq. `v1-c7-13` define a impedância `Z_L = jωL`) pressupõe o número complexo,
  a identidade de Euler e a correspondência senoidal↔fasor; volta na potência
  (`sub:v1-c7-potencia`) e nos mecanismos de falha elétrica do Vol. II.
- **Gap:** o Vol. 0 nunca menciona número complexo além de citar
  "$\mathrm{i}$" na Tabela 2.1; o leitor chega ao Cap. 7 do Vol. I sem o
  vocabulário inteiro.
- **Ação:** nova subseção ao fim do Cap. 4 (Funções Elementares), antes da
  síntese — identidade de Euler, forma polar, o truque $\mathrm{d}/\mathrm{d}t
  \leftrightarrow \mathrm{i}\omega$, definição do fasor, as duas condições de
  validade (linearidade + frequência única, exatamente como o Vol. I enuncia),
  ponte com $Z$ e nota $\mathrm{i}$ × $\mathrm{j}$ (o Vol. I usa $\mathrm{j}$).
  1 figura nova (plano complexo/fasor girante).
- **Verificação:** compilação 3×, 0 erros/overfulls; auto-referência das
  equações novas; conferência visual das páginas.

### B0-02 — Derivada material $\mathrm{D}/\mathrm{D}t$ + menção a EDP
- **Onde é exigido:** Vol. I Cap. 2 define a derivada material
  ($\frac{D\varphi}{Dt}$) e a usa no teorema de transporte de Reynolds e em
  toda a dinâmica (Navier-Stokes é escrita $\rho\,D\bm{v}/Dt = \nabla\cdot\bm{\sigma}+\rho\bm{b}$);
  EDPs aparecem sem nunca ser apresentadas (Navier-Stokes, condução de calor).
- **Gap:** o Cap. 6 do Vol. 0 cobre derivada parcial e gradiente, mas não a
  diferença "taxa num ponto fixo × taxa seguindo a partícula"; o Cap. 8 fala
  só de EDO.
- **Ação:** subseção nova no Cap. 6 ($D/Dt$, com a regra da cadeia já
  ensinada) + subseção curta no Cap. 8 (o que é uma EDP; condições de
  contorno; nenhuma é resolvida na coleção — reconhecer o objeto).

## P2 — Alto: formalismo usado explicitamente nos volumes seguintes

### B0-03 — Convenção de Einstein, delta de Kronecker, divergência/rotacional e teorema da divergência
- **Onde é exigido:** Vol. I Cap. 2 usa $\delta_{ij}$ e soma implícita na lei
  constitutiva ($\tau_{ij} = 2\mu S_{ij} - \frac{2}{3}\mu(\nabla\cdot\bm{v})\delta_{ij}$);
  o **teorema da divergência** é invocado quatro vezes (forma integral →
  diferencial dos balanços, Caps. 2/4/6); $\nabla\times$ aparece nas equações
  de Maxwell (Cap. 7). O "teorema de Stokes" citado no backlog original
  revelou-se a *hipótese* de Stokes (fluido) — o teorema integral do rotacional
  NÃO é usado nos volumes; entra só como menção.
- **Ação:** subseção no Cap. 5 (índices: Kronecker + convenção de Einstein);
  subseção no Cap. 6 (divergência e rotacional — significado físico de fonte/
  circulação); subseção no Cap. 7 (integrais de linha e de superfície +
  teorema da divergência, com a leitura operacional de balanço; Stokes em uma
  frase).

### B0-04 — Autovalores e autovetores
- **Onde é exigido:** Vol. I Cap. 2 ("Sendo simétrico e real, $\bm{\sigma}$
  admite três autovalores reais" — tensões principais, base dos critérios de
  falha). O Vol. II não usa o termo, mas herda o vocabulário por modos/
  estabilidade.
- **Gap:** o Cap. 5 cita o determinante como critério de existência e para por
  aí.
- **Ação:** subseção no Cap. 5 (equação de autovalores, polinômio
  característico, significado físico de modo natural/direção principal;
  ponte com as tensões principais do Vol. I).

## P3 — Médio: didática e acabamento

### B0-05 — Exercícios resolvidos
- **Justificativa:** o parecer Manus recomenda exemplos numéricos resolvidos
  como meio de ampliar o público; o backlog V0 original deixou a decisão em
  aberto — **resolvida a favor** pelo autor ao mandar criar e seguir este
  backlog.
- **Ação:** subseção "Exercícios resolvidos" ao fim de cada capítulo (antes da
  síntese), 2 exercícios por capítulo, resolução completa com os números de
  equação citados, nada além do que o capítulo ensinou.

### B0-06 — Séries geométricas
- **Ação:** meia página no Cap. 9 (soma da geometérica, significado do
  $|r|<1$, uso em decaimentos em cascata/respostas ao degrau discretizadas).

### B0-07 — Figura da capa
- **Gap:** a capa tem um `vspace{5cm}` vazio com comentário "Placeholder para
  ilustração conceitual do Volume 0".
- **Ação:** figura vetorial TikZ conceitual (a escada Volume 0 → I → II), no
  padrão vetorial versionado no próprio `.tex` do volume.

## P4 — Baixo: cosmético / decisão

### B0-08 — Consistência de símbolos na Tabela de letras gregas
- $\omega$/$\Omega$ lista "resistência elétrica" — o ohm é $\Omega$ como
  *unidade*, não como grandeza; ajustar a redação para não sugerir colisão com
  velocidade angular. (Avaliar também se vale uma Nomenclatura própria do
  volume — provavelmente não, pois o Cap. 2 já é a tabela de notação da
  coleção.)

---

## Concluídos (auditoria de conformidade desta sessão, antes do conteúdo)

- ✅ **`\clearpage` antes dos 10 capítulos** — faltava (convenção da coleção);
  conferido por extração de páginas: Caps. 1–10 abrem em p. 7, 8, 11, 13, 15,
  17, 20, 23, 26, 28.
- ✅ **Lista de Figuras + Lista de Tabelas** ausentes → adicionadas (mesmo
  formato do Vol. I: `\phantomsection` + `\addcontentsline`).
- ✅ **Auto-referência de equação** (`\eqref{}` de si mesma no parágrafo
  anterior): 2 violações (`eq:v0-c4-2`, `eq:v0-c6-4`) corrigidas — varredura
  agora 0/22.
- ✅ **Prosa:** "dez ve menos que mil" (typo + sentido errado — 10⁴ é 10×
  *mais* que mil e 10× *menos* que cem mil); frase truncada do trabalho
  líquido no $p$–$V$; "vetorial duplo repetido"; citação da Eq. 6.4 só depois
  de aparecer.
- ✅ **Achado colateral (fora deste volume):** o Volume I não usa
  `\clearpage` nenhum — desvia da convenção; decisão pendente do autor.
- ✅ **Compilação de referência:** 3 passagens, 29 páginas, 0 erros, 0
  overfulls, 0 referências indefinidas.
