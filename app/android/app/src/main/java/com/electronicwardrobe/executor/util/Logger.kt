package com.electronicwardrobe.executor.util

import android.content.Context
import android.util.Log
import java.io.File
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object Logger {
    private const val TAG = "Executor"
    private lateinit var logDir: File
    private val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

    fun init(context: Context) {
        logDir = File(context.getExternalFilesDir(null), "logs").apply { mkdirs() }
        i("Logger initialized")
    }

    fun i(message: String) {
        Log.i(TAG, message)
        write("INFO", message)
    }

    fun w(message: String) {
        Log.w(TAG, message)
        write("WARN", message)
    }

    fun e(message: String, throwable: Throwable? = null) {
        Log.e(TAG, message, throwable)
        write("ERROR", buildString {
            append(message)
            throwable?.let {
                append(" :: ")
                append(it.localizedMessage)
            }
        })
    }

    private fun write(level: String, message: String) {
        if (!::logDir.isInitialized) return
        val now = LocalDateTime.now().format(formatter)
        val file = File(logDir, "session.log")
        file.appendText("[$now][$level] $message\n")
    }
}
