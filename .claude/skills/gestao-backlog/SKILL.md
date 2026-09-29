---
name: gestao-backlog
description: Metodologia genérica para levantar, priorizar e fechar itens de backlog (livro, código, qualquer artefato) com verificação-antes-de-listar — template de item com par "Gap/Verificação", critério de criticidade, anti-padrões e rotina de fim de sessão. Carregar ANTES de escrever um item novo de backlog, revisar um backlog existente, ou decidir se algo "pendente" ainda está pendente.
---

# Gestão de backlog verificável

Extraída da experiência de um projeto que já pagou caro por dois defeitos de
processo recorrentes: **status congelado** (um relatório descreve bem o dia em
que foi escrito e a linha "pendente" envelhece sem ninguém notar) e **achado
de revisor externo tratado como escopo fechado** sem verificar a causa (ver
skill irmã `calibracao-revisor-externo`). As regras abaixo valem para
qualquer tipo de backlog — texto, código, infraestrutura — não só o domínio
de origem.

## 1. Princípios gerais

1. **Verificar antes de listar.** Nenhum item entra no backlog por lembrança
   de registro anterior — toda lacuna vem de um comando (`grep`, contagem,
   execução) rodado *nesta* sessão. Reler um relatório antigo e assumir que
   o estado nele descrito continua válido é o erro mais caro e mais fácil de
   cometer.
2. **Criticidade ≠ ordem de descoberta.** Priorizar pelo que bloqueia ou
   degrada o consumo do artefato pelo usuário final — não pela ordem em que
   o item foi encontrado. Cada item deve citar o ponto exato downstream que
   depende dele (o capítulo seguinte que pressupõe o conteúdo, a função que
   chama o código faltante).
3. **Item sem verificação não é item.** Cada item traz o comando que confirma
   que ele ainda está aberto, para que a próxima sessão (ou você mesmo, mais
   tarde) reconfirme em segundos sem reler todo o histórico.
4. **Fechar o item no arquivo de origem.** Ao implementar, atualizar o status
   *onde o item nasceu* — nunca só num changelog/contexto separado, sob pena
   de as duas fontes divergirem.
5. **Separar item executável de decisão em aberto.** "Implementar se
   possível" ou "avaliar viabilidade" não é um item de backlog — ou vira uma
   decisão fechada com o responsável, ou vai para uma lista de
   escopo/observação claramente distinta.
6. **Não reabrir o que foi encerrado por decisão deliberada.** Um item
   recusado com justificativa registrada fica recusado até alguém com
   autoridade sobre o escopo levantar o assunto de novo — reabrir sozinho é
   desperdício e mina a confiança no registro.

## 2. Template de item

```markdown
### <ID> — <título curto>
- **Onde é exigido:** <arquivo:linha / módulo / seção>, o ponto exato onde o
  artefato é consumido (não necessariamente onde o item nasceu).
- **Gap (evidência de hoje):** comando + resultado. Ex.:
  `grep -c "X" arquivo` → 0.
- **Ação:** o que entra, em que ponto, respeitando as convenções do projeto.
- **Verificação:** os comandos/testes que provam que o item foi resolvido.
- **Prioridade:** nível + justificativa em uma linha.
- **Status:** pendente | em andamento | implementado (data, referência).
```

A diferença entre um item bom e um mau é o par **"Gap" × "Verificação"**: o
primeiro prova que o item existe hoje, o segundo prova que ele deixou de
existir amanhã. Um item sem os dois é uma frase solta, não um item de
backlog.

## 3. Critério de prioridade (adaptar os rótulos ao projeto, manter a lógica)

- **P1 — bloqueia o consumo downstream.** Alguém depende do artefato sem que
  ele tenha sido entregue.
- **P2 — formalismo/vocabulário usado explicitamente** adiante, sem ter sido
  definido.
- **P3 — acabamento e didática** (documentação, exemplos, polimento).
- **P4 — cosmético ou decisão de quem é dono do projeto.**

**Conformidade precede conteúdo novo.** Defeitos de convenção (estilo,
formatação, referência quebrada) entram antes de funcionalidade nova — corrige
o mesmo defeito uma vez em vez de duas.

## 4. Anti-padrões — o que já custou tempo

1. Item sem comando de verificação — impossível de reconferir sem reler tudo.
2. Item vindo de revisor externo sem checagem na fonte primária (ver skill
   `calibracao-revisor-externo`).
3. Implementar primeiro e verificar o achado depois — sempre na ordem
   inversa: verificar, só então implementar.
4. Reabrir item encerrado por decisão deliberada.
5. Duplicar item que já está registrado como pendente, sem conferir o estado
   atual por verificação direta.
6. "Implementar se possível" sem decisão — vira status congelado na sessão
   seguinte.
7. Reescrever entradas antigas de um registro cronológico (changelog,
   contexto) em vez de sempre acrescentar — o registro é a ferramenta de
   auditoria do projeto; editar o passado destrói essa função.
8. Declarar um item pronto sem rodar a verificação que o próprio item define.

## 5. Rotina barata de fim de sessão

- Rodar as varreduras/testes aplicáveis ao que foi editado nesta sessão.
- Comparar contagens relevantes contra um baseline registrado (testes
  passando, warnings, métricas do projeto) — qualquer regressão nova é
  regressão até provado o contrário.
- Atualizar o status dos itens tocados nos arquivos de origem.
- Deixar o estado do repositório limpo ou explicado (nada persistido sem
  pedido explícito, se essa for a convenção do projeto).

## 6. Exemplo aplicado

```markdown
### BK-14 — <nome do gap>
- **Onde é exigido:** módulo Y depende da função X, que promete um
  comportamento nunca implementado.
- **Gap (evidência):** `grep -ci "comportamento" modulo.py` → 0.
- **Ação:** implementar a função no módulo indicado, seguindo o padrão das
  vizinhas já existentes.
- **Verificação:** teste novo cobrindo o caso; suíte completa verde.
- **Prioridade:** P2 — usado explicitamente pelo módulo Y, sem alternativa.
- **Status:** pendente.
```
