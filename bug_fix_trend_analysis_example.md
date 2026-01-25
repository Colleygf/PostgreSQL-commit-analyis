# Bug 修复提交时间、作者、模块规律分析（示例流程）

## 1. 输入准备
- 使用已标注的 bug_fix_commits.csv（字段含 hash, date, author, is_bugfix, modules, loc_add, loc_del 等）。
- 过滤 is_bugfix=Y（可选保留 Maybe 做灵敏度分析）。

## 2. 时间分布分析
- 用 pandas 读取数据，date 字段转为 datetime。
- 按年、月、周 groupby 统计 bug 修复数量。
- 画折线图/柱状图，找出高峰期与低谷。

## 3. 作者分布分析
- groupby author 统计每人修复次数、总 LOC 增删。
- 取 Top N 作者，分析其活跃周期和主要修复模块。
- 可画水平条形图、热力图（作者-模块交叉）。

## 4. 模块分布分析
- modules 字段按分号/逗号拆分，统计各模块修复次数。
- 画饼图/条形图，突出 storage/replication/WAL 等高风险模块。
- 分析各模块的平均/中位 LOC 增删。

## 5. 结果输出
- 统计表：时间-数量、作者-数量、模块-数量、作者-模块透视表。
- 图表：时间序列、作者 top N、模块分布、交叉热力图。
- 文字总结：
  - 主要修复高峰期与 PostgreSQL 发布周期是否吻合。
  - 高频作者是否集中在特定模块。
  - 高风险模块的长期占比。

## 6. 示例代码片段
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('bug_fix_commits.csv', parse_dates=['date'])
df = df[df['is_bugfix'] == 'Y']
# 时间分布
monthly = df.groupby(df['date'].dt.to_period('M')).size()
monthly.plot(kind='bar')
plt.title('Monthly Bug Fixes')
plt.show()
# 作者分布
by_author = df.groupby('author').size().sort_values(ascending=False)
by_author.head(10).plot(kind='barh')
plt.title('Top 10 Authors')
plt.show()
# 模块分布
from collections import Counter
modules = df['modules'].dropna().str.cat(sep=';').split(';')
mod_count = pd.Series(Counter([m.strip() for m in modules if m.strip()]))
mod_count.plot(kind='bar')
plt.title('Bug Fixes by Module')
plt.show()
```

## 7. 产出建议
- 统计表（csv）、图表（png/svg）、分析结论（md/txt）。
- 供团队后续报告与展示直接引用。
