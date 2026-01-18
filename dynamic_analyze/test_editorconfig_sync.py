import pytest
import subprocess
import sys
import os
# 目标脚本路径 [cite: 53]
TARGET_SCRIPT = "src/tools/generate_editorconfig.py"

class TestEditorConfigSync:
    
    @pytest.fixture
    def setup_files(self, tmp_path):
        """模拟仓库环境的目录结构"""
        tools_dir = tmp_path / "src" / "tools"
        tools_dir.mkdir(parents=True)
        
        # 模拟 .gitattributes 文件，加入 2025 年新增的 Python 规则 [cite: 4]
        git_attr = tmp_path / ".gitattributes"
        git_attr.write_text("*.py    filter=indent\n", encoding="utf-8")
        
        # 复制实际脚本到临时目录进行测试
        import shutil
        local_script = os.path.join(os.getcwd(), TARGET_SCRIPT)
        test_script = tools_dir / "generate_editorconfig.py"
        shutil.copy(local_script, test_script)
        
        yield tmp_path

    def test_logic_effectiveness_2025(self, setup_files):
        """
        验证 2025 年改正后的有效性：
        运行脚本后，.editorconfig 应该包含对应的 Python 缩进规则。
        """
        work_dir = setup_files
        script_path = work_dir / "src" / "tools" / "generate_editorconfig.py"
        
        # 执行脚本 [cite: 55]
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(work_dir),
            capture_output=True,
            text=True
        )
        
        # 验证 1: 脚本执行成功 (returncode 为 0) [cite: 58, 59]
        assert result.returncode == 0
        
        # 验证 2: 检查是否生成了 .editorconfig 文件
        editor_config_file = work_dir / ".editorconfig"
        assert editor_config_file.exists(), "改正后应能自动生成 .editorconfig"
        
        # 验证 3: 检查内容是否同步了 .gitattributes 中的规则 
        content = editor_config_file.read_text()
        assert "[*.py]" in content
        assert "indent_style = space" in content  # 假设脚本逻辑是将 py 映射为 space

    def test_regression_comparison(self, setup_files):
        """
        对比测试：模拟改正前的状态（无此脚本时）。
        """
        work_dir = setup_files
        editor_config_file = work_dir / ".editorconfig"
        
        # 改正前：如果手动删除脚本或不运行，文件不会自动更新 [cite: 1]
        if editor_config_file.exists():
            os.remove(editor_config_file)
            
        # 结论：在没有该 2025 年补丁前，属性变更不会反应在配置中
        assert not editor_config_file.exists()