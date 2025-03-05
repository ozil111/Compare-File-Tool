import subprocess
import os
import sys

def run_test():
    # 获取当前脚本的绝对路径
    script_path = os.path.abspath(__file__)
    # 计算workspace路径（脚本目录的上级目录）
    workspace = os.path.dirname(os.path.dirname(script_path))
    
    # 构建完整的命令参数
    compare_script = os.path.join(workspace, "compare_text.py")
    test_file1 = os.path.join("test", "1.bdf")
    test_file2 = os.path.join("test", "1_copy.bdf")
    
    # 执行比较命令
    cmd = [
        sys.executable,
        compare_script,
        test_file1,
        test_file2
    ]
    
    # 在workspace目录下执行命令
    result = subprocess.run(
        cmd,
        cwd=workspace,
        capture_output=True,
        text=True
    )
    
    # 合并标准输出和错误输出
    full_output = result.stdout + result.stderr
    
    # 验证输出结果
    if "Files are identical." in full_output:
        print("测试通过：成功检测到'Files are identical.'")
        return True
    else:
        print("测试失败：未找到预期输出")
        print("实际输出内容：\n" + full_output)
        return False

if __name__ == "__main__":
    run_test()