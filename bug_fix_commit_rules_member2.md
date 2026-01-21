# Bug 修复提交识别与标注规则

目的：在 PostgreSQL master 分支（2022–2025）中半自动识别并标注 Bug 修复提交，用于后续统计与分析。

## 1. 优先级排序的判定信号
- 强关键词（提交信息，命中即高置信）：fix|bug|issue|crash|segfault|leak|overflow|deadlock|race|corrupt|assert|regress|incorrect|wrong|mishandled|panic|hang|memory leak。
- 弱关键词（配合结构信号）：validate|check|boundary|overflow|mutex|lock|wait|timeout|retry|zero_damaged_pages|ereport|elog|error path|failover。
- 结构/范围信号：
  - 触及 src/backend/ 或 src/include/（核心执行路径），或 WAL/storage/replication 相关目录。
  - 补充条件/边界：新增/改写 if/else、长度/索引检查、Lock/Unlock、ResourceOwner、Reference counting。
  - 错误处理收紧：新增 ereport/elog(ERROR/FATAL/LOG)；返回值检查从忽略改为处理。
  - 数据损坏/恢复路径：zero_damaged_pages、checksum、fpi/full-page-write、redo/recovery。
- 回归/测试信号：
  - commit message 含 regression test / backpatch / CVE。
  - 同一个 commit 修改了 src/test/** 或 contrib/*/sql|expected/。

## 2. 排除/降权信号
- 纯文档、翻译、注释、README 变更且无测试/代码修改。
- 仅格式化（whitespace/indentation/pgindent）或 CI 脚本调整。
- 仅性能/重构描述且无错误修复暗示（"refactor", "cleanup", "perf"），除非伴随强关键词。

## 3. 识别流程（可脚本化）
1) 预筛选提交（日志层）：
   - `git log --since=2022-01-01 --until=2025-12-31 --grep='fix\|bug\|crash\|segfault\|overflow\|deadlock\|race\|corrupt\|assert\|regress\|panic\|leak' --extended-regexp`。
   - 可追加弱关键词形成第二层候选集，供人工复核。
2) 结构加权（diff 层）：
   - 对候选集运行 `git show -U3 <hash>`，解析：
     - 是否修改 src/backend/ 或 src/include/。
     - 是否新增条件/校验/ereport/elog/Lock/Unlock；是否出现零/负长度检查。
     - 是否涉及 WAL/storage/replication/visibility/buffer/btree/gist/gin/heapam/aio。
3) 测试关联：
   - 提交同时修改 src/test/** 或 contrib/*/sql|expected/ 视为提升置信度。
4) 标签标注（示例字段）：
   - `is_bugfix`（Y/N/Maybe）、`signals`（关键词|结构|测试）、`modules`（按路径映射：storage|executor|planner|replication|catalog|utils|client）、`risk_level`（H/M/L）。

## 4. 简易正则/脚本片段
- 关键词过滤：`--grep='fix\|bug\|crash\|segfault\|overflow\|deadlock\|race\|corrupt\|panic' --extended-regexp`。
- 判定 ereport/elog 增量：在 diff 中查找 `^\+.*ereport` 或 `^\+.*elog`。
- 条件/边界补充：查找新增的 `^\+\s*if.*`、`^\+.*Assert`、`^\+.*CHECK_FOR_INTERRUPTS`、`^\+.*(<=\s*|>=\s*|<\s*0|==\s*0)`。

## 5. 判定示例（人工规则）
- 高置信 Bug 修复：
  - Message: "Fix crash in heap vacuum when page is all-visible"；路径含 src/backend/storage/，新增条件检查 → 标注 Y。
  - Message: "Prevent deadlock in logical replication apply worker"；diff 调整 Lock/Unlock 顺序 → 标注 Y。
- 需要复核：
  - Message: "Refactor walreceiver timeouts"；无强关键词但触及 replication + Lock 逻辑 → 标注 Maybe。
- 非 Bug 修复：
  - Message: "Docs: update release notes"；仅 doc 路径 → 标注 N。

## 6. 输出格式建议
- CSV/JSON 字段：`hash, date, author, message, is_bugfix (Y/M/N), signals (list), modules, files, loc_add, loc_del`。
- 保留 git show 摘要文本以便复查（可存入 markdown）。

## 7. 标注操作步骤
1) 拉取候选：`git log --since=2022-01-01 --until=2025-12-31 --grep='fix\|bug\|crash\|segfault\|overflow\|deadlock\|race\|corrupt\|assert\|regress\|panic\|leak' --extended-regexp --no-merges > tmp_bugfix_candidates.log`。
2) 逐条查看：`git show -U3 <hash>`，按第 1–5 节的信号判定。
3) 标注到表（推荐 csv）：字段 `hash,is_bugfix(Y/M/N),signals(modules|keywords|tests),reason(loc summary),paths(located modules),loc_add,loc_del,date,author`。
4) 示例行：`abcd1234,Y,keywords+structure+tests,"msg contains 'Fix crash'; touched storage/buffer; added if+ereport",storage/buffer,25,3,2023-05-02,alice@example.com`。
5) 对高风险路径（storage/replication/WAL/locking）优先人工复核。

## 8. 产出与复用
- 交付物：候选清单 + 已标注表（csv/json/md 均可）+ 每类示例 commit（高置信/待复核/否定各 2–3 个）。
- 供后续静态/动态/形式化分析直接消费，避免重复筛查。
