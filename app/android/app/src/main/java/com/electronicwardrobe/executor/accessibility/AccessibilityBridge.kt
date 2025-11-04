package com.electronicwardrobe.executor.accessibility

import android.view.accessibility.AccessibilityNodeInfo
import com.electronicwardrobe.executor.model.TaskEntry
import com.electronicwardrobe.executor.util.Logger
import java.io.File

class AccessibilityBridge {
    private fun service(): AutomationAccessibilityService {
        return AutomationAccessibilityService.current()
            ?: throw IllegalStateException("Accessibility service not connected")
    }

    fun ensureHome() {
        val svc = service()
        val tab = svc.findByText(XianyuSelectors.Home.TAB_SELL_TEXT)
            ?: svc.findByText(XianyuSelectors.Home.TAB_SELL_DESC)
        tab?.let { svc.performClick(it) }
    }

    fun openPublishEntry() {
        val svc = service()
        val button = svc.findByText(XianyuSelectors.PublishEntry.BUTTON_TEXT)
            ?: svc.findById(XianyuSelectors.PublishEntry.BUTTON_ID)
        if (button != null) {
            svc.performClick(button)
        } else {
            Logger.w("未找到发布入口按钮")
        }
    }

    fun fillTitleAndDescription(entry: TaskEntry) {
        val svc = service()
        val title = File(entry.titleFile).takeIf { it.exists() }?.readText() ?: entry.styleCode
        val desc = File(entry.descriptionFile).takeIf { it.exists() }?.readText() ?: entry.descriptionFile
        val titleSuccess = svc.clearAndSetTextById("com.taobao.idlefish:id/edit_title", title)
        val descSuccess = svc.clearAndSetTextById("com.taobao.idlefish:id/edit_desc", desc)
        if (!titleSuccess) Logger.w("标题输入失败")
        if (!descSuccess) Logger.w("描述输入失败")
    }

    fun selectImages(entry: TaskEntry) {
        val svc = service()
        svc.findByText(XianyuSelectors.Picture.ADD_DESC)?.let { svc.performClick(it) }
        val album = svc.findByText(XianyuSelectors.Picture.ALBUM_TEXT)
            ?: svc.findById(XianyuSelectors.Picture.ALBUM_ID)
        album?.let { svc.performClick(it) }
        svc.findByText(XianyuSelectors.Picture.TASK_DIR_KEYWORD)?.let { svc.performClick(it) }
        // TODO: 根据图片顺序选择文件，当前仅占位
    }

    fun setPriceAndStock(price: Double, stock: Int) {
        val svc = service()
        svc.findByText(XianyuSelectors.Price.BATCH_TEXT)?.let { svc.performClick(it) }
        val priceNode = svc.findById(XianyuSelectors.Price.PRICE_FIELD_ID)
        val stockNode = svc.findById(XianyuSelectors.Price.STOCK_FIELD_ID)
        if (priceNode != null) svc.setText(priceNode, price.toString())
        if (stockNode != null) svc.setText(stockNode, stock.toString())
        svc.findByText(XianyuSelectors.Price.CONFIRM_TEXT)?.let { svc.performClick(it) }
    }

    fun publish(): Boolean {
        val svc = service()
        val publishNode = svc.findByText(XianyuSelectors.Publish.BUTTON_TEXT)
            ?: svc.findByText(XianyuSelectors.Publish.BUTTON_DESC_KEYWORD)
        return publishNode?.let { svc.performClick(it) } ?: false
    }

    fun scroll(node: AccessibilityNodeInfo?) {
        service().scroll(node, forward = true)
    }
}
