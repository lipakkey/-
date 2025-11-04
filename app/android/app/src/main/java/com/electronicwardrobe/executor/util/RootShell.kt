package com.electronicwardrobe.executor.util

import java.io.BufferedReader
import java.io.InputStreamReader

object RootShell {
    fun move(source: String, target: String): Boolean {
        return run(arrayOf("su", "-c", "mv \"\" \"\""))
    }

    fun copy(source: String, target: String): Boolean {
        return run(arrayOf("su", "-c", "cp \"\" \"\""))
    }

    fun chmod(path: String, mode: String): Boolean {
        return run(arrayOf("su", "-c", "chmod  \"\""))
    }

    fun mkdir(path: String): Boolean {
        return run(arrayOf("su", "-c", "mkdir -p \"\""))
    }

    fun screencap(target: String): Boolean {
        return run(arrayOf("su", "-c", "screencap -p \"\""))
    }

    private fun run(cmd: Array<String>): Boolean {
        return runCatching {
            val process = Runtime.getRuntime().exec(cmd)
            val exit = process.waitFor()
            if (exit != 0) {
                BufferedReader(InputStreamReader(process.errorStream)).use { reader ->
                    Logger.e("RootShell error: ")
                }
            }
            exit == 0
        }.onFailure {
            Logger.e("RootShell exec failed", it)
        }.getOrDefault(false)
    }
}
