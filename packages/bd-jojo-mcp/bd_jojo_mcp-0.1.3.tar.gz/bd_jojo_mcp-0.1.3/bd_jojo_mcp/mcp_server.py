# mcp_server.py
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz
# 创建一个MCP服务器实例
# Demo为服务器名称，用于标识这个MCP服务
mcp = FastMCP("Demo")

# 协议原语 ：MCP 定义了三大类“原语”
# Resources（资源），资源相当于静态数据块
# Tools（工具），资源相当于静态数据块
# Prompts（提示词模板），提示词模板是一些预设的对话或工作流程。

# 添加一个将当前workspace的JoJo工具链升级的函数，可接受DEV/PPE/RELEASE三个参数，分别对应不同的环境
@mcp.tool()
def upgrade_jojo_toolchain(workspace_dir: str, env: str) -> str:
    """
    将当前workspace的JoJo工具链升级到指定环境
    :param workspace_dir: 当前workspace目录
    :param env: 环境，DEV/PPE/RELEASE
    :return: 升级命令的执行结果
    """
    import os
    import shutil
    import subprocess
    # 1. 检查workspace_dir是否存在
    if not os.path.exists(workspace_dir):
        return "workspace_dir不存在"
    # 2. 检查env是否合法
    if env not in ["DEV", "PPE", "RELEASE"]:
        return "env参数错误，必须为DEV/PPE/RELEASE"
    # 3. 执行mbox jojo setup命令，并且返回其输出值
    try:
        # 切换到workspace目录
        original_dir = os.getcwd()
        os.chdir(workspace_dir)
        
        # 执行mbox jojo setup命令
        cmd = ["mbox", "jojo", "setup"]
        
        # 设置环境变量
        env_vars = os.environ.copy()
        if env == "DEV":
            env_vars["JOJO_ENABLE_DEV"] = "true"
        elif env == "PPE":
            env_vars["JOJO_ENABLE_PPE"] = "true"

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env_vars)
        
        # 恢复原始目录
        os.chdir(original_dir)
        
        # 返回执行结果
        if result.returncode == 0:
            return f"JoJo工具链升级成功！\n环境：{env}\n输出：{result.stdout}"
        else:
            return f"JoJo工具链升级失败！\n环境：{env}\n错误：{result.stderr}"
    
    except subprocess.TimeoutExpired:
        os.chdir(original_dir)
        return "命令执行超时（超过5分钟）"
    except Exception as e:
        os.chdir(original_dir)
        return f"执行命令时发生错误：{str(e)}"

# 添加一个汇总当前workspace所有相关日志的函数
# 汇总并打包当前workspace所有相关的日志，包括当天的BuildService日志、XcodeMate日志、install日志、build日志
@mcp.tool()
def collect_logs(workspace_dir: str) -> str:
    """
    汇总并打包当前workspace所有相关的日志，包括当天的BuildService日志、XcodeMate日志、install日志、build日志
    :param workspace_dir: 当前workspace目录
    :return: 压缩文件的路径
    """
    import os
    import shutil
    import zipfile
    from datetime import datetime
    
    # BuildService日志路径为：/Users/bytedance/.jojo/Logs/BuildServiceLogs/default.log
    # XcodeMate日志路径为：/Users/bytedance/.jojo/Logs/XcodeMate/Mate.log
    # install和build日志路径为: workspace_dir/Aweme/Aweme/.jojo/logs/当天日期，如2025-08-12
    
    try:
        # 获取当前日期，格式为YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 创建临时日志收集目录
        log_collection_dir = os.path.join(workspace_dir, "collected_logs")
        if os.path.exists(log_collection_dir):
            shutil.rmtree(log_collection_dir)
        os.makedirs(log_collection_dir)
        
        # 1. 收集BuildService日志
        buildservice_log_path = "/Users/bytedance/.jojo/Logs/BuildServiceLogs/default.log"
        if os.path.exists(buildservice_log_path):
            buildservice_dir = os.path.join(log_collection_dir, "BuildService")
            os.makedirs(buildservice_dir)
            shutil.copy2(buildservice_log_path, os.path.join(buildservice_dir, "default.log"))
        
        # 2. 收集XcodeMate日志
        xcodemate_log_path = "/Users/bytedance/.jojo/Logs/XcodeMate/Mate.log"
        if os.path.exists(xcodemate_log_path):
            xcodemate_dir = os.path.join(log_collection_dir, "XcodeMate")
            os.makedirs(xcodemate_dir)
            shutil.copy2(xcodemate_log_path, os.path.join(xcodemate_dir, "Mate.log"))
        
        # 3. 收集install和build日志
        workspace_logs_path = os.path.join(workspace_dir, "Aweme", ".jojo", "logs", current_date)
        if os.path.exists(workspace_logs_path):
            workspace_logs_dir = os.path.join(log_collection_dir, "workspace_logs")
            shutil.copytree(workspace_logs_path, workspace_logs_dir)
        
        # 4. 压缩所有收集的日志
        zip_filename = f"jojo_logs_{current_date}.zip"
        zip_path = os.path.join(workspace_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(log_collection_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, log_collection_dir)
                    zipf.write(file_path, arcname)
        
        # 清理临时目录
        shutil.rmtree(log_collection_dir)
        
        return f"日志收集完成！\n压缩文件路径：{zip_path}\n包含日志：\n- BuildService日志：{buildservice_log_path if os.path.exists(buildservice_log_path) else '未找到'}\n- XcodeMate日志：{xcodemate_log_path if os.path.exists(xcodemate_log_path) else '未找到'}\n- 工作空间日志：{workspace_logs_path if os.path.exists(workspace_logs_path) else '未找到'}"
    
    except Exception as e:
        return f"收集日志时发生错误：{str(e)}"

# 添加一个将当前最新的编译日志中报错的组件名提取出来的函数
# 获取最新一次编译日志中报错的组件名
@mcp.tool()
def get_error_repo_name(workspace_dir: str) -> str:
    """
    获取最新一次编译日志中报错的组件名
    return: 报错的组件名
    """
    import os
    current_date = datetime.now().strftime("%Y-%m-%d")
    workspace_logs_path = os.path.join(workspace_dir, "Aweme", ".jojo", "logs", current_date)
    build_log_content = basic_tool.read_latest_build_log_content(workspace_logs_path)
    error_lines = basic_tool.get_error_lines(build_log_content)
    if error_lines:
        # 找到所有的repo_name
        repo_names = [basic_tool.extract_repo_name(line) for line in error_lines]
        return f"报错的组件有：{', '.join(repo_names)}"
    return "未找到报错组件"


# 添加一个加法工具函数
# @MCP.tool()装饰器将这个函数注册为MCP工具
#获取当前时间的工具
@mcp.tool()
async def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取指定时区的当前时间（默认北京时间），无需任何输入参数。
    示例调用场景：
    - "现在几点了？"
    - "当前北京时间是多少？"
    - "告诉我现在的时间"
    
    :return: 格式化后的时间字符串，包含时区信息
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return f"⏰ 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')} ({tz.zone})"
    except pytz.UnknownTimeZoneError:
        return f"⚠️ 无效时区：{timezone}"

# 添加一个动态问候语资源
# @MCP.resource()装饰器将这个函数注册为MCP资源
@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """生成个性化问候语"""
    return f"Hello, {name}!"

def main():
    mcp.run()

# 启动MCP服务器
if __name__ == "__main__":
    main()
    