package com.electronicwardrobe.executor.env

import android.content.Context
import android.provider.Settings
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import androidx.core.content.getSystemService
import com.electronicwardrobe.executor.util.Logger
import com.electronicwardrobe.executor.util.RootShell

data class EnvReport(
    val accessibilityEnabled: Boolean,
    val rootGranted: Boolean,
    val networkAvailable: Boolean,
) {
    val isHealthy: Boolean
        get() = accessibilityEnabled && rootGranted && networkAvailable

    fun summary(): String = buildString {
        append("无障碍=")
        append(if (accessibilityEnabled) "正常" else "未开启")
        append(" Root=")
        append(if (rootGranted) "正常" else "缺失")
        append(" 网络=")
        append(if (networkAvailable) "正常" else "不可用")
    }
}

class EnvDiagnostics(private val context: Context) {
    fun runChecks(): EnvReport {
        val accessibility = isAccessibilityEnabled()
        val root = isRootGranted()
        val network = isNetworkAvailable()
        val report = EnvReport(accessibility, root, network)
        Logger.i("EnvDiagnostics: ${report.summary()}")
        return report
    }

    private fun isAccessibilityEnabled(): Boolean {
        return runCatching {
            Settings.Secure.getInt(context.contentResolver, Settings.Secure.ACCESSIBILITY_ENABLED) == 1
        }.getOrDefault(false)
    }

    private fun isRootGranted(): Boolean {
        return RootShell.run("id")
    }

    private fun isNetworkAvailable(): Boolean {
        val manager = context.getSystemService<ConnectivityManager>() ?: return false
        val active = manager.activeNetwork ?: return false
        val capabilities = manager.getNetworkCapabilities(active) ?: return false
        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
    }
}
