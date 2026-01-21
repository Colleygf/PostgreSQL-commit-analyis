# Bug 修复提交时间 / 作者 / 模块规律分析方案

目标：基于已标注的 Bug 修复提交（2022–2025），量化时间节奏、贡献者分布、模块热点。

## 数据来源
- 标注表（字段示例）：hash, date, author, message, is_bugfix (Y/M/N), signals, modules, files, loc_add, loc_del。
- Git 基线：PostgreSQL master（2022–2025）。

## 指标设计
- 时间维度：按年/月/周统计 Bug 修复数量；计算滚动平均与峰值（发布周期关联）。
- 作者维度：Top N 贡献者的 Bug 修复次数、占比；人均 LOC 增删中位数；作者与模块交叉分布。
- 模块维度（按路径映射）：storage/replication/WAL/buffer/btree/gist/gin/heapam, executor, planner, catalog, utils, client；统计修复次数、占比、趋势。
- 变更规模：每次修复的文件数、loc_add/loc_del 分布（中位数、P90）。
- 置信/信号：Y/M/N 占比；包含 tests 的修复占比；含强关键词的占比。

## 处理流程
1) 读取标注表（csv/json），过滤 is_bugfix=Y（可选保留 Maybe 做灵敏度分析）。
2) 规范化模块字段：依据文件路径映射到统一模块名（见上）。
3) 聚合统计：
   - 时间：group by 年/月/周，绘制折线或柱状。
   - 作者：group by author；再 group by author+module 做热力或透视表。
   - 模块：group by module；计算 loc_add/loc_del 分布。
4) 可视化建议：pandas + matplotlib/seaborn；时间序列、堆叠柱状、水平条形图、热力图。
5) 报告要点：
   - 峰值月份/周与发布周期是否对齐。
   - 高频作者是否集中在特定模块。
   - 高风险模块（storage/replication/WAL/locking）是否长期占比高。
   - 大体量修复（P90 loc）的分布与作者/模块关联。

## 输出格式
- 表格：时间/作者/模块的聚合数据（csv）。
- 图表：时间序列、作者 top N、模块占比、作者-模块透视（png/svg）。
- 简短解读：主要发现与异常峰值的文字总结。
