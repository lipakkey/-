package com.electronicwardrobe.executor.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.electronicwardrobe.executor.util.Logger

class AutomationAccessibilityService : AccessibilityService() {
    override fun onServiceConnected() {
        super.onServiceConnected()
        Logger.i("Accessibility service connected")
        instance = this
        serviceInfo = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED or
                AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            notificationTimeout = 100
            flags = AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or
                AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        listeners.toList().forEach { listener ->
            runCatching { listener.onEvent(event, this) }.onFailure {
                Logger.e("Listener error", it)
            }
        }
    }

    override fun onInterrupt() {
        Logger.w("Accessibility service interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        listeners.clear()
    }

    fun findByText(text: String): AccessibilityNodeInfo? {
        return rootInActiveWindow?.findAccessibilityNodeInfosByText(text)?.firstOrNull()
    }

    fun findById(id: String): AccessibilityNodeInfo? {
        return runCatching { rootInActiveWindow?.findAccessibilityNodeInfosByViewId(id)?.firstOrNull() }
            .getOrNull()
    }

    fun performClick(node: AccessibilityNodeInfo?): Boolean {
        var current = node
        while (current != null) {
            if (current.isClickable) {
                return current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            }
            current = current.parent
        }
        return false
    }

    fun setText(node: AccessibilityNodeInfo?, value: CharSequence): Boolean {
        if (node == null) return false
        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, value)
        }
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
    }

    fun clearAndSetTextById(viewId: String, value: CharSequence): Boolean {
        val node = findById(viewId) ?: return false
        node.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, value)
        }
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
    }

    fun scroll(node: AccessibilityNodeInfo?, forward: Boolean = true): Boolean {
        if (node == null) return false
        val action = if (forward) AccessibilityNodeInfo.ACTION_SCROLL_FORWARD else AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
        return node.performAction(action)
    }

    companion object {
        @Volatile
        private var instance: AutomationAccessibilityService? = null
        private val listeners = mutableSetOf<AccessibilityListener>()

        fun current(): AutomationAccessibilityService? = instance

        fun registerListener(listener: AccessibilityListener) {
            listeners += listener
        }

        fun unregisterListener(listener: AccessibilityListener) {
            listeners -= listener
        }
    }
}

fun interface AccessibilityListener {
    fun onEvent(event: AccessibilityEvent, service: AutomationAccessibilityService)
}
