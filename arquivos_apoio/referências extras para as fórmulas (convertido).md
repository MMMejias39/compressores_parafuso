# Referências extras para as fórmulas

> Convertido em 08/09/2026 a partir de `referências extras para as fórmulas.md`,
> que na verdade é um arquivo OpenDocument Text (.odt) com extensão `.md`
> (não era legível como Markdown — ver `dicas_COPILOT.md`, item E). O arquivo
> binário original foi preservado intacto; este é a versão em texto.
>
> **Estado de absorção (08/09/2026):** todas as referências listadas abaixo já
> constam da bibliografia do livro (`compressores.tex`) — `moran`, `hanlon`,
> `incropera`, `simon`, `rawlings`, `kingma`, `raissi`, `shigley` — e os
> respectivos capítulos já as citam. Nenhuma ação pendente; arquivo mantido
> como registro da origem do mapeamento equação → fonte.

As equações apresentadas ao longo do desenvolvimento do Gêmeo Digital derivam de
princípios fundamentais da termodinâmica, mecânica dos fluidos, teoria de
controle e aprendizado de máquina profundo. Abaixo estão as referências
específicas para cada grupo de fórmulas:

## 1. Termodinâmica e Performance (Estágio HP e Resfriamento)

- **Relações Politrópicas e Potência (T_out, Ẇ):**
  - Referência: MORAN, M. J.; SHAPIRO, H. N. *Fundamentals of Engineering
    Thermodynamics*. Capítulo 7 (Entropy Analysis) e Capítulo 9 (Gas Power
    Systems).
  - Equação: Derivada da definição de trabalho de fluxo para processos
    politrópicos reversíveis: w = ∫v dP.
- **Eficiência Volumétrica e Vazamento (η_v,HP):**
  - Referência: HANLON, P. C. *Compressor Handbook*. McGraw-Hill. Capítulo 5
    (Reciprocating Compressors) e Capítulo 6 (Rotary-Type Compressors).
  - Equação: Baseada na geometria de folga e na equação de Bernoulli para
    escoamento compressível através de orifícios.
- **Efetividade Térmica e Fouling (ε_ac, R_f):**
  - Referência: INCROPERA, F. P.; DEWITT, D. P. *Fundamentals of Heat and Mass
    Transfer*. Capítulo 11 (Heat Exchangers).
  - Equação: Método ε-NTU e a definição de resistência térmica global.

## 2. Estimação de Estados e Controle (EKF e MPC)

- **Filtro de Kalman Estendido (Predição e Correção):**
  - Referência: SIMON, D. *Optimal State Estimation: Kalman, H Infinity, and
    Nonlinear Approaches*. Wiley. Capítulo 13 (The Extended Kalman Filter).
  - Equação: Linearização por série de Taylor de primeira ordem das funções de
    transição f(x) e observação h(x).
- **Função de Custo do MPC (J):**
  - Referência: RAWLINGS, J. B.; MAYNE, D. Q.; DIEHL, M. *Model Predictive
    Control: Theory, Computation, and Design*. Capítulo 2 (Model Predictive
    Control).
  - Equação: Formulação quadrática padrão para rastreamento de referência com
    penalidade no esforço de controle.

## 3. Inteligência Artificial e Physics-ML (VAE e PINN)

- **Perda do Autoencoder Variacional (L_VAE):**
  - Referência: KINGMA, D. P.; WELLING, M. "Auto-Encoding Variational Bayes".
    arXiv:1312.6114, 2013.
  - Equação: Evidência do Limite Inferior (ELBO), combinando erro de
    reconstrução (MSE) e Divergência de Kullback-Leibler (D_KL).
- **Resíduo de Navier-Stokes e Perda PINN (L_PIML, R):**
  - Referência: RAISSI, M.; PERDIKARIS, P.; KARNIADAKIS, G. E. "Physics-informed
    neural networks". *Journal of Computational Physics*, 2019.
  - Equação: Derivada das leis de conservação de massa e quantidade de
    movimento (Navier-Stokes) e conservação de energia.

## 4. Mecânica e Integridade Estrutural

- **Tensão de Flexão e Sincronismo (σ_b, Δθ_sync):**
  - Referência: SHIGLEY, J. E.; MISCHKE, C. R. *Mechanical Engineering
    Design*. McGraw-Hill. Capítulo sobre engrenagens e eixos.
  - Equação: Fórmulas de Lewis para tensão em dentes de engrenagens e dinâmica
    de folga (*backlash*).
