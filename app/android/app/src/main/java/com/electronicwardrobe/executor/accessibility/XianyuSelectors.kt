package com.electronicwardrobe.executor.accessibility

object XianyuSelectors {
    object Home {
        const val TAB_SELL_TEXT = "卖闲置"
        const val TAB_SELL_DESC = "发布"
    }

    object PublishEntry {
        const val BUTTON_TEXT = "发布闲置"
        const val BUTTON_ID = "com.taobao.idlefish:id/publish"
    }

    object PublishForm {
        const val TITLE_FIELD_ID = "com.taobao.idlefish:id/edit_title"
        const val DESC_FIELD_ID = "com.taobao.idlefish:id/edit_desc"
    }

    object Picture {
        const val ADD_DESC = "添加图片"
        const val GRID_VIEW = "android.widget.ImageView"
        const val ALBUM_TEXT = "相册"
        const val ALBUM_ID = "com.android.gallery3d:id/action_album"
        const val TASK_DIR_KEYWORD = "XianyuTasks"
    }

    object Spec {
        const val TAB_TEXT = "商品规格"
        const val ADD_TEXT = "添加规格"
        const val ADD_ID = "com.taobao.idlefish:id/add_sku"
        const val ENABLE_IMAGE_TEXT = "支持添加图片"
        const val ENABLE_IMAGE_ID = "com.taobao.idlefish:id/switch"
    }

    object Price {
        const val BATCH_TEXT = "批量设置价格和库存"
        const val BATCH_ID = "com.taobao.idlefish:id/batch"
        const val PRICE_FIELD_ID = "com.taobao.idlefish:id/price"
        const val STOCK_FIELD_ID = "com.taobao.idlefish:id/stock"
        const val CONFIRM_TEXT = "确定"
    }

    object Publish {
        const val BUTTON_TEXT = "确认发布"
        const val BUTTON_DESC_KEYWORD = "发布"
        const val SUCCESS_TOAST = "发布成功"
    }
}
