import os
import sys
import re
import platform
import subprocess
import logging


def get_version_tag():
    version_file = "version"
    last_version = ""
    updated = False

    # Check if the version file exists and read its content
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as file:
                content = file.read()
                last_version = content.strip()
        except Exception as e:
            return "", False, e

    # Prompt the user to enter a new version number
    try:
        current_version = input(
            f"Enter version number (current: {last_version}):\n").strip()
    except Exception as e:
        return "", False, e

    if current_version:
        updated = last_version != current_version
        last_version = current_version

        if not re.match(r"^\d+\.\d+\.\d+$", current_version):
            return "", False, f"版本号{current_version}格式不正确。应为 x.y.z, 例如: 1.2.3"

    # If the version was updated, write the new version back to the file
    if updated:
        try:
            with open(version_file, 'w') as file:
                file.write(last_version)
        except Exception as e:
            return "", False, e

    return last_version, updated, None


def run(args=None):
    """调用工具的入口，兼容 MacOS 和 Windows 多平台多架构"""
    binary_name = "deploy"  # 默认的二进制文件名称

    # 获取操作系统和架构信息
    system = platform.system().lower()  # 操作系统名称 (windows, darwin, linux)
    arch = platform.machine().lower()   # CPU 架构 (x86_64, arm64, etc.)

    # 根据操作系统和架构拼接二进制文件名
    if system == "windows":
        binary_name += f"_windows_{arch}.exe"
    elif system == "darwin":  # MacOS 的系统名是 darwin
        binary_name += f"_macos_{arch}"
    elif system == "linux":
        binary_name += f"_linux_{arch}"
    else:
        logging.error(f"Unsupported operating system: {system}")
        return

    # 获取二进制文件路径
    binary_path = os.path.join(os.path.dirname(__file__), binary_name)

    # 检查二进制文件是否存在
    if not os.path.exists(binary_path):
        logging.error(f"Binary file not found: {binary_path}")
        return

    # 构建并运行命令
    version_tag, upgrade, err = get_version_tag()
    if err:
        logging.error(err)
        return

    args = ["-v", version_tag, "-u" if upgrade else ""]
    command = [binary_path] + (args or [])
    print("Args:", args)
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 实时读取标准输出
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            elif process.poll() is not None:
                break

        # 捕获剩余的标准错误输出
        stderr = process.stderr.read()
        if stderr:
            print(stderr.strip(), file=sys.stderr)

        return_code = process.poll()
        if return_code != 0:
            print(f"Command exited with {return_code}")
            sys.exit(return_code)

        # result = subprocess.run(
        #     command,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True,
        #     check=True,  # 自动抛出非零退出码异常
        #     timeout=10,  # 设置超时时间
        # )
        # print("Command executed successfully.")
        # print("STDOUT:", result.stdout)
        # print("STDERR:", result.stderr)
        # return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("Error: Command timed out.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}", file=sys.stderr)
