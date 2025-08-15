def clean_command(command: str) -> str:
    """清理命令字符串"""
    # 移除可能的引号和多余空格
    command = command.strip()
    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]
    if command.startswith("'") and command.endswith("'"):
        command = command[1:-1]
    return command.strip()
