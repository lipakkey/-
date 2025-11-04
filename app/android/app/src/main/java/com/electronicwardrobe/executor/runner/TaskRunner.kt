package com.electronicwardrobe.executor.runner

import android.view.accessibility.AccessibilityEvent
import com.electronicwardrobe.executor.accessibility.AccessibilityBridge
import com.electronicwardrobe.executor.accessibility.AccessibilityListener
import com.electronicwardrobe.executor.accessibility.AutomationAccessibilityService
import com.electronicwardrobe.executor.env.EnvDiagnostics
import com.electronicwardrobe.executor.repository.PendingTask
import com.electronicwardrobe.executor.repository.TaskRepository
import com.electronicwardrobe.executor.storage.LogSink
import com.electronicwardrobe.executor.storage.ResultWriter
import com.electronicwardrobe.executor.util.Logger
import com.electronicwardrobe.executor.util.RootShell
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

private const val MAX_RETRY = 2

class TaskRunner(
    private val repository: TaskRepository,
    private val writer: ResultWriter,
    private val logSink: LogSink,
    private val envDiagnostics: EnvDiagnostics,
    private val scheduler: ActionScheduler = ActionScheduler(),
    private val accessibility: AccessibilityBridge = AccessibilityBridge(),
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Default),
) : AccessibilityListener {

    private val machine = TaskStateMachine()
    private var job: Job? = null

    fun start() {
        if (job?.isActive == true) return
        AutomationAccessibilityService.registerListener(this)
        job = scope.launch { loop() }
    }

    fun stop() {
        job?.cancel()
        job = null
        AutomationAccessibilityService.unregisterListener(this)
    }

    private suspend fun loop() {
        while (job?.isActive == true) {
            logSink.info("开始环境检查")
            machine.moveTo(TaskState.EnvCheck)
            val report = envDiagnostics.runChecks()
            if (!report.isHealthy) {
                logSink.warn("环境异常：${report.summary()}")
                delay(10_000)
                continue
            }

            val task = repository.loadNextTask()
            if (task == null) {
                machine.moveTo(TaskState.Idle)
                logSink.info("没有待处理任务，进入待机")
                break
            }

            processTask(task)
        }
    }

    private suspend fun processTask(task: PendingTask) {
        var attempt = 0
        val start = System.currentTimeMillis()
        var success = false
        var errorCode: String? = null
        val screenshots = mutableListOf<String>()

        while (attempt <= MAX_RETRY && !success) {
            attempt += 1
            try {
                executeTask(task, screenshots)
                success = true
            } catch (failure: TaskFailure) {
                errorCode = failure.code
                logSink.error("任务 ${task.styleCode} 失败：${failure.message}")
                screenshots += failure.screenshotPath ?: captureFailure(task, attempt)
                if (attempt <= MAX_RETRY) {
                    scheduler.randomBrowse()
                }
            }
        }

        val duration = System.currentTimeMillis() - start
        val status = if (success) "success" else "failed"
        writer.markCompleted(task, status, errorCode, attempt - 1, screenshots, duration)
        moveFolderToDone(task)
        logSink.info("任务 ${task.styleCode} 完成，状态=$status，耗时=${duration}ms，重试=${attempt - 1}")
        scheduler.macroPause()
    }

    private suspend fun executeTask(task: PendingTask, screenshots: MutableList<String>) {
        accessibility.ensureHome()
        accessibility.openPublishEntry()

        machine.moveTo(TaskState.Prepare(task))
        scheduler.beforeAction("prepare")

        machine.moveTo(TaskState.FillForm(task))
        accessibility.fillTitleAndDescription(task)
        accessibility.selectImages(task)
        accessibility.setPriceAndStock(task)
        scheduler.afterAction("fillForm")

        machine.moveTo(TaskState.Review)
        machine.moveTo(TaskState.Publish)

        if (!accessibility.publish()) {
            throw TaskFailure("PUBLISH_TIMEOUT", "发布超时", captureFailure(task, retries = 0))
        }

        machine.moveTo(TaskState.PostTask(task, "success"))
    }

    private fun moveFolderToDone(task: PendingTask) {
        val source = "/sdcard/XianyuTasks/Todo/${task.styleCode}"
        val targetRoot = "/sdcard/XianyuTasks/Done/${task.styleCode}"
        if (!RootShell.move(source, targetRoot)) {
            logSink.error("移动任务目录失败：$source -> $targetRoot")
        }
    }

    private fun captureFailure(task: PendingTask, retries: Int): String {
        val dirPath = "/sdcard/XianyuTasks/Done/${task.styleCode}"
        RootShell.mkdir(dirPath)
        val path = "$dirPath/fail_$retries.png"
        if (!RootShell.screencap(path)) {
            Logger.w("截图失败：$path")
        }
        return path
    }

    override fun onEvent(event: AccessibilityEvent, service: AutomationAccessibilityService) {
        if (event.eventType == AccessibilityEvent.TYPE_NOTIFICATION_STATE_CHANGED) {
            Logger.i("Toast: ${event.text}")
        }
    }
}

class TaskFailure(
    val code: String,
    message: String,
    val screenshotPath: String? = null,
) : RuntimeException(message)
