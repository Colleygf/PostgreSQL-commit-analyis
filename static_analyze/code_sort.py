import os
import pandas as pd

DIFF_DIR = 'static_analysis_diffs'
patterns = {
    'NullCheck': ['NULL', 'nullptr', 'nil'],
    'Memory': ['palloc', 'pfree', 'malloc', 'free', 'leak'],
    'Logic': ['if (', 'else', '==', '!=', '>', '<'],
    'Assertion': ['Assert(', 'Trap('],
    'Concurrency': ['LWLock', 'SpinLock', 'LockRelation']
}

report = []

for file in os.listdir(DIFF_DIR):
    if file.endswith('.diff'):
        with open(os.path.join(DIFF_DIR, file), 'r', encoding='utf-8') as f:
            content = f.read()
            detected = []
            for category, keys in patterns.items():
                if any(key in content for key in keys):
                    detected.append(category)
            
            report.append({
                'file': file,
                'patterns': ", ".join(detected) if detected else "Other"
            })

# 输出初步分析简报
analysis_df = pd.DataFrame(report)
analysis_df.to_csv('static_pattern_summary.csv', index=False)
print("📊 静态模式初步分类已完成，详见 static_pattern_summary.csv")