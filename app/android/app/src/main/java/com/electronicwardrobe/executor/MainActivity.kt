package com.electronicwardrobe.executor

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.electronicwardrobe.executor.env.EnvDiagnostics
import com.electronicwardrobe.executor.runner.TaskController

class MainActivity : AppCompatActivity() {
    private lateinit var envDiagnostics: EnvDiagnostics
    private lateinit var controller: TaskController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        envDiagnostics = EnvDiagnostics(this)
        controller = TaskController(this)

        val statusView: TextView = findViewById(R.id.label_status)
        val startButton: Button = findViewById(R.id.button_start)
        val stopButton: Button = findViewById(R.id.button_stop)

        startButton.setOnClickListener {
            val report = envDiagnostics.runChecks()
            if (report.isHealthy) {
                controller.start()
                statusView.text = getString(R.string.main_status_running)
            } else {
                statusView.text = report.summary()
            }
        }

        stopButton.setOnClickListener {
            controller.stop()
            statusView.text = getString(R.string.main_status_idle)
        }
    }
}
