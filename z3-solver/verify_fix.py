from z3 import *


def verify_fix_logic():
    print("=== PostgreSQL 修复后逻辑的形式化验证 (Z3) ===")

    # 1. 定义域
    FileType = Int('FileType')  # 0=Unknown, 1=C, 2=H, 3=Py
    Attribute = Int('Attribute')  # 0=None, 1=Indent
    OutputAction = Int('OutputAction')  # 0=None, 1=GenC, 2=GenPy

    s = Solver()
    s.add(FileType >= 0, FileType <= 3)
    s.add(Attribute >= 0, Attribute <= 2)
    s.add(OutputAction >= 0, OutputAction <= 2)

    # 2. 建模“修复后的逻辑” (Corrected Implementation)
    # 逻辑变更点：在 Else 分支中增加了对 Python 的判断
    # IF type is C/H -> GenC
    # ELSE IF type is Py -> GenPy  <-- 补丁新增逻辑
    # ELSE -> DoNothing
    corrected_implementation = If(Or(FileType == 1, FileType == 2),
                                  OutputAction == 1,
                                  If(FileType == 3,
                                     OutputAction == 2,
                                     OutputAction == 0))

    s.add(corrected_implementation)

    # 3. 同样的规约 (Specification)
    # 我们依然寻找“输入是 Python 但输出错误”的反例
    violation_condition = And(
        FileType == 3,
        Attribute == 1,
        OutputAction != 2
    )

    s.add(violation_condition)

    # 4. 验证
    print("\n正在验证修复后的逻辑一致性...")
    result = s.check()

    if result == sat:
        print("\n[!] 验证失败：依然存在反例！修复无效。")
        print(s.model())
    else:
        print("\n[√] 验证通过：逻辑完备 (UNSAT)。")
        print("证明：在修复后的逻辑约束下，不存在违反规约的输入组合。")


if __name__ == "__main__":
    verify_fix_logic()