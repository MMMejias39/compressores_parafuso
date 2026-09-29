//! `sim_core` — Núcleo de simulação do Gêmeo Digital de Compressores de Parafuso.
//!
//! # Módulos
//! - [`constantes`] — constantes físicas e defaults
//! - [`nucleo`] — termodinâmica dos estágios e psicrometria
//! - [`subsistemas`] — intercooler, separador, PSA, vaso
//! - [`sistema`] — cascata completa (`simular`)
//! - [`psa_ciclo`] — ciclagem das torres do secador PSA
//! - [`dinamica`] — dinâmica temporal e modos de controle
//! - [`mpc`] — controle preditivo baseado em modelo
//! - [`pso`] — otimização por enxame de partículas
//! - [`ekf`] — filtro de Kalman estendido
//! - [`pi_telemetry`] — telemetria PI System e tags industriais
//! - [`frota`] — supervisório de frota offshore e RUL
//! - [`treinamento`] — diagnóstico e arena de treinamento de falhas

pub mod constantes;
pub mod nucleo;
pub mod subsistemas;
pub mod sistema;
pub mod psa_ciclo;
pub mod dinamica;
pub mod mpc;
pub mod pso;
pub mod ekf;
pub mod fadiga;
pub mod pi_telemetry;
pub mod frota;
pub mod treinamento;
pub mod calib_lm;

// Re-exportações de conveniência
pub use sistema::{simular, Params, ResultadoSistema};
pub use pso::otimizar as pso_otimizar;
pub use psa_ciclo::simular_ciclo_psa;
pub use dinamica::simular_transiente;
pub use mpc::simular_mpc;
pub use ekf::simular_ekf;
pub use calib_lm::{calibrar_parametros_lm, ResultadoCalibLm};
pub use pi_telemetry::{extrair_snapshot_pi, exportar_csv, SnapshotTag, TagPI};
pub use frota::{criar_frota_padrao_offshore, criar_frota_com_capacidade, executar_ciclo_supervisorio_frota, MaquinaFrota, PainelMaquina};
pub use treinamento::{gerar_caso_cego, avaliar_resposta, classificar_falha, CasoCego, MecanismoFalha};

