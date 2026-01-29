#!/usr/bin/env python3

import os

def cd_to_repo_root():
    abspath = os.path.abspath(__file__)
    # 注意：如果脚本在 src/tools/ 下运行，向上退两级是根目录
    dname = os.path.join(os.path.dirname(abspath), "..", "..")
    os.chdir(dname)

# 针对以空格为基础的缩进级别进行硬编码
space_based_indent_sizes = {
    "*.py": 4,
    "*.sgml": 1,
    "*.xsl": 1,
    "*.xml": 2,
}

def main():
    cd_to_repo_root()

    if not os.path.exists(".gitattributes"):
        print("Error: .gitattributes not found!")
        return

    with open(".gitattributes", "r") as f:
        lines = f.read().splitlines()

    new_contents = """root = true

[*]
indent_size = tab
"""

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # 增强解析：支持复杂的 gitattributes 行
        parts = line.split()
        if len(parts) < 2:
            continue
        name = parts[0]
        git_rules = parts[1:] # 获取该文件后缀对应的所有规则

        rules = []
        
        # --- 核心修复：识别 filter=indent 或包含 python 的规则 ---
        is_indent_filtered = any("filter=indent" in r for r in git_rules)
        is_whitespace_rule = any(r.startswith("whitespace=") or r == "-whitespace" for r in git_rules)

        if is_indent_filtered or is_whitespace_rule:
            # 基础规则设置
            rules += ["trim_trailing_whitespace = true", "insert_final_newline = true"]
            
            # 缩进风格判断
            if name in space_based_indent_sizes:
                rules += ["indent_style = space"]
                rules += [f"indent_size = {space_based_indent_sizes[name]}"]
            else:
                rules += ["indent_style = tab"]
                rules += ["tab_width = 4"] # 默认值

        else:
            # 如果不符合已知规则，跳过
            continue

        if rules:
            rules_str = "\n".join(rules)
            new_contents += f"\n[{name}]\n{rules_str}\n"

    with open(".editorconfig", "w") as f:
        f.write(new_contents)
    print("Successfully generated .editorconfig")

if __name__ == "__main__":
    main()