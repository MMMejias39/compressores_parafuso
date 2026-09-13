# Plano de Melhorias Técnicas e Próximos Passos — Gêmeo Digital de Sistemas de Compressão Offshore

> **STATUS: MAJORITARIAMENTE VENCIDO — verificado em 13/09/2026.**
>
> Este plano foi escrito antes das sessões de 16/08/2026 em diante, que
> implementaram boa parte do que ele pede. Conferido item a item contra
> `compressores.tex` e o `aplicativo/`:
>
> **Já implementado (não reabrir):**
> - $\zeta_{valv}$ como coeficiente parametrizado de válvulas — Eq. 5.16 do
>   livro (10 ocorrências no `.tex`), vetor $\Lambda$ da Eq. 28.1 estendido de
>   3 para 4 elementos.
> - EKF com estado aumentado para identificação de parâmetro — Eqs. 28.1/28.2 e
>   `aplicativo/compressor_sim/ekf.py::simular_ekf_aumentado()`. **Ressalva
>   honesta:** só $K$ é de fato identificável; $\eta_{mec}$, $\zeta_{ref}$ e
>   $\zeta_{valv}$ exigiriam canais de medição que nem o EKF nem a Tabela 18.1
>   têm hoje.
> - Classificador automático multi-mecanismo $\hat{m}_{falha}$ — Eq. 29.2 e
>   `compressor_sim/treinamento_falhas.py`.
> - Supervisório contínuo de frota — Cap. 26 (`ciclo_supervisorio`),
>   `compressor_sim/frota_supervisorio.py` e `compressor2/crates/sim_core/src/frota.rs`.
> - Soft-sensor de vazão de água $\dot m_w$ — Eq. 12.8 (5 ocorrências).
> - Balanceamento adaptativo de $\lambda$ no PIML — Eq. 23.4, implementado de
>   fato via `torch.autograd.grad`.
> - Problema inverso via PINN — Cap. 23.8, Eq. 23.5,
>   `piml.py::treinar_com_identificacao()`.
> - Teste NIS $\chi^2$ para auditoria do filtro — Eq. 21.7, nos dois apps.
>
> **Ainda válido:**
> - Toda a **Seção 2 (calibração experimental)** — isotermas de adsorção,
>   $k_{ads,ref}$, esfericidade real, coeficientes de Vogel, curvas S-N,
>   condutâncias térmicas. Depende de bancada e de dados de campo, não de
>   edição. O `k_ads_ref` continua explicitamente não verificado (registrado
>   como tal no código, na UI e na Tabela 15.2 do livro).
> - **Análise de sensibilidade de Sobol/Morris** — 0 ocorrências no `.tex`.
> - **UKF ou MHE substituindo o EKF** — o MHE ganhou subseção (Cap. 27.4,
>   `do-mpc`), mas segue sem equacionamento próprio; UKF não é mencionado.
> - **Instrumentação nova** (ΔP de válvula, medição trifásica contínua, anel de
>   aterramento instrumentado, vazão de água) — é justamente o que destrava os
>   três parâmetros de $\Lambda$ ainda não identificáveis. Depende de hardware.
> - **MLOps/persistência** (InfluxDB/TimescaleDB, MLflow/DVC, deriva de modelo)
>   e o **dataset sintético multi-falha** $\mathcal{D}_{multi}$ — nenhum
>   iniciado.

Este documento consolida as lacunas técnicas identificadas, os parâmetros que demandam calibração experimental, os aprimoramentos nos algoritmos e a infraestrutura necessária para a evolução do Gêmeo Digital.

---

## 1\. Lacunas de Instrumentação e Sensoriamento (Hardware e Observabilidade)

