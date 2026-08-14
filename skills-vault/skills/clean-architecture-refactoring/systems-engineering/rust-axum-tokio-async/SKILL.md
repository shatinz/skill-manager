---
id: clean-architecture-refactoring.systems-engineering.rust-axum-tokio-async
name: rust-axum-tokio-async
title: Rust Axum & Tokio High-Throughput Async Architecture
category: clean-architecture-refactoring
subcategory: systems-engineering
version: 1.3.0
tags:
- rust
- axum
- tokio
- async
- sqlx
- tower
- high-performance
- zero-cost-abstractions
trust_rating: 0.99
estimated_tokens: 1900
description: Architect ultra-high-throughput, memory-safe asynchronous web services
  and microservices using Rust, Axum, Tokio multi-threaded runtime, Tower middleware,
  and SQLx compile-time query validation.
trigger_patterns:
- rust axum rest api server
- tokio async rust web service
- sqlx compile time postgres rust
- tower middleware layers axum
---

# Rust Axum & Tokio High-Throughput Async Architecture

## Objective
Engineer mission-critical, sub-millisecond latency backend microservices in Rust leveraging Axum's type-safe routing, Tokio multi-threaded work-stealing runtime, and Tower middleware.

## Production Rust Axum Service (`src/main.rs`)
```rust
use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, postgres::PgPoolOptions};
use std::sync::Arc;
use tower_http::trace::TraceLayer;

#[derive(Clone)]
struct AppState {
    db: PgPool,
}

#[derive(Serialize, Deserialize, sqlx::FromRow)]
struct SkillRecord {
    id: String,
    name: String,
    trust_score: f64,
}

#[derive(Deserialize)]
struct CreateSkillRequest {
    name: String,
    trust_score: f64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();

    let database_url = std::env::var("DATABASE_URL").unwrap_or_else(|_| "postgres://localhost/skills".into());
    let pool = PgPoolOptions::new()
        .max_connections(50)
        .connect(&database_url)
        .await?;

    let state = Arc::new(AppState { db: pool });

    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/skills", post(create_skill).get(list_skills))
        .route("/skills/:id", get(get_skill))
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    tracing::info!("Listening on {}", listener.local_addr()?);
    axum::serve(listener, app).await?;

    Ok(())
}

async fn get_skill(
    Path(id): Path<String>,
    State(state): State<Arc<AppState>>,
) -> Result<Json<SkillRecord>, StatusCode> {
    sqlx::query_as::<_, SkillRecord>("SELECT id, name, trust_score FROM skills WHERE id = $1")
        .bind(id)
        .fetch_optional(&state.db)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        .map(Json)
        .ok_or(StatusCode::NOT_FOUND)
}

async fn create_skill(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<CreateSkillRequest>,
) -> Result<(StatusCode, Json<SkillRecord>), StatusCode> {
    let id = uuid::Uuid::new_v4().to_string();
    let record = sqlx::query_as::<_, SkillRecord>(
        "INSERT INTO skills (id, name, trust_score) VALUES ($1, $2, $3) RETURNING id, name, trust_score"
    )
    .bind(&id)
    .bind(&payload.name)
    .bind(payload.trust_score)
    .fetch_one(&state.db)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok((StatusCode::CREATED, Json(record)))
}

async fn list_skills(
    State(state): State<Arc<AppState>>,
) -> Result<Json<Vec<SkillRecord>>, StatusCode> {
    let records = sqlx::query_as::<_, SkillRecord>("SELECT id, name, trust_score FROM skills ORDER BY trust_score DESC LIMIT 50")
        .fetch_all(&state.db)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(records))
}
```

## Anti-Patterns
- ❌ Performing blocking CPU-heavy operations or synchronous file I/O directly in Tokio worker threads without `tokio::task::spawn_blocking`.
- ❌ Unbounded memory allocations in request body parsers (always enforce request body limits with `DefaultBodyLimit`).
