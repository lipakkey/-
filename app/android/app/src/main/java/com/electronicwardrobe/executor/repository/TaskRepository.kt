package com.electronicwardrobe.executor.repository

import com.electronicwardrobe.executor.model.BatchManifest
import com.electronicwardrobe.executor.model.EntryMedia
import com.electronicwardrobe.executor.model.MacroDelay
import com.electronicwardrobe.executor.model.TaskEntry
import com.electronicwardrobe.executor.storage.ResultWriter
import com.electronicwardrobe.executor.util.Logger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.io.File

data class PendingTask(
    val manifest: BatchManifest,
    val entry: TaskEntry,
    private val todoRoot: File,
) {
    val styleCode: String
        get() = entry.styleCode

    private fun resolve(relative: String): File =
        File(todoRoot, relative.replace("/", File.separator))

    fun titleFile(): File = resolve(entry.paths.title)

    fun descriptionFiles(): List<File> = entry.paths.descriptions.map(::resolve)

    fun media(): EntryMedia = entry.media

    fun primaryImages(): List<File> = entry.media.primary.map(::resolve)

    fun variantImages(): Map<String, List<File>> =
        entry.media.variants.associate { variant ->
            variant.name to variant.images.map(::resolve)
        }

    fun mediaFiles(): List<File> = primaryImages() + variantImages().values.flatten()

    val price: Double
        get() = entry.pricing.price

    val stockPerVariant: Int?
        get() = entry.pricing.stockPerVariant

    val macroDelay: MacroDelay
        get() = entry.pricing.macroDelay
}

class TaskRepository(
    private val todoRoot: File,
    private val resultWriter: ResultWriter,
    private val json: Json = Json { ignoreUnknownKeys = true },
) {
    suspend fun loadNextTask(): PendingTask? = withContext(Dispatchers.IO) {
        val manifestFile = File(todoRoot, "batch_manifest.json")
        if (!manifestFile.exists()) {
            Logger.i("Manifest not found: ${manifestFile.absolutePath}")
            return@withContext null
        }

        val manifest = runCatching {
            json.decodeFromString<BatchManifest>(manifestFile.readText())
        }.onFailure {
            Logger.e("Failed to parse manifest", it)
        }.getOrNull() ?: return@withContext null

        val entry = manifest.entries.firstOrNull { task ->
            !resultWriter.isCompleted(task.styleCode)
        } ?: return@withContext null

        PendingTask(manifest, entry, todoRoot)
    }
}
