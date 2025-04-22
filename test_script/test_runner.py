import json
import os
import subprocess
import sys
import re
from pathlib import Path

class JSONTestRunner:
    def __init__(self, config_file="test_cases.json"):
        self.workspace = Path(__file__).parent.parent
        self.config_path = Path(__file__).parent / config_file
        self.test_cases = []
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }

    def load_test_cases(self):
        """加载并验证测试用例配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            required_fields = ["name", "command", "args", "expected"]
            for case in config["test_cases"]:
                if not all(field in case for field in required_fields):
                    raise ValueError(f"测试用例 {case.get('name', 'unnamed')} 缺少必要字段")
                
                case["args"] = [
                    str(self.workspace / arg) if not arg.startswith("--") else arg
                    for arg in case["args"]
                ]
                self.test_cases.append(case)
                
            print(f"成功加载 {len(self.test_cases)} 个测试用例")
        except Exception as e:
            sys.exit(f"配置文件加载失败: {str(e)}")

    def run_single_test(self, case):
        """执行单个测试用例"""
        result = {
            "name": case["name"],
            "status": "failed",
            "message": ""
        }

        try:
            # 构造完整命令
            full_cmd = case["command"].split() + case["args"]
            
            # 执行命令
            process = subprocess.run(
                full_cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                check=False
            )
            
            # 合并输出
            full_output = process.stdout + process.stderr
            
            # Check for expected output patterns
            if "output_contains" in case["expected"]:
                for keyword in case["expected"]["output_contains"]:
                    if keyword not in full_output:
                        result["message"] = f"未找到关键内容: {keyword}"
                        return result
            
            # Check for regex pattern matches
            if "matches" in case["expected"]:
                for pattern in case["expected"]["matches"]:
                    if not re.search(pattern, full_output):
                        result["message"] = f"未找到匹配模式: {pattern}"
                        return result

            # 所有检查通过
            result["status"] = "passed"
            return result
            
        except Exception as e:
            result["message"] = f"执行异常: {str(e)}"
            return result

    def generate_report(self):
        """生成测试报告"""
        print("\n测试结果汇总:")
        print(f"总用例数: {self.results['total']}")
        print(f"通过数: {self.results['passed']}")
        print(f"失败数: {self.results['failed']}\n")
        
        print("详细结果:")
        for detail in self.results["details"]:
            status_icon = "✓" if detail["status"] == "passed" else "✗"
            print(f"{status_icon} {detail['name']}")
            if detail["message"]:
                print(f"   -> {detail['message']}")

    def run_all_tests(self):
        """执行全部测试用例"""
        self.load_test_cases()
        self.results["total"] = len(self.test_cases)
        
        for case in self.test_cases:
            test_result = self.run_single_test(case)
            if test_result["status"] == "passed":
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            self.results["details"].append(test_result)
            
        self.generate_report()
        return self.results["failed"] == 0

if __name__ == "__main__":
    runner = JSONTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)