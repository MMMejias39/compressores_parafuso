//! Servidor Web Axum para o Gêmeo Digital de Compressores Offshore (Rust 2.0).
//!
//! Interface Web fiel à identidade visual industrial, parâmetros normativos
//! (API 619, ISO 1217, ISO 8573-1, ASME VIII) e fluxos operacionais completos.

use axum::{
    extract::{Query, State},
    http::Method,
    response::{Html, Json},
    routing::{get, post},
    Router,
};
use serde::Deserialize;
use std::sync::{Arc, Mutex};
use tower_http::cors::{Any, CorsLayer};

use sim_core::{
    avaliar_resposta, classificar_falha, criar_frota_padrao_offshore,
    executar_ciclo_supervisorio_frota, extrair_snapshot_pi, gerar_caso_cego,
    pso_otimizar, simular, simular_ciclo_psa, simular_ekf, simular_mpc,
    simular_transiente, CasoCego, MaquinaFrota, Params, ResultadoSistema,
};

#[derive(Clone)]
struct AppState {
    frota: Arc<Mutex<Vec<MaquinaFrota>>>,
}

// ---------------------------------------------------------------------------
// Assets embutidos no binário: a interface funciona sem internet (CDN externo
// proibido em ambiente offshore) e sem arquivos soltos ao lado do executável.
// ---------------------------------------------------------------------------
const APP_CSS: &[u8] = include_bytes!("../assets/app.css");
const CHART_JS: &[u8] = include_bytes!("../assets/chart.umd.min.js");
const CONJUNTO_PNG: &[u8] = include_bytes!("../assets/conjunto-pontos.png");
const CONJUNTO_PDF: &[u8] = include_bytes!("../assets/conjunto-pontos.pdf");
const CONJUNTO3D_PNG: &[u8] = include_bytes!("../assets/conjunto-3d.png");
const CONJUNTO3D_PDF: &[u8] = include_bytes!("../assets/conjunto-3d.pdf");
const CONJUNTO_SVG: &[u8] = include_bytes!("../assets/conjunto-pontos.svg");

const FAVICON_SVG: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="7" fill="#0e1626"/>
<circle cx="16" cy="16" r="9" fill="none" stroke="#4c8dff" stroke-width="2.2"/>
<circle cx="16" cy="16" r="3.4" fill="#22d3ee"/>
<path d="M16 7v3.2M16 21.8V25M7 16h3.2M21.8 16H25" stroke="#4c8dff" stroke-width="2.2" stroke-linecap="round"/>
</svg>"##;


