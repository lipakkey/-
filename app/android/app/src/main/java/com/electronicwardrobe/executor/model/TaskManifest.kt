package com.electronicwardrobe.executor.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class BatchManifest(
    @SerialName("device_id")
    val deviceId: String,
    @SerialName("batch_id")
    val batchId: String,
    @SerialName("generated_at")
    val generatedAt: String? = null,
    val entries: List<ManifestEntry>,
)

@Serializable
data class ManifestEntry(
    @SerialName("style_code")
    val styleCode: String,
    val paths: EntryPaths,
    val media: EntryMedia,
    val pricing: EntryPricing,
    val flags: EntryFlags? = null,
)

@Serializable
data class EntryPaths(
    val root: String,
    val title: String,
    val descriptions: List<String>,
    val meta: String? = null,
)

@Serializable
data class EntryMedia(
    val primary: List<String>,
    val variants: List<MediaVariant>,
)

@Serializable
data class MediaVariant(
    val name: String,
    val images: List<String>,
)

@Serializable
data class EntryPricing(
    val price: Double,
    @SerialName("stock_per_variant")
    val stockPerVariant: Int? = null,
    @SerialName("macro_delay")
    val macroDelay: MacroDelay,
)

@Serializable
data class MacroDelay(
    val min: Int,
    val max: Int,
)

@Serializable
data class EntryFlags(
    @SerialName("sensitive_hits")
    val sensitiveHits: List<String>? = null,
    @SerialName("needs_manual_review")
    val needsManualReview: Boolean? = null,
)
