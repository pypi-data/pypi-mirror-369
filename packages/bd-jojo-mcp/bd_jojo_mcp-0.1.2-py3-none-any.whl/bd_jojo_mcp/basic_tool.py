import os

# 读取文件内容
def read_file_content(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

# 获取指定目录下，时间戳最新的、以build.log结尾的文件
def get_latest_build_log_file(directory: str) -> str:
    # 列出目录下所有以build.log结尾的文件
    build_log_files = [f for f in os.listdir(directory) if f.endswith('build.log')]
    
    # 按文件名排序，最新的在最后
    build_log_files.sort()
    
    # 返回最新的文件
    return os.path.join(directory, build_log_files[-1]) if build_log_files else None

# 读取指定目录下，时间戳最新的、以build.log结尾的文件内容
def read_latest_build_log_content(directory: str) -> str:
    latest_build_log_file = get_latest_build_log_file(directory)
    if latest_build_log_file:
        return read_file_content(latest_build_log_file)
    return ""

# 获取指定文件中，以ERROR: 开头的行
def get_error_lines(file_content: str) -> list[str]:
    return [line for line in file_content.splitlines() if line.startswith("ERROR: ")]

# 提取一行内容中，在.jojo/repos/之后、/之前的内容
def extract_repo_name(line: str) -> str:
    start_index = line.find(".jojo/repos/") + len(".jojo/repos/")
    end_index = line.find("/", start_index)
    return line[start_index:end_index]

def compress_logs(log_dir: str) -> str:
    """
    压缩指定目录下的所有日志文件为 zip 格式。
    :param log_dir: 日志文件所在目录
    :param output_path: 压缩后的输出路径
    :return: 压缩文件的路径
    """
    import os
    output_path = os.path.join(log_dir, "logs.zip")
    try:
        # 实现压缩逻辑
        import zipfile
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(log_dir):
                for file in files:
                    if file.endswith('.log'):
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), log_dir))
        return f"日志文件已压缩至：{output_path}"
    except Exception as e:
        return f"压缩日志时出错：{str(e)}"

# 获取用户的git邮箱
def get_git_user_email() -> str:
    """
    获取当前系统的 Git 用户邮箱。
    :return: Git 用户邮箱
    """
    try:
        email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
        return email
    except subprocess.CalledProcessError:
        return "未找到 Git 用户邮箱"