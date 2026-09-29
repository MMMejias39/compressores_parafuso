---
name: calibracao-revisor-externo
description: Como tratar achados de um revisor externo (outra IA, outra pessoa, ferramenta de lint/análise) antes de aceitá-los como escopo — verificar a causa na fonte primária, não só confirmar o sintoma. Carregar ANTES de transformar um relatório de revisão externa em item de backlog ou em mudança de código/texto.
---

# Calibração de revisor externo

Um revisor externo (outro modelo de IA, outra pessoa, uma ferramenta
automática) é um **ponto de partida**, nunca um **escopo fechado**. A
diferença entre os dois é uma verificação na fonte primária antes de agir.

## Regra central

**Verificar a causa, não só o sintoma — e verificar antes de implementar,
nunca depois.** Um revisor pode acertar que existe um problema e errar
completamente por que ele existe; implementar a correção proposta sem
reconferir a causa propaga o erro do revisor para dentro do artefato.

## O que cada padrão de erro de revisor parece, na prática

Calibrar expectativa por tipo de revisor ajuda a saber onde gastar a
verificação com mais cuidado:

- **Acerta o sintoma, erra a causa.** O revisor aponta corretamente que algo
  está errado, mas a explicação/correção proposta ataca o problema errado.
  Aceitar a correção sem investigar a causa real resolve o sintoma
  superficialmente e deixa o defeito de fundo intacto (ou pior, mascarado).
- **Subestima a extensão.** O revisor encontra uma instância real de um
  problema, mas não uma varredura sistemática — há mais instâncias do mesmo
  problema em outros lugares que ele não cobriu. Tratar o achado como "1
  ocorrência corrigida, fechado" sem rodar a própria varredura sistemática
  deixa o resto do problema pendente sem ninguém perceber.
- **Falso positivo.** O revisor aponta um problema que não existe — geralmente
  por não ter acesso ao contexto completo (uma convenção do projeto, uma
  decisão deliberada anterior, uma diferença de versão). Confirmar na fonte
  primária antes de "corrigir" algo que já estava certo.
- **Confirma achados normativos/factuais.** Quando o achado é sobre uma norma,
  especificação ou fato externo verificável, um revisor que cita a fonte
  primária correta é o caso mais confiável — mas ainda vale conferir a
  citação, não só confiar no nome da norma.

## Processo

1. **Nunca implementar direto da palavra do revisor.** Ler o achado como uma
   hipótese, não como um fato.
2. **Reproduzir o sintoma você mesmo** — rodar o mesmo comando, ler o mesmo
   trecho, reproduzir o mesmo comportamento — antes de aceitar que ele existe.
3. **Perguntar "por quê" uma vez a mais do que o revisor perguntou.** Se o
   revisor parou no sintoma, continue até a causa raiz verificável.
4. **Rodar uma varredura sistemática da mesma classe de defeito**, não só
   corrigir a instância apontada — a extensão real quase sempre difere da
   relatada.
5. **Registrar a calibração**, não só o achado: o que o revisor acertou, o
   que errou, e por quê — isso constrói um histórico de quanto confiar em
   cada fonte de revisão ao longo do projeto (ver skill irmã
   `gestao-backlog`, item "achado de revisor externo sem checagem na fonte"
   na lista de anti-padrões).
6. **Só então vira item de backlog** — com o template da skill
   `gestao-backlog` (par Gap/Verificação), nunca como a frase original do
   revisor copiada e colada.

## Anti-padrão a evitar

Tratar "um revisor apontou X" como equivalente a "X é verdade e está
priorizado" — pula direto a etapa de implementação e pula a única etapa que
realmente protege a qualidade do artefato: a verificação independente na
fonte primária.
