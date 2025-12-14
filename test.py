"""
Main Module - 数学表达式分析器测试系统
从 JSON 文件读取测试案例，执行两个主要任务：
1. 表达式分析：分词 + AST 生成
2. 等价性检查：判断两个表达式是否相等
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from lexer import tokenize
from parser import parse
from ast_nodes import print_ast
from polynomial import normalize_expression
from equality import are_equivalent, check_equivalence_verbose


# ============================================================================
# 输出重定向工具
# ============================================================================

class TeeOutput:
    """同时输出到控制台和文件的工具类"""
    
    def __init__(self, filename: str):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()




# ============================================================================
# 工具函数
# ============================================================================

def print_section(title: str):
    """打印格式化的章节标题"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")


def print_subsection(title: str):
    """打印格式化的子章节标题"""
    print(f"\n{'-' * 80}")
    print(f"  {title}")
    print(f"{'-' * 80}")


def load_test_cases(json_file: str = "test_cases.json") -> dict:
    """
    从 JSON 文件加载测试案例
    
    Args:
        json_file: JSON 文件路径
    
    Returns:
        测试案例字典
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到测试文件 '{json_file}'")
        return {}
    except json.JSONDecodeError as e:
        print(f"错误: JSON 文件格式错误 - {e}")
        return {}


# ============================================================================
# Task 1: 表达式分析 (分词 + AST)
# ============================================================================

def analyze_expression(expr_str: str, show_details: bool = True):
    """
    Task 1: 分析单个表达式
    显示: 输入 → 词法分析(Tokens) → 语法分析(AST) → 规范化
    
    Args:
        expr_str: 表达式字符串
        show_details: 是否显示详细信息
    
    Returns:
        (success: bool, error_msg: str or None)
    """
    if show_details:
        print(f"\n表达式: {expr_str}")
        print("-" * 70)
    
    try:
        # Step 1: 词法分析 (Tokenization)
        tokens = tokenize(expr_str)
        
        if show_details:
            print("📝 词法分析 (Tokens):")
            for token in tokens:
                token_type = token.type.name
                # 高亮隐式乘法
                if token.type.name == 'IMPLICIT_MULTIPLY':
                    token_type = f"*{token_type}*"
                print(f"  {token_type:22} | value={repr(token.value):10} | pos={token.pos}")
        
        # Step 2: 语法分析 (Parsing to AST)
        ast = parse(expr_str)
        
        if show_details:
            print("\n🌳 语法分析 (AST):")
            print_ast(ast, indent=2)
        
        # Step 3: 规范化 (Normalization)
        try:
            poly = normalize_expression(ast)
            if show_details:
                print(f"\n✓ 规范化成功: {poly}")
        except Exception:
            if show_details:
                print(f"\n⚠ 规范化跳过 (包含不可展开的元素)")
        
        return True, None
        
    except Exception as e:
        if show_details:
            print(f"\n✗ 错误: {e}")
        return False, str(e)


def run_task1_expression_analysis(test_data: dict):
    """
    运行 Task 1: 表达式分析测试
    
    Args:
        test_data: Task 1 的测试数据
    """
    print_section("TASK 1: 表达式分析 (分词 + AST)")
    print(f"说明: {test_data.get('description', '')}\n")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_group in test_data.get('test_cases', []):
        category = test_group.get('category', 'Unknown')
        expressions = test_group.get('expressions', [])
        
        print_subsection(f"分类: {category} ({len(expressions)} 个测试)")
        
        for expr in expressions:
            total_tests += 1
            success, error = analyze_expression(expr, show_details=True)
            
            if success:
                passed_tests += 1
            else:
                failed_tests.append((expr, error))
    
    # 打印汇总
    print_subsection("Task 1 汇总")
    print(f"总计: {total_tests} 个测试")
    print(f"✓ 成功: {passed_tests}")
    print(f"✗ 失败: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\n失败的测试:")
        for expr, error in failed_tests:
            print(f"  - {expr}: {error}")


# ============================================================================
# Task 2: 等价性检查
# ============================================================================

def check_equivalence(expr1_str: str, expr2_str: str, expected: bool = None) -> tuple:
    """
    Task 2: 检查两个表达式是否等价
    
    Args:
        expr1_str: 第一个表达式字符串
        expr2_str: 第二个表达式字符串
        expected: 期望的结果 (True/False/None)
    
    Returns:
        (is_equivalent: bool, is_correct: bool, method: str, details: str)
    """
    try:
        ast1 = parse(expr1_str)
        ast2 = parse(expr2_str)
        
        is_equiv, method, details = check_equivalence_verbose(ast1, ast2)
        
        # 判断是否符合预期
        is_correct = (expected is None) or (is_equiv == expected)
        
        return is_equiv, is_correct, method, details
    
    except Exception as e:
        return False, False, "error", str(e)


def print_equivalence_result(expr1: str, expr2: str, is_equiv: bool, is_correct: bool, method: str):
    """
    打印等价性检查结果
    
    Args:
        expr1: 第一个表达式
        expr2: 第二个表达式
        is_equiv: 是否等价
        is_correct: 是否符合预期
        method: 使用的方法
    """
    status_symbol = "✓" if is_equiv else "✗"
    correct_symbol = "✓" if is_correct else "✗✗"
    
    equiv_text = "等价" if is_equiv else "不等价"
    
    print(f"{correct_symbol} {expr1:25} ≟ {expr2:25} → {status_symbol} {equiv_text:6} ({method})")


def run_task2_equivalence_checking(test_data: dict):
    """
    运行 Task 2: 等价性检查测试
    
    Args:
        test_data: Task 2 的测试数据
    """
    print_section("TASK 2: 等价性检查")
    print(f"说明: {test_data.get('description', '')}\n")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_group in test_data.get('test_cases', []):
        category = test_group.get('category', 'Unknown')
        should_be_equivalent = test_group.get('should_be_equivalent', None)
        pairs = test_group.get('pairs', [])
        
        print_subsection(f"分类: {category} ({len(pairs)} 个测试)")
        
        for expr1, expr2 in pairs:
            total_tests += 1
            
            is_equiv, is_correct, method, details = check_equivalence(
                expr1, expr2, expected=should_be_equivalent
            )
            
            print_equivalence_result(expr1, expr2, is_equiv, is_correct, method)
            
            if is_correct:
                passed_tests += 1
            else:
                failed_tests.append((expr1, expr2, is_equiv, should_be_equivalent))
    
    # 打印汇总
    print_subsection("Task 2 汇总")
    print(f"总计: {total_tests} 个测试")
    print(f"✓ 正确: {passed_tests}")
    print(f"✗ 错误: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\n错误的测试 (结果与预期不符):")
        for expr1, expr2, actual, expected in failed_tests:
            actual_text = "等价" if actual else "不等价"
            expected_text = "等价" if expected else "不等价"
            print(f"  - {expr1} ≟ {expr2}")
            print(f"    实际: {actual_text}, 期望: {expected_text}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主程序：从 JSON 加载测试案例并运行所有测试
    """
    # 生成输出文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"test_results_{timestamp}.log"
    
    # 重定向输出到 LOG 文件和控制台
    tee = TeeOutput(log_file)
    sys.stdout = tee
    
    try:
        # 打印测试开始信息
        print("=" * 80)
        print("数学表达式分析器 - 测试报告")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试配置: test_cases.json")
        print(f"LOG 输出: {log_file}")
        print("=" * 80)
        
        print_section("数学表达式分析器 - 自动化测试系统")
        print("测试配置文件: test_cases.json")
        print("包含两个主要任务:")
        print("  - Task 1: 表达式分析 (分词 + AST)")
        print("  - Task 2: 等价性检查")
        
        # 加载测试案例
        test_cases = load_test_cases("test_cases.json")
        
        if not test_cases:
            print("\n✗ 无法加载测试案例，程序退出")
            return
        
        # Task 1: 表达式分析
        if 'task1_expression_analysis' in test_cases:
            run_task1_expression_analysis(test_cases['task1_expression_analysis'])
        else:
            print("\n⚠ 未找到 Task 1 测试案例")
        
        # Task 2: 等价性检查
        if 'task2_equivalence_checking' in test_cases:
            run_task2_equivalence_checking(test_cases['task2_equivalence_checking'])
        else:
            print("\n⚠ 未找到 Task 2 测试案例")
        
        print_section("测试完成")
        print(f"\n✓ LOG 文件已保存到: {log_file}")
        
    finally:
        # 恢复标准输出
        sys.stdout = tee.terminal
        tee.close()
        print(f"\n✓ 测试完成!")
        print(f"  - LOG 文件: {log_file}")


if __name__ == "__main__":
    main()
