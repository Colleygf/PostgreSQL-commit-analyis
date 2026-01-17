import pysnooper
import os
import subprocess
import sys

# --- 第一步：定义全局变量 ---
LOG_DIR = "analysis_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# --- 第二步：定义分析函数 ---

# 针对 2025 年脚本：分析配置同步逻辑
@pysnooper.snoop(os.path.join(LOG_DIR, 'editorconfig_sync.log'), depth=2)
def analyze_editorconfig_sync():
    # 注意：确保该路径在你的本地仓库中存在
    target_script = "src/tools/generate_editorconfig.py"
    if os.path.exists(target_script):
        print(f"正在追踪: {target_script}")
        # 使用当前环境的 python 解释器运行脚本
        result = subprocess.run([sys.executable, target_script], capture_output=True, text=True)
        return result.stdout
    else:
        return f"错误：未找到脚本 {target_script}"

# 针对 2022 年脚本：分析规则生成逻辑
@pysnooper.snoop(os.path.join(LOG_DIR, 'unaccent_rules.log'))
def analyze_unaccent_rules():
    target_script = "contrib/unaccent/generate_unaccent_rules.py"
    if os.path.exists(target_script):
        print(f"正在追踪: {target_script}")
        result = subprocess.run([sys.executable, target_script], capture_output=True, text=True)
        return result.stdout
    else:
        return f"错误：未找到脚本 {target_script}"

# --- 第三步：主执行逻辑 ---
if __name__ == "__main__":
    print("=== 开始 PostgreSQL Python 脚本动态轨迹分析 ===")
    
    # 执行 2025 年脚本分析
    try:
        analyze_editorconfig_sync()
        print("2025 年脚本分析成功，日志已生成。")
    except Exception as e:
        print(f"执行同步脚本分析失败: {e}")

    # 执行 2022 年脚本分析
    try:
        analyze_unaccent_rules()
        print("2022 年脚本分析成功，日志已生成。")
    except Exception as e:
        print(f"执行规则生成脚本分析失败: {e}")

    print(f"\n分析完成！请在目录 {os.path.abspath(LOG_DIR)} 查看日志文件。")