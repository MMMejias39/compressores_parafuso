dicas_COPILOT.md — Verificação rápida do PDF compressores.pdf

Resumo das verificações automáticas

1) Extração de texto: pdftotext -layout produziu compressores.txt sem ocorrências de referências não-resolvidas do tipo "??" e sem caracteres de substituição U+FFFD (�).

2) Contagens/consistência:
   - Ocorrências da palavra “Equação” / "Eq." no texto extraído: 206
   - Labels de equação no fonte compressores.tex (\label{eq:s*}): 192
     *Obs.*: diferença pequena — "Equação" aparece também em prosa explicativa; não prova perda automática, mas recomenda reconciliar numericamente.

3) Ocorrências de "Tabela"/"Figura": 53 tabelas detectadas no texto extraído; 51 figuras detectadas. (Não há "Table" em inglês.)

Itens que merecem revisão visual manual (achados automatizados / sinais de atenção)

A. Equações com layout/recorte estranho na extração
   - Equação (11.6): na extração a linha aparece fragmentada/embaralhada (trechos com parênteses/sobrescritos deslocados). No .tex há label eq:s11-6; revisar visualmente a página do PDF que contém (11.6) para confirmar que a expressão completa e os expoentes/potências aparecem corretamente no PDF impresso.
   - Equação (9.8): presente; a extração mostrou a fórmula com numerador/denominador em linhas separadas, mas a versão textual inclui a divisão por 60 e a explicação — validar visualmente (9.8) para garantir o fração está formatada corretamente no PDF (parece OK na extração, mas conferir layout no PDF).
   - Equação (15.7): encontrada; dado histórico de erro de unidade nesta equação no repositório, confirmar que a fórmula no PDF reflete a versão corrigida (conversão para Kelvin) e que a legenda/nota explicativa acompanha a alteração.

B. Referências cruzadas e numeradores
   - Não foram encontrados "??" (marcadores de referência não resolvida) no texto extraído — bom sinal. Ainda assim, recomenda-se varredura visual rápida em todos os locais onde o texto menciona "Equação (x.y)" para garantir que o número corresponde ao conteúdo exibido (a comparação automática entre texto extraído e labels do .tex é informativa, mas falhas de layout podem ocultar problemas visuais).

C. Tabelas e diagramação
   - O relatório de diagramação (dicas_kimi.md / relatorio_diagramacao.md) indica overfulls e células de Nomenclatura com colisão — estes são problemas de layout (largura/células) que não aparecem como "texto faltante" mas prejudicam a leitura. Verificar visualmente as tabelas citadas no relatório (ex.: tabela de Nomenclatura, matrizes de falha) e as subseções com overfulls (ex.: subseção 5.5 mencionada no relatório) para confirmar que o conteúdo foi ajustado e não cortado.

D. Metadados / acessibilidade
   - A extração de texto não mostrou bytes de controle residuais (ligaduras fi/ff corrigidas previamente). Ainda assim, confirmar que o PDF contém metadados (pdftitle/pdfauthor) e que bookmarks estão corretos (problemáticas antigas com \texorpdfstring foram apontadas no relatório).

E. Arquivo não verificado
   - "referências extras para as fórmulas.md" na raiz é um arquivo binário (.odt renomeado). Não foi possível checar seu conteúdo como Markdown. Se esse arquivo deveria alimentar alguma tabela/legenda no PDF, peça-se a conversão para texto (.md/.txt/.bib/.csv) para checagem.

Recomendações concretas e próximas ações (prioridade)

1) Inspeção visual rápida do PDF (10–15 min): revisar páginas que contêm (11.6), (9.8) e (15.7) — confirmar layout completo das expressões, expoentes e frações. (Prioridade alta para 11.6, pois a extração mostrou fragmentação.)

2) Conferir tabelas com risco de corte: abrir PDF nas páginas apontadas por dicas_kimi.md (ex.: Nomenclatura, matrizes de falha, subseção 5.5) e verificar se alguma célula está truncada. (Prioridade alta para Nomenclatura.)

3) Reconciliar contagem de equações: fazer uma lista automatizada de todos os rótulos \label{eq:s*} no .tex e pesquisar cada "(C.N)" correspondente no texto extraído para detectar saltos/ausências numéricas. A diferença atual é pequena, mas esse confronto finda por achar renumerações acidentais. (Prioridade média; já disponível lista de labels.)

4) Convertendo e revisar o arquivo binário "referências extras para as fórmulas.md" se ele deveria compor bibliografia/legendas, ou confirmar que não afeta o PDF final. (Prioridade baixa até o autor indicar uso.)

Notas finais

- A verificação automatizada não detectou sinais tóxicos óbvios ("??", caracteres de substituição) — isso é bom. A fragilidade principal está na renderização/recorte de equações ao extrair texto (PDF→texto espreme quebras de linha e colunas), o que pode dar falsos positivos. Por isso as recomendações abaixo priorizam uma inspeção visual humana focada nas poucas equações/tabelas listadas acima.

- Se desejar, executo agora a varredura de reconciliação (item 3) e gero uma lista por número de equação mostrando se cada número aparece no texto extraído; isso facilita localizar discrepâncias numéricas precisas. Deseja seguir com essa conferência automática? 

— Fim do relatório automático (dicas_COPILOT.md)