* **Monitoramento Diferencial em Válvulas ($\\Delta P\_{valv}$):** O modelo parametriza a degradação progressiva em válvulas de retenção (*check valves*), *blow-off* e PSVs via coeficiente de perda localizada $\\zeta\_{valv}$ (Eq. 5.16). Para torná-lo observável pelo EKF aumentado (Seção 28.1), é necessário especificar e instalar transmissores de pressão diferencial dedicados nesses elementos.  
* **Medição Trifásica e Assimetria Elétrica:** Integrar a aquisição contínua de tensão e corrente por fase ($V\_{L,1}, V\_{L,2}, V\_{L,3}$ e $I\_1, I\_2, I\_3$) junto às temperaturas individuais de enrolamento ($T\_1, T\_2, T\_3$) no pipeline de telemetria, viabilizando o cálculo online dos índices $VU$, $IU$ e $\\Delta T\_{fases}$ (Eq. 4.8).  
* **Monitoramento de Descargas Eletrostáticas (EDM):** Instalar anel de aterramento de eixo instrumentado (*shaft grounding probe*) com canal de medição de picos de corrente/tensão para validar em campo o modelo de divisor capacitivo e rigidez dielétrica do filme de óleo (Eq. 4.13).  
* **Validação de Vazão de Água de Resfriamento:** Implementar medidores de vazão mássica ou ultrassônicos portáteis nos circuitos de água do *intercooler*, *aftercooler* e resfriador de óleo para validação cruzada do *soft-sensor* de vazão de água $\\dot{m}\_w$ (Eq. 12.8).

---

## 2\. Parâmetros que Exigem Calibração Experimental e Dados de Campo (Categoria iv)

* **Propriedades dos Leitos Dessecantes (Tabela 15.1):**  
  * Obter isotermas reais de adsorção em baixa umidade relativa para Sílica Gel e Peneira Molecular 13X em condições de processo.  
  * Medir experimentalmente as taxas cinéticas de adsorção ($k\_{ads,ref}$) e constantes de regeneração ($\\kappa\_{regen}$).  
  * Levantar a esfericidade real ($\\psi\_p$) e porosidade ($\\varepsilon\_{leito}$) dos lotes de dessecante para calibração da Equação de Ergun (Eq. 15.16).  
* **Condutâncias Térmicas e Coeficientes Convectivos:**  
  * Determinar experimentalmente as condutâncias de convecção natural ($G\_{ext}$) e forçada ($G\_{arref}$) da carcaça do elemento compressor dentro do *canopy* acústico ($T\_{hood}$, Eq. 2.4).  
  * Calibrar as correlações de convecção interna gás-rotor ($h\_r$) e taxa de condução axial pelo eixo para os mancais ($\\dot{Q}\_{cond,eixo}$, Eq. 9.18).  
* **Reologia de Óleo e Perda em Filtros:**  
  * Levantar em bancada os coeficientes de Vogel ($a, b, c$) para o lubrificante em diferentes estágios de oxidação/envelhecimento (TAN elevado).  
  * Determinar os coeficientes de permeabilidade e inércia ($A, B$) de Darcy-Forchheimer para os elementos filtrantes de óleo novos e saturados (Eq. 7.3).  
* **Mecânica e Dinâmica Estrutural:**  
  * Obter do fabricante ou por ensaio as curvas S-N reais (coeficiente $C$ e expoente de Basquin $b\_f$, Eq. 19.8) para o aço das engrenagens da *gearbox*.  
  * Levantar a rigidez torcional equivalente real ($k\_{t,eq}$) e momentos de inércia ($I\_1, I\_2$) do conjunto acoplamento-eixos para calibrar a frequência natural de torção (Eq. 8.10).

---

## 3\. Aprimoramentos Matemáticos e Algorítmicos

* **Evolução do Algoritmo de Estimação de Estado:**  
  * Substituir a linearização por Jacobianos do EKF por **Filtro de Kalman Unscented (UKF)** ou **Estimação de Horizonte Móvel (MHE)** para tratar as não linearidades severas de chaveamento das torres PSA e regimes de escoamento bloqueado (*choked flow*).  
  * Expandir a implementação do EKF aumentado para incluir simultaneamente todos os parâmetros $\\Lambda \= \[K, \\eta\_{mec}, \\zeta\_{ref}, \\zeta\_{valv}\]^T$ (Eq. 28.1).  
