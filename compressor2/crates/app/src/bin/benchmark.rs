use std::time::Instant;
use sim_core::{
    simular, simular_transiente, simular_ekf, pso_otimizar,
    criar_frota_padrao_offshore, executar_ciclo_supervisorio_frota, Params
};

fn bench_sistema_estatico(n_iter: usize) -> (f64, f64) {
    let p = Params::default();
    // Warmup
    for _ in 0..100 {
        let _ = simular(&p);
    }
    let t0 = Instant::now();
    let mut w_tot = 0.0;
    for _ in 0..n_iter {
        let res = simular(&p);
        w_tot = res.potencias.w_total;
    }
    let elap = t0.elapsed();
    let dt_us = (elap.as_secs_f64() / n_iter as f64) * 1e6;
    (dt_us, w_tot / 1000.0)
}

fn bench_dinamica_transiente(n_iter: usize) -> (f64, f64) {
    // Warmup
    for _ in 0..10 {
        let _ = simular_transiente(
            30.0, 0.20, 50_000.0, 2.0, 303.15, 8.0e5, 6.0e5, 0.15,
            (540.0, 1080.0), 1.35, "VSD", 0.5e5, 0.25, 0.95, 0.30, 5.0, 0.5
        );
    }
    let t0 = Instant::now();
    let mut energia = 0.0;
    for _ in 0..n_iter {
        let res = simular_transiente(
            30.0, 0.20, 50_000.0, 2.0, 303.15, 8.0e5, 6.0e5, 0.15,
            (540.0, 1080.0), 1.35, "VSD", 0.5e5, 0.25, 0.95, 0.30, 5.0, 0.5
        );
        energia = res.kpis.energia_kwh;
    }
    let elap = t0.elapsed();
    let dt_ms = (elap.as_secs_f64() / n_iter as f64) * 1e3;
    (dt_ms, energia)
}

fn bench_ekf(n_iter: usize) -> f64 {
    let p = Params::default();
    let folga_true: Vec<f64> = (0..50).map(|i| 0.002 + (0.008 - 0.002) * (i as f64 / 49.0)).collect();
    let rf_true: Vec<f64> = (0..50).map(|i| 0.0001 + (0.0008 - 0.0001) * (i as f64 / 49.0)).collect();
    // Warmup
    for _ in 0..10 {
        let _ = simular_ekf(&p, &folga_true, &rf_true, 0.005, 0.5, [1e-6, 1e-8], [0.002, 0.0001], [1e-4, 1e-6], 42);
    }
    let t0 = Instant::now();
    for _ in 0..n_iter {
        let _ = simular_ekf(&p, &folga_true, &rf_true, 0.005, 0.5, [1e-6, 1e-8], [0.002, 0.0001], [1e-4, 1e-6], 42);
    }
    let elap = t0.elapsed();
    (elap.as_secs_f64() / n_iter as f64) * 1e3
}

fn bench_pso(n_iter: usize) -> f64 {
    let custo = |x: &[f64]| -> f64 { (x[0] - 6.5).powi(2) + 6.2 };
    // Warmup
    for _ in 0..5 {
        let _ = pso_otimizar(custo, &[4.0], &[12.0], 20, 30, 0.9, 0.4, 2.0, 2.0, 42);
    }
    let t0 = Instant::now();
    for _ in 0..n_iter {
        let _ = pso_otimizar(custo, &[4.0], &[12.0], 20, 30, 0.9, 0.4, 2.0, 2.0, 42);
    }
    let elap = t0.elapsed();
    (elap.as_secs_f64() / n_iter as f64) * 1e3
}

fn bench_frota(n_iter: usize) -> f64 {
    let mut frota = criar_frota_padrao_offshore(4);
    // Warmup
    for _ in 0..10 {
        let _ = executar_ciclo_supervisorio_frota(&mut frota, 1.0);
    }
    let t0 = Instant::now();
    for _ in 0..n_iter {
        let _ = executar_ciclo_supervisorio_frota(&mut frota, 1.0);
    }
    let elap = t0.elapsed();
    (elap.as_secs_f64() / n_iter as f64) * 1e3
}

fn main() {
    println!("=== BENCHMARK RUST (Release/Optimized) ===");
    let (us_est, w_tot) = bench_sistema_estatico(10_000);
    println!("1. Balanço Estático (7 Nós): {:.3} µs/chamada ({:.0} ops/s) | W_tot={:.2} kW", us_est, 1e6 / us_est, w_tot);

    let (ms_din, energia) = bench_dinamica_transiente(1_000);
    println!("2. Dinâmica Transiente (3.600 passos): {:.3} ms/chamada ({:.0} ops/s) | Energia={:.2} kWh", ms_din, 1e3 / ms_din, energia);

    let ms_ekf = bench_ekf(500);
    println!("3. Filtro de Kalman EKF (50 passos): {:.3} ms/chamada ({:.0} ops/s)", ms_ekf, 1e3 / ms_ekf);

    let ms_pso = bench_pso(500);
    println!("4. Otimização Global PSO (600 evals): {:.3} ms/chamada ({:.0} ops/s)", ms_pso, 1e3 / ms_pso);

    let ms_frota = bench_frota(500);
    println!("5. Supervisório de Frota (4 ativos + PI): {:.3} ms/chamada ({:.0} ops/s)", ms_frota, 1e3 / ms_frota);
}
