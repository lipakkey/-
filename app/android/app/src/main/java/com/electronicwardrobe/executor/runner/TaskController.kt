package com.electronicwardrobe.executor.runner

import android.content.Context
import com.electronicwardrobe.executor.env.EnvDiagnostics
import com.electronicwardrobe.executor.repository.TaskRepository
import com.electronicwardrobe.executor.storage.LogSink
import com.electronicwardrobe.executor.storage.ResultWriter
import com.electronicwardrobe.executor.util.Logger
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import java.io.File

class TaskController(private val context: Context) {
    private var isRunning = false
    private val scope = CoroutineScope(Dispatchers.Default)
    private val todoRoot = File("/sdcard/XianyuTasks/Todo")
    private val doneRoot = File("/sdcard/XianyuTasks/Done")
    private val logSink = LogSink(doneRoot)
    private val resultWriter = ResultWriter(doneRoot)
    private val repository = TaskRepository(todoRoot, resultWriter)
    private val envDiagnostics = EnvDiagnostics(context)
    private val runner = TaskRunner(
        repository = repository,
        writer = resultWriter,
        logSink = logSink,
        envDiagnostics = envDiagnostics,
        scheduler = ActionScheduler(),
    )

    fun start() {
        if (isRunning) return
        Logger.i("TaskController start")
        isRunning = true
        runner.start()
    }

    fun stop() {
        if (!isRunning) return
        Logger.i("TaskController stop")
        isRunning = false
        runner.stop()
    }
}
