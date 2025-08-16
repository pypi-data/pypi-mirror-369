"""用户界面工具模块"""

import sys
import time
import select
from typing import Optional, List


def prompt_with_timeout(message: str, timeout: int = 3, default: str = "") -> str:
    """带超时的用户输入提示
    
    Args:
        message: 提示信息
        timeout: 超时时间（秒）
        default: 默认值
        
    Returns:
        用户输入或默认值
    """
    print(message, end='', flush=True)
    
    # Windows系统不支持select，使用简化版本
    if sys.platform.startswith('win'):
        return input()
    
    # Unix系统使用select实现超时
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    
    if ready:
        return sys.stdin.readline().strip()
    else:
        print(f"\n⏰ {timeout}秒超时，使用默认选择: {default}")
        return default


def select_from_list(items: List[str], prompt: str = "请选择", 
                    timeout: int = 3, default_index: int = 0) -> int:
    """从列表中选择项目，支持超时自动选择
    
    Args:
        items: 选择项列表
        prompt: 提示信息
        timeout: 超时时间（秒）
        default_index: 默认选择的索引
        
    Returns:
        选择的索引，-1表示取消
    """
    if not items:
        return -1
    
    # 显示选择列表
    print(f"\n{prompt}:")
    for i, item in enumerate(items, 1):
        marker = "⭐" if i - 1 == default_index else "  "
        print(f"{marker} {i}. {item}")
    
    # 显示提示信息
    default_display = items[default_index] if 0 <= default_index < len(items) else "无"
    message = f"\n请选择 (1-{len(items)}, 回车选择默认: {default_display}, {timeout}秒后自动选择): "
    
    try:
        user_input = prompt_with_timeout(message, timeout, str(default_index + 1))
        
        if not user_input.strip():
            # 回车选择默认
            return default_index
        
        try:
            choice = int(user_input.strip())
            if 1 <= choice <= len(items):
                return choice - 1
            else:
                print(f"❌ 无效选择: {choice}")
                return -1
        except ValueError:
            print(f"❌ 无效输入: {user_input}")
            return -1
            
    except KeyboardInterrupt:
        print("\n❌ 操作取消")
        return -1


def show_loading(message: str, duration: float = 1.0):
    """显示加载动画"""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        print(f'\r{frame} {message}', end='', flush=True)
        time.sleep(0.1)
        i += 1
    
    print(f'\r✅ {message}完成')


def confirm_action(message: str, default: bool = False) -> bool:
    """确认操作"""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{message} ({default_text}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes', '是', 'true', '1']


def print_status(message: str, status: str = "info"):
    """打印状态信息"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳"
    }
    
    icon = icons.get(status, "ℹ️")
    print(f"{icon} {message}")


def print_header(title: str):
    """打印标题头"""
    print(f"\n{'=' * 50}")
    print(f"🚀 {title}")
    print(f"{'=' * 50}")


def print_separator():
    """打印分隔线"""
    print("-" * 50)