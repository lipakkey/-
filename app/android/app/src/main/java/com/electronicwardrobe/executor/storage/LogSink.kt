package com.electronicwardrobe.executor.storage

import com.electronicwardrobe.executor.util.Logger
import java.io.File
import java.time.OffsetDateTime

class LogSink(private val root: File) {
    private val sessionFile: File = File(root, "session.log").apply { parentFile?.mkdirs() }

    fun info(message: String) {
        write("INFO", message)
    }

    fun error(message: String) {
        write("ERROR", message)
    }

    fun warn(message: String) {
        write("WARN", message)
    }

    private fun write(level: String, message: String) {
        Logger.i("LogSink[$level] $message")
        val line = "[${OffsetDateTime.now()}][$level] $message\n"
        sessionFile.appendText(line)
    }
}