#[tokio::main]
async fn main() {
    let frota = Arc::new(Mutex::new(criar_frota_padrao_offshore(4)));
    let state = AppState { frota };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any);

    let app = Router::new()
        .route("/", get(index_handler))
        .route("/assets/app.css", get(css_handler))
        .route("/assets/chart.umd.js", get(chart_handler))
        .route("/assets/conjunto-pontos.png", get(conjunto_png_handler))
        .route("/assets/conjunto-pontos.pdf", get(conjunto_pdf_handler))
        .route("/assets/conjunto-3d.png", get(conjunto3d_png_handler))
        .route("/assets/conjunto-3d.pdf", get(conjunto3d_pdf_handler))
        .route("/assets/conjunto-pontos.svg", get(conjunto_svg_handler))
        .route("/favicon.svg", get(favicon_handler))
        .route("/favicon.ico", get(|| async { axum::http::StatusCode::NO_CONTENT }))
        .route("/api/health", get(health_handler))
        .route("/api/simular", post(simular_handler))
        .route("/api/frota", get(frota_handler))
        .route("/api/pi/snapshot", get(pi_snapshot_handler))
        .route("/api/telemetria", post(telemetria_handler))
        .route("/api/treinamento/catalogo", get(treinamento_catalogo_handler))
        .route("/api/treinamento/caso", post(treinamento_caso_handler))
        .route("/api/treinamento/avaliar", post(treinamento_avaliar_handler))
        .route("/api/diagnostico/classificar", post(diagnostico_classificar_handler))
        .route("/api/psa/simular", post(psa_simular_handler))
        .route("/api/dinamica/simular", post(dinamica_simular_handler))
        .route("/api/mpc/simular", post(mpc_simular_handler))
        .route("/api/pso/otimizar", post(pso_otimizar_handler))
        .route("/api/ekf/simular", post(ekf_simular_handler))
        .layer(cors)
        .with_state(state);

    // Porta configurável: `PORT=8090 cargo run`. O padrão continua 8080.
    // A 8080 pode estar reservada pelo sistema (WSAEACCES) ou ocupada por
    // outro serviço; nesse caso a mensagem abaixo diz exatamente o que fazer.
    let porta = std::env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr = format!("0.0.0.0:{porta}");

    let listener = match tokio::net::TcpListener::bind(&addr).await {
        Ok(l) => l,
        Err(e) => {
            eprintln!("❌ Não foi possível abrir {addr}: {e}");
            eprintln!("   A porta pode estar reservada pelo sistema ou em uso.");
            eprintln!("   Escolha outra, por exemplo: PORT=8090 cargo run --bin compressor2");
            std::process::exit(1);
        }
    };

    println!("🚀 Digital Twin Compressores (Rust 2.0) rodando em http://localhost:{porta}");
    axum::serve(listener, app).await.unwrap();
}

async fn health_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "service": "Digital Twin Compressor2 (Rust Axum)",
        "version": "2.0.0"
    }))
}

async fn simular_handler(Json(params): Json<Params>) -> Json<ResultadoSistema> {
    let res = simular(&params);
    Json(res)
}

#[derive(Deserialize)]
struct FrotaQuery {
    n_compressores: Option<usize>,
    fad_unitario: Option<f64>,
}

async fn frota_handler(
    State(state): State<AppState>,
    Query(query): Query<FrotaQuery>,
) -> Json<serde_json::Value> {
    let mut frota = state.frota.lock().unwrap();
    if let Some(n) = query.n_compressores {
        let fad = query.fad_unitario.unwrap_or(10.0);
        let n_clamped = n.clamp(1, 16);
        if frota.len() != n_clamped || (frota.len() > 0 && (frota[0].params.fad_m3_min - fad).abs() > 1e-3) {
            *frota = sim_core::criar_frota_com_capacidade(n_clamped, fad);
        }
    }
    let painel = sim_core::executar_ciclo_supervisorio_frota(&mut frota, 1.0);
    Json(serde_json::json!({ "painel": painel }))
}

#[derive(Deserialize)]
struct SnapshotQuery {
    prefixo: Option<String>,
}

async fn pi_snapshot_handler(Query(query): Query<SnapshotQuery>) -> Json<serde_json::Value> {
    let prefixo = query.prefixo.unwrap_or_else(|| "CMP01".to_string());
    let params = Params::default();
    let res = simular(&params);
    let snap = extrair_snapshot_pi(&res, &params, &prefixo, true, Some(42));
    Json(serde_json::json!({ "snapshot": snap }))
}

#[derive(Deserialize)]
struct TelemetriaReq {
    params: Option<Params>,
    prefixo: Option<String>,
    seed: Option<u64>,
}

async fn telemetria_handler(Json(req): Json<TelemetriaReq>) -> Json<serde_json::Value> {
    let prefixo = req.prefixo.unwrap_or_else(|| "CMP01".to_string());
    let params = req.params.unwrap_or_default();
    let res = simular(&params);
    let seed = req.seed.unwrap_or(42);
    let snap = extrair_snapshot_pi(&res, &params, &prefixo, true, Some(seed));
    Json(serde_json::json!({ "snapshot": snap }))
}

