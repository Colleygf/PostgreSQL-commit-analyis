import pandas as pd
import os

# --- 配置 ---
DIFF_DIR = 'static_analysis_diffs'
SUMMARY_FILE = 'static_pattern_summary.csv'
AST_REPORT = 'ast_logic_analysis_report.csv'

def extract_top_5_for_z3():
    # 1. 加载数据
    df_summary = pd.read_csv(SUMMARY_FILE)
    df_ast = pd.read_csv(AST_REPORT)
    
    # 2. 筛选逻辑：模式包含 Logic 和 Assertion，且 AST 解析成功（没有 ERROR）
    # 这样筛选出的样本最适合 Z3，因为 Assertion 提供了现成的安全约束
    merged = pd.merge(df_summary, df_ast, left_on='file', right_on='filename')
    
    targets = merged[
        (merged['patterns'].str.contains('Logic')) & 
        (merged['patterns'].str.contains('Assertion')) &
        (~merged['ast_features'].str.contains('AST_PARSE_ERROR'))
    ].head(5)

    if targets.empty:
        # 如果没有同时满足 Logic+Assertion 的，则退而求其次寻找复杂的 Logic 样本
        targets = merged[
            (merged['patterns'].str.contains('Logic')) & 
            (~merged['ast_features'].str.contains('AST_PARSE_ERROR'))
        ].head(5)

    print(f"🚀 成功锁定 {len(targets)} 个目标验证样本：\n")

    for idx, row in targets.iterrows():
        print(f"{'='*60}")
        print(f"【目标 {idx+1}】 文件名: {row['file']}")
        print(f"【模式分类】: {row['patterns']}")
        print(f"【AST 逻辑特征】: {row['ast_features']}")
        print(f"{'-'*60}")
        
        # 读取补丁全文
        try:
            with open(os.path.join(DIFF_DIR, row['file']), 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"读取失败: {e}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    extract_top_5_for_z3()