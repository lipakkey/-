package com.electronicwardrobe.executor.storage

import com.electronicwardrobe.executor.model.ResultPayload
import com.electronicwardrobe.executor.util.Logger
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.io.File
import java.time.OffsetDateTime

class ResultWriter(
    private val doneRoot: File,
    private val json: Json = Json { prettyPrint = true },
) {
    fun markCompleted(
        styleCode: String,
        status: String,
        errorCode: String?,
        retryCount: Int,
        screenshots: List<String>,
        durationMs: Long,
    ) {
        val styleDir = File(doneRoot, styleCode).apply { mkdirs() }
        val resultFile = File(styleDir, "result.json")
        val payload = ResultPayload(
            style_code = styleCode,
            status = status,
            error_code = errorCode,
            retry_count = retryCount,
            published_at = OffsetDateTime.now().toString(),
            screenshots = screenshots,
            duration_ms = durationMs,
        )
        resultFile.writeText(json.encodeToString(payload))
        Logger.i("Result recorded for $styleCode -> $status")
    }

    fun isCompleted(styleCode: String): Boolean {
        return File(doneRoot, "$styleCode/result.json").exists()
    }
}