async fn treinamento_catalogo_handler() -> Json<serde_json::Value> {
    let catalogo = sim_core::treinamento::catalogo_falhas();
    Json(serde_json::json!({ "catalogo": catalogo }))
}

#[derive(Deserialize)]
struct CasoReq {
    nivel: Option<String>,
    seed: Option<u64>,
}

async fn treinamento_caso_handler(Json(req): Json<CasoReq>) -> Json<CasoCego> {
    let nivel = req.nivel.unwrap_or_else(|| "Intermediario".to_string());
    let seed = req.seed.unwrap_or_else(|| rand::random());
    let caso = gerar_caso_cego(&nivel, seed);
    Json(caso)
}

#[derive(Deserialize)]
struct AvaliarReq {
    caso: CasoCego,
    mecanismo_id: String,
    severidade: f64,
    subsistema: String,
}

async fn treinamento_avaliar_handler(Json(req): Json<AvaliarReq>) -> Json<sim_core::treinamento::AvaliacaoResposta> {
    let aval = avaliar_resposta(&req.caso, &req.mecanismo_id, req.severidade, &req.subsistema);
    Json(aval)
}

#[derive(Deserialize)]
struct DiagnosticoReq {
    params_base: Option<Params>,
    resultado_observado: ResultadoSistema,
}

async fn diagnostico_classificar_handler(Json(req): Json<DiagnosticoReq>) -> Json<serde_json::Value> {
    let base = req.params_base.unwrap_or_default();
    let ranking = classificar_falha(&base, &req.resultado_observado);
    Json(serde_json::json!({ "ranking": ranking }))
}

#[derive(Deserialize)]
struct PsaReq {
    horizonte_min: Option<f64>,
    m_dot_ar: Option<f64>,
    n_vasos: Option<usize>,
    capacidade_trabalho: Option<f64>,
    massa_leito_kg: Option<f64>,
    t_ads_min: Option<f64>,
    t_regen_min: Option<f64>,
    t_resfriamento_min: Option<f64>,
}

async fn psa_simular_handler(Json(req): Json<PsaReq>) -> Json<sim_core::psa_ciclo::ResultadoPsaCiclo> {
    let res = simular_ciclo_psa(
        req.horizonte_min.unwrap_or(180.0),
        req.m_dot_ar.unwrap_or(0.20),
        req.t_ads_min.unwrap_or(60.0),
        req.t_regen_min.unwrap_or(45.0),
        req.t_resfriamento_min.unwrap_or(10.0),
        req.n_vasos.unwrap_or(2),
        1.5,
        1.0e5,
        8.0e5,
        0.15,
        30.0,
        80.0,
        15.0,
        req.capacidade_trabalho.unwrap_or(0.10),
        req.massa_leito_kg.unwrap_or(200.0),
        0.1,
    );
    Json(res)
}

#[derive(Deserialize)]
struct DinamicaReq {
    horizonte_min: Option<f64>,
    dt_s: Option<f64>,
    modo: Option<String>,
    dem_base: Option<f64>,
    dp_db_bar: Option<f64>,
    v_vaso: Option<f64>,
}

async fn dinamica_simular_handler(Json(req): Json<DinamicaReq>) -> Json<sim_core::dinamica::ResultadoTransiente> {
    let modo = req.modo.unwrap_or_else(|| "VSD".to_string());
    let dp_db = req.dp_db_bar.unwrap_or(0.5) * 1e5;
    let horiz = req.horizonte_min.unwrap_or(30.0).clamp(1.0, 300.0);
    let dt = req.dt_s.unwrap_or(0.5).clamp(0.05, 5.0);
    let v_vaso = req.v_vaso.unwrap_or(2.0).max(0.1);

    let res = simular_transiente(
        horiz,
        0.20,
        50_000.0,
        v_vaso,
        303.15,
        8.0e5,
        6.0e5,
        req.dem_base.unwrap_or(0.15),
        (horiz * 60.0 * 0.3, horiz * 60.0 * 0.6),
        1.35,
        &modo,
        dp_db,
        0.25,
        0.95,
        0.30,
        5.0,
        dt,
    );
    Json(res)
}

