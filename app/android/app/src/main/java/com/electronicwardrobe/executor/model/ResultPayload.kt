package com.electronicwardrobe.executor.model

import kotlinx.serialization.Serializable

@Serializable
data class ResultPayload(
    val style_code: String,
    val status: String,
    val error_code: String?,
    val retry_count: Int,
    val published_at: String,
    val screenshots: List<String>,
    val duration_ms: Long,
)
