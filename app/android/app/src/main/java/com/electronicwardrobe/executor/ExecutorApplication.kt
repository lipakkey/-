package com.electronicwardrobe.executor

import android.app.Application
import com.electronicwardrobe.executor.util.Logger

class ExecutorApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        Logger.init(this)
    }
}