#[derive(Deserialize)]
struct MpcReq {
    horizonte_min: Option<f64>,
    dem_base: Option<f64>,
}

async fn mpc_simular_handler(Json(req): Json<MpcReq>) -> Json<sim_core::mpc::ResultadoMpc> {
    let res = simular_mpc(
        req.horizonte_min.unwrap_or(30.0),
        1.0,
        10,
        0.20,
        2.0,
        303.15,
        8.0e5,
        req.dem_base.unwrap_or(0.15),
        (10.0 * 60.0, 20.0 * 60.0),
        1.3,
        0.1,
        0.30,
        50_000.0,
        0.95,
    );
    Json(res)
}

#[derive(Deserialize)]
struct PsoReq {
    n_particulas: Option<usize>,
    n_iter: Option<usize>,
}

async fn pso_otimizar_handler(Json(req): Json<PsoReq>) -> Json<sim_core::pso::ResultadoPso> {
    let res = pso_otimizar(
        |x| {
            let mut p = Params::default();
            p.pi_total = x[0];
            let r = simular(&p);
            r.kpis.spc
        },
        &[6.0],
        &[10.0],
        req.n_particulas.unwrap_or(20),
        req.n_iter.unwrap_or(30),
        0.9,
        0.4,
        2.0,
        2.0,
        42,
    );
    Json(res)
}

#[derive(Deserialize)]
struct EkfReq {
    n_passos: Option<usize>,
}

async fn ekf_simular_handler(Json(req): Json<EkfReq>) -> Json<sim_core::ekf::ResultadoEkf> {
    let n = req.n_passos.unwrap_or(50);
    let folga_true: Vec<f64> = (0..n).map(|i| 0.002 + 0.007 * (i as f64 / (n - 1) as f64)).collect();
    let rf_true = vec![0.0; n];
    let params = Params::default();
    let res = simular_ekf(
        &params,
        &folga_true,
        &rf_true,
        1e-4,
        0.05,
        [1e-7, 1e-10],
        [0.002, 0.0],
        [1e-6, 1e-10],
        42,
    );
    Json(res)
}

async fn index_handler() -> Html<&'static str> {
    Html(include_str!("index.html"))
}

async fn css_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "text/css; charset=utf-8"),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        APP_CSS,
    )
}

async fn chart_handler() -> impl axum::response::IntoResponse {
    (
        [
            (
                axum::http::header::CONTENT_TYPE,
                "application/javascript; charset=utf-8",
            ),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        CHART_JS,
    )
}

async fn conjunto_png_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "image/png"),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        CONJUNTO_PNG,
    )
}

async fn conjunto_pdf_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "application/pdf"),
            (
                axum::http::header::CONTENT_DISPOSITION,
                "inline; filename=\"conjunto-pontos.pdf\"",
            ),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        CONJUNTO_PDF,
    )
}

async fn conjunto_svg_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "image/svg+xml"),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        CONJUNTO_SVG,
    )
}

async fn conjunto3d_png_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "image/png"),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        CONJUNTO3D_PNG,
    )
}

async fn conjunto3d_pdf_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "application/pdf"),
            (
                axum::http::header::CONTENT_DISPOSITION,
                "inline; filename=\"conjunto-3d.pdf\"",
            ),
            (axum::http::header::CACHE_CONTROL, "public, max-age=3600"),
        ],
        CONJUNTO3D_PDF,
    )
}

async fn favicon_handler() -> impl axum::response::IntoResponse {
    (
        [
            (axum::http::header::CONTENT_TYPE, "image/svg+xml"),
            (axum::http::header::CACHE_CONTROL, "public, max-age=86400"),
        ],
        FAVICON_SVG,
    )
}