* **Generalização do Treinamento PIML:**  
  * Implementar o balanceamento adaptativo de gradientes ($\\lambda^{(t)}$, Eq. 23.4) com ponderação individual para os resíduos de massa ($\\mathcal{F}\_1$), energia ($\\mathcal{F}\_2$) e entropia ($\\mathcal{F}\_3$).  
  * Utilizar a formulação de problema inverso (Eq. 23.5) para estimar distribuições espaciais de parâmetros via *DeepXDE*.  
* **Classificador Automático Multi-Mecanismo:**  
  * Implementar o algoritmo de busca por resíduo mínimo ponderado ($\\hat{m}\_{falha}$, Eq. 29.2) sobre o catálogo de falhas $\\mathcal{M}$ (Tabela 28.2), eliminando a necessidade de seleção manual de hipóteses.  
* **Garantia de Viabilidade e Robustez no MPC:**  
  * Sintonizar as penalidades de variáveis de folga ($\\varrho\_s$, Eq. 24.2) para assegurar convergência determinística do algoritmo de controle ótimo em computadores de borda (*Edge IPCs*).  
  * Realizar análises formais de sensibilidade paramétrica (método de Sobol ou Morris) nas variáveis da Categoria (iv) que impactam as restrições duras ($\\sigma\_b \\le \\sigma\_{adm}$).

---

## 4\. Arquitetura de Software, MLOps e Operação de Frota

* **Geração de Base de Dados Sintética Multi-Falha ($\\mathcal{D}\_{multi}$):** Desenvolver script de varredura paramétrica automatizada sobre o modelo direto da Parte I para simular combinações de severidade e pontos de operação para os 59 mecanismos catalogados.  
* **Mecanismo de Supervisão Contínua de Frota:** Evoluir o código-fonte (atualmente focado em execuções pontuais de uma máquina) para um laço contínuo de supervisão de frota (`ciclo_supervisorio`, Seção 26.6), persistindo séries temporais em banco de dados dedicado (*InfluxDB/TimescaleDB*).  
* **Pipeline de MLOps e Detecção de Deriva (*Model Drift*):**  
  * Estruturar rotina periódica de auditoria do filtro via teste estatístico $NIS \\sim \\chi^2\_{n\_z}$ (Eq. 21.7).  
  * Automatizar a triagem de dados de operação saudável usando *Isolation Forest* (Eq. 25.2) antes de disparar o retreinamento do VAE.  
  * Versionamento conjunto de pesos, dados de calibração e topologia física (*MLflow / DVC*).

---

## 5\. Roteiro de Execução Técnica (Próximos Passos)

| Fase | Ação Técnica Prioritária | Entregável / Validação |
| :---- | :---- | :---- |
| **1\. Calibração** | Ensaios laboratoriais e de bancada para parâmetros de dessecantes, óleos e condutâncias térmicas. | Tabela consolidada de parâmetros com incertezas calibradas (eliminação da Categoria iv). |
| **2\. Algoritmos** | Codificação do EKF aumentado multivariável e implementação da busca por resíduo mínimo $\\hat{m}\_{falha}$ (Eq. 29.2). | Módulo de diagnóstico capaz de classificar falhas a partir do catálogo completo. |
| **3\. Simulação** | Geração do dataset sintético $\\mathcal{D}\_{multi}$ e treinamento dos modelos substitutos (*surrogates*) em *NVIDIA Modulus*. | Redução do tempo de avaliação física para milissegundos, viabilizando o MPC em tempo real. |
| **4\. Borda / Edge** | Embarque do pipeline (Pré-processamento $\\rightarrow$ EKF/VAE $\\rightarrow$ MPC) em hardware industrial local com integração MQTT/PI Web API. | Teste de latência e determinismo de ciclo ($\< 100\\text{ ms}$) sob contingências de rede offshore. |
| **5\. Supervisório** | Implementação do painel de monitoramento de frota com ordenação por urgência de $HI$, $NIS$ e alarmes ISA. | Dashboard operacional com exibição de RUL probabilístico por ativo. |

