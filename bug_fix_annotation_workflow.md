# Bug 修复提交标注流程

目标：将候选 Bug 修复提交批量标注为 Y/M/N，并记录信号与理由，供后续统计与分析使用。

## 输入
- 候选列表：由识别规则筛出的提交 hash（建议含 message、日期、作者）。
- 代码基线：PostgreSQL master（2022–2025）。

## 步骤
1) 生成候选清单：
   - `git log --since=2022-01-01 --until=2025-12-31 --grep='fix\|bug\|crash\|segfault\|overflow\|deadlock\|race\|corrupt\|assert\|regress\|panic\|leak' --extended-regexp --no-merges > tmp_bugfix_candidates.log`
2) 逐条审阅：
   - `git show -U3 <hash>`，检查：
     - 是否修改核心路径（src/backend/**, src/include/**, storage/replication/WAL/buffer/btree/gist/gin/heapam/aio）。
     - 是否新增条件/边界/锁/引用计数/ereport/elog。
     - 是否伴随测试变更（src/test/**，contrib/*/sql|expected/）。
3) 记录标注：
   - 建议使用 CSV：`hash,is_bugfix(Y/M/N),signals(keywords|structure|tests),modules(storage|executor|planner|replication|catalog|utils|client),reason,text_paths,loc_add,loc_del,date,author`。
   - 示例：`abcd1234,Y,keywords+structure+tests,"msg: Fix crash; touched storage/buffer; added if+ereport",storage/buffer,25,3,2023-05-02,alice@example.com`。
4) 质量控制：
   - 对高风险模块（storage/replication/WAL/locking）进行二人复核或补充备注。
   - 将 `tmp_bugfix_candidates.log` 与标注表留存，便于追溯。

## 输出
- 标注表（csv/json/md 均可）。
- 补充材料：高置信/待复核/否定各 2–3 个示例 commit 的 git show 摘要，便于分享与校准。
