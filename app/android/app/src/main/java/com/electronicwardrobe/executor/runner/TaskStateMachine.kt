package com.electronicwardrobe.executor.runner

import com.electronicwardrobe.executor.repository.PendingTask
import com.electronicwardrobe.executor.util.Logger

sealed interface TaskState {
    object Idle : TaskState
    object EnvCheck : TaskState
    data class LoadTask(val task: PendingTask?) : TaskState
    data class Prepare(val task: PendingTask) : TaskState
    data class FillForm(val task: PendingTask) : TaskState
    object Review : TaskState
    object Publish : TaskState
    data class PostTask(val task: PendingTask, val status: String) : TaskState
    data class Error(val message: String) : TaskState
}

class TaskStateMachine {
    var currentState: TaskState = TaskState.Idle
        private set

    fun moveTo(newState: TaskState) {
        Logger.i("State transition: \\ -> \\")
        currentState = newState
    }
}
