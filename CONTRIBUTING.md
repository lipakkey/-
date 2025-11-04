# 贡献指南（草稿）

## 分支策略
- `main`：稳定分支，仅合并通过测试的 PR。
- `develop`（可选）：集成环境。
- `feature/<scope>`：功能开发；完成后提交 PR。

## 提交流程
1. `uv sync` 安装依赖。
2. `pre-commit install`。
3. 功能开发 → 补充测试 → `make checks`。
4. 提交信息格式：`feat(core): 支持敏感词过滤`。
5. 提交 PR 前更新相关文档。

## 代码规范
- Python：PEP8，黑名单词处理，类型标注齐全。
- Kotlin：遵循 Android Kotlin Style Guide。
- 文档：使用 Markdown，中文优先。

## 评审标准
- 测试覆盖率不降低。
- 文档同步更新。
- 日志、异常处理完整。

> 完整版本将在 Stage 6 文档交付阶段完善。
