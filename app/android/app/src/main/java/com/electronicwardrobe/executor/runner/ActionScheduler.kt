package com.electronicwardrobe.executor.runner

import com.electronicwardrobe.executor.util.Logger
import com.electronicwardrobe.executor.util.RandomDelays

class ActionScheduler(
    private val delays: RandomDelays = RandomDelays(),
) {
    suspend fun beforeAction(label: String) {
        Logger.i("beforeAction $label")
        delays.microDelay()
    }

    suspend fun afterAction(label: String) {
        Logger.i("afterAction $label")
        delays.microDelay()
    }

    suspend fun macroPause() {
        Logger.i("macroPause begin")
        delays.macroDelay()
        Logger.i("macroPause end")
    }

    suspend fun randomBrowse() {
        Logger.i("random browse placeholder")
        delays.randomBrowseDelay()
    }
}
