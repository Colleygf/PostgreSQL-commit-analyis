import pandas as pd
from git import Repo
import os

def fast_extract(year):
    repo = Repo('./postgres')
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    print(f"正在快速提取 {year} 年基础数据...")
    commits = list(repo.iter_commits('master', since=start_date, until=end_date))
    
    data = [{
        'hash': c.hexsha,
        'author': c.author.name,
        'date': c.committed_datetime,
        'msg': c.summary
    } for c in commits]
    
    df = pd.DataFrame(data)
    df.to_csv(f'raw_base_{year}.csv', index=False)
    return df

def filter_bug_fixes(df):
    keywords = ['fix', 'bug', 'error', 'crash', 'leak', 'overflow', 'assert']
    # 过滤出可能是 Bug 修复的提交
    df['is_fix'] = df['msg'].str.lower().apply(lambda x: any(k in str(x) for k in keywords))
    return df[df['is_fix'] == True].copy()

def detailed_analysis(fix_df, repo_path='./postgres'):
    repo = Repo(repo_path)
    details = []
    
    print(f"对 {len(fix_df)} 个潜在 Bug 提交进行详尽分析...")
    for idx, row in fix_df.iterrows():
        commit = repo.commit(row['hash'])
        # 统计修改的模块
        paths = [f.split('/')[0] for f in commit.stats.files.keys()]
        
        details.append({
            'hash': row['hash'],
            'author': row['author'],
            'modules': list(set(paths)),
            'lines_added': commit.stats.total['insertions'],
            'lines_deleted': commit.stats.total['deletions']
        })
    
    return pd.DataFrame(details)

for year in [2023,2024,2025]:
    df = fast_extract(year)
    bug_fixes_df = filter_bug_fixes(df)
    detailed_df = detailed_analysis(bug_fixes_df)
    detailed_df.to_csv(f'bug_fixes_detailed_{year}.csv', index=False)