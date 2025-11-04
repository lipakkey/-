# 桌面端同步需求（中央厨房报告字段）

## 报告文件
- 生成路径：`<输出目录>/reports/delivery_report.json`
- JSON 结构包含：
  - `summary`
    - `total`：生成的任务数量（int）
    - `success`：成功数量 = total - len(failures)
    - `failures`：列表，元素格式 `"STYLE001: 错误描述"`
    - `per_device`：字典，`device_id -> 任务数`
    - `sensitive_hits`：字典，`敏感词 -> [关联款号列表]`
  - `entries`：数组，每个元素对应单款任务
    - `style_code`
    - `device_id`
    - `price`
    - `macro_delay`：`[min, max]`
    - `title_file`：相对路径（指向任务包内 `text/title.txt`）
    - `description_files`：数组，相对路径列表
    - `image_files`：数组，相对路径列表

## 桌面端待关注事项
1. 读取 `summary.per_device` 与设备映射表，展示任务分布。
2. 对 `summary.failures` 做重点提示，支持人工快速定位输入目录。
3. `entries` 中的路径在批次目录内相对路径，例如：
   - `Output_Batch_Phone_1/STYLE001/text/title.txt`
4. 未来扩展字段：
   - `entries[i].sku`（待图片标注阶段补充）
   - `summary.retries`（安卓执行器回传后补写）

## 下一步协同
- 请工作区1确认是否需要额外字段（如价格随机尾数来源、版本号等）。
- 桌面端实现时，需支持加载多个 `delivery_report.json` 并按日期归档。
