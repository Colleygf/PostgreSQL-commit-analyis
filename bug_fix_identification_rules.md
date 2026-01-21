# Bug 修复提交识别规则

适用范围：PostgreSQL master 分支（2022–2025）提交历史的候选 Bug 修复筛查。

## 判定信号（优先级顺序）
- 强关键词（提交信息）：fix|bug|issue|crash|segfault|leak|overflow|deadlock|race|corrupt|assert|regress|incorrect|wrong|mishandled|panic|hang|memory leak。
- 弱关键词（需配合结构信号）：validate|check|boundary|mutex|lock|wait|timeout|retry|zero_damaged_pages|ereport|elog|error path|failover。
- 结构/范围：
  - 路径触及 src/backend/、src/include/，或 WAL/storage/replication 相关目录。
  - 新增/强化条件与边界：if/else、长度/索引检查、Lock/Unlock、ResourceOwner、引用计数。
  - 错误处理收紧：新增 ereport/elog(ERROR/FATAL/LOG)、返回值检查从忽略改为处理。
  - 数据损坏/恢复：zero_damaged_pages、checksum、fpi/full-page-write、redo/recovery。
- 回归/测试信号：commit message 含 regression test/backpatch/CVE，或同一提交修改 src/test/**、contrib/*/sql|expected/。

## 排除与降权
- 纯文档/翻译/注释/README 变更且无代码或测试改动。
- 仅格式化（whitespace/indent/pgindent）或 CI/脚本调度调整。
- 仅性能/重构描述且无错误修复暗示（"refactor", "cleanup", "perf"），除非伴随强关键词。

## 快速筛查命令
- 日志预筛：`git log --since=2022-01-01 --until=2025-12-31 --grep='fix\|bug\|crash\|segfault\|overflow\|deadlock\|race\|corrupt\|assert\|regress\|panic\|leak' --extended-regexp --no-merges`。
- 二次补充（弱关键词）：追加 `--grep='validate\|boundary\|timeout\|retry\|failover'` 生成待复核列表。
- Diff 加权：`git show -U3 <hash>` 查看是否新增条件/ereport/elog/Lock/Unlock、触及 storage/replication/WAL/aio/buffer/btree/gist/gin/heapam。

## 标记建议
- 标签字段：`is_bugfix (Y/M/N)`, `signals (keywords|structure|tests)`, `modules (storage|executor|planner|replication|catalog|utils|client)`, `risk_level (H/M/L)`。
- 高风险路径（storage/replication/WAL/locking）优先人工复核。
