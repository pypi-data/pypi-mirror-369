#!/usr/bin/env python3
"""FastCC CLI主程序"""

import sys
import subprocess
from typing import Optional
import click
from pathlib import Path

from .core.config import ConfigManager
from .utils.crypto import generate_master_key
from .utils.ui import select_from_list, print_status, print_header, show_loading


@click.group(invoke_without_command=True)
@click.option('--smart', '-s', is_flag=True, help='智能启动模式（推荐）')
@click.pass_context
def cli(ctx, smart):
    """FastCC - 快速Claude配置管理工具
    
    常用命令：
      nv                          # 智能启动（推荐）
      nv init                     # 初始化配置
      nv add <名称>               # 添加新配置
      nv list                     # 查看所有配置
      nv use <名称>               # 使用指定配置
      nv config                   # 配置管理（更改同步方式等）
      nv uninstall                # 卸载本地配置
      nv status                   # 查看状态
    """
    if ctx.invoked_subcommand is None:
        if smart:
            # 智能启动模式
            smart_launch()
        else:
            # 默认智能启动（用户友好）
            smart_launch()


def smart_launch():
    """智能快速启动Claude Code - nv fastcc的核心逻辑"""
    try:
        print_header("FastCC 智能启动")
        
        config_manager = ConfigManager()
        
        # 步骤1: 检查登录状态
        if not config_manager.user_id:
            print_status("首次使用，需要登录GitHub账户", "info")
            if not auto_initialize(config_manager):
                return
        
        # 步骤2: 初始化存储后端（如果需要）
        if not config_manager.storage_backend:
            print_status("初始化存储后端...", "loading")
            if not config_manager.initialize_storage_backend():
                print_status("存储后端初始化失败", "error")
                return
        
        # 步骤3: 同步配置
        show_loading("同步云端配置", 1.5)
        config_manager.sync_from_cloud()
        
        # 步骤4: 获取配置列表
        profiles = config_manager.list_profiles()
        if not profiles:
            print_status("暂无配置档案", "warning")
            print("请先添加配置: nv add <名称>")
            return
        
        # 步骤5: 智能选择配置
        selected_profile = smart_select_profile(config_manager, profiles)
        if not selected_profile:
            return
        
        # 步骤6: 应用配置并启动
        print_status(f"应用配置: {selected_profile.name}", "loading")
        if config_manager.apply_profile(selected_profile.name):
            launch_claude_code()
        else:
            print_status("配置应用失败", "error")
            
    except Exception as e:
        print_status(f"启动失败: {e}", "error")


def auto_initialize(config_manager: ConfigManager) -> bool:
    """自动初始化配置"""
    try:
        print_status("正在初始化GitHub认证...", "loading")
        
        if config_manager.initialize_storage_backend():
            # 尝试同步现有配置
            config_manager.sync_from_cloud()
            print_status("初始化完成！", "success")
            return True
        else:
            print_status("GitHub认证失败", "error")
            print("请检查网络连接或稍后重试")
            return False
            
    except Exception as e:
        print_status(f"初始化失败: {e}", "error")
        return False


def smart_select_profile(config_manager: ConfigManager, profiles) -> Optional:
    """智能选择配置档案"""
    try:
        # 获取默认配置
        default_profile = config_manager.get_default_profile()
        default_index = 0
        
        if default_profile:
            # 找到默认配置的索引
            for i, profile in enumerate(profiles):
                if profile.name == default_profile.name:
                    default_index = i
                    break
        
        # 构建选择列表
        profile_names = []
        for profile in profiles:
            desc = f" - {profile.description}" if profile.description else ""
            profile_names.append(f"{profile.name}{desc}")
        
        # 用户选择（3秒超时）
        selected_index = select_from_list(
            profile_names, 
            "选择配置档案", 
            timeout=3, 
            default_index=default_index
        )
        
        if selected_index >= 0:
            return profiles[selected_index]
        else:
            print_status("未选择配置", "warning")
            return None
            
    except Exception as e:
        print_status(f"选择配置失败: {e}", "error")
        return None


def quick_launch():
    """传统快速启动Claude Code"""
    try:
        config_manager = ConfigManager()
        
        # 检查是否已初始化
        if not config_manager.user_id:
            print("🚀 欢迎使用FastCC！")
            print("首次使用需要初始化配置，请运行: nv init")
            print("或者使用: nv fastcc 进行智能启动")
            return
        
        # 尝试从云端同步配置
        if config_manager.storage_backend:
            config_manager.sync_from_cloud()
        
        profiles = config_manager.list_profiles()
        if not profiles:
            print("📝 暂无配置档案，请使用 'nv add' 添加配置")
            return
        
        # 获取默认配置或让用户选择
        default_profile = config_manager.get_default_profile()
        
        if default_profile:
            # 使用默认配置
            print(f"🚀 使用默认配置: {default_profile.name}")
            if config_manager.apply_profile(default_profile.name):
                launch_claude_code()
        else:
            # 显示配置列表让用户选择
            print("📋 可用配置档案:")
            for i, profile in enumerate(profiles, 1):
                last_used = profile.last_used or "从未使用"
                if profile.last_used:
                    last_used = profile.last_used[:10]  # 只显示日期部分
                print(f"  {i}. {profile.name} - {profile.description} (最后使用: {last_used})")
            
            try:
                choice = input("\n请选择配置 (输入数字): ").strip()
                index = int(choice) - 1
                
                if 0 <= index < len(profiles):
                    selected_profile = profiles[index]
                    if config_manager.apply_profile(selected_profile.name):
                        launch_claude_code()
                else:
                    print("❌ 无效选择")
            except (ValueError, KeyboardInterrupt):
                print("❌ 操作取消")
                
    except Exception as e:
        print(f"❌ 启动失败: {e}")


def launch_claude_code():
    """启动Claude Code"""
    try:
        print("🚀 正在启动Claude Code...")
        
        # 尝试启动Claude Code
        result = subprocess.run(['claude', '--version'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Claude Code已安装，启动交互模式
            subprocess.run(['claude'])
        else:
            print("❌ 未找到Claude Code，请先安装: https://claude.ai/code")
            
    except FileNotFoundError:
        print("❌ 未找到Claude Code，请先安装: https://claude.ai/code")
    except KeyboardInterrupt:
        print("\n👋 退出Claude Code")


@cli.command()
def init():
    """初始化FastCC配置"""
    try:
        print("🔧 初始化FastCC...")
        
        config_manager = ConfigManager()
        
        # 初始化GitHub后端
        if config_manager.initialize_storage_backend():
            # 尝试从云端同步现有配置
            config_manager.sync_from_cloud()
            
            print("✅ FastCC初始化完成！")
            print("现在可以使用以下命令：")
            print("  nv add <名称>     - 添加新配置")
            print("  nv list          - 查看所有配置")
            print("  nv               - 快速启动")
        else:
            print("❌ 初始化失败")
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


@cli.command()
@click.argument('name')
@click.option('--description', '-d', default="", help='配置描述')
def add(name, description):
    """添加新的配置档案"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.user_id:
            print("❌ 请先运行 'nv init' 初始化配置")
            return
        
        # 确保存储后端已初始化
        if not config_manager.storage_backend:
            if not config_manager.initialize_storage_backend():
                print("❌ 存储后端初始化失败")
                return
        
        print(f"➕ 添加配置档案: {name}")
        
        # 获取用户输入
        base_url = input("请输入 ANTHROPIC_BASE_URL: ").strip()
        if not base_url:
            print("❌ BASE_URL 不能为空")
            return
        
        api_key = input("请输入 ANTHROPIC_API_KEY: ").strip()
        if not api_key:
            print("❌ API_KEY 不能为空")
            return
        
        if not description:
            description = input("请输入配置描述 (可选): ").strip()
        
        # 确认信息
        print(f"\n📋 配置信息:")
        print(f"  名称: {name}")
        print(f"  描述: {description or '无'}")
        print(f"  BASE_URL: {base_url}")
        print(f"  API_KEY: {api_key[:10]}...{api_key[-4:]}")
        
        confirm = input("\n确认添加? (y/N): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            if config_manager.add_profile(name, description, base_url, api_key):
                print("✅ 配置添加成功！")
            else:
                print("❌ 配置添加失败")
        else:
            print("❌ 操作取消")
            
    except KeyboardInterrupt:
        print("\n❌ 操作取消")
    except Exception as e:
        print(f"❌ 添加配置失败: {e}")


@cli.command()
def list():
    """列出所有配置档案"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.user_id:
            print("❌ 请先运行 'nv init' 初始化配置")
            return
        
        # 确保存储后端已初始化
        if not config_manager.storage_backend:
            if not config_manager.initialize_storage_backend():
                print("❌ 存储后端初始化失败")
                return
        
        # 从云端同步最新配置
        if config_manager.storage_backend:
            config_manager.sync_from_cloud()
        
        profiles = config_manager.list_profiles()
        default_name = config_manager.settings.get('default_profile')
        
        if not profiles:
            print("📝 暂无配置档案")
            print("使用 'nv add <名称>' 添加新配置")
            return
        
        print("📋 配置档案列表:")
        for profile in profiles:
            is_default = "⭐" if profile.name == default_name else "  "
            last_used = profile.last_used or "从未使用"
            if profile.last_used:
                last_used = profile.last_used[:16].replace('T', ' ')
            
            print(f"{is_default} {profile.name}")
            print(f"     描述: {profile.description or '无'}")
            print(f"     BASE_URL: {profile.base_url}")
            print(f"     最后使用: {last_used}")
            print()
            
    except Exception as e:
        print(f"❌ 列出配置失败: {e}")


@cli.command()
@click.argument('name')
def use(name):
    """使用指定配置启动Claude Code"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.user_id:
            print("❌ 请先运行 'nv init' 初始化配置")
            return
        
        # 确保存储后端已初始化
        if not config_manager.storage_backend:
            if not config_manager.initialize_storage_backend():
                print("❌ 存储后端初始化失败")
                return
        
        if config_manager.apply_profile(name):
            launch_claude_code()
        
    except Exception as e:
        print(f"❌ 使用配置失败: {e}")


@cli.command()
@click.argument('name')
def default(name):
    """设置默认配置档案"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.user_id:
            print("❌ 请先运行 'nv init' 初始化配置")
            return
        
        # 确保存储后端已初始化
        if not config_manager.storage_backend:
            if not config_manager.initialize_storage_backend():
                print("❌ 存储后端初始化失败")
                return
        
        config_manager.set_default_profile(name)
        
    except Exception as e:
        print(f"❌ 设置默认配置失败: {e}")


@cli.command()
@click.argument('name')
def remove(name):
    """删除配置档案"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.user_id:
            print("❌ 请先运行 'nv init' 初始化配置")
            return
        
        # 确保存储后端已初始化
        if not config_manager.storage_backend:
            if not config_manager.initialize_storage_backend():
                print("❌ 存储后端初始化失败")
                return
        
        profile = config_manager.get_profile(name)
        if not profile:
            print(f"❌ 配置档案 '{name}' 不存在")
            return
        
        print(f"⚠️  即将删除配置档案: {name}")
        print(f"   描述: {profile.description}")
        print(f"   BASE_URL: {profile.base_url}")
        
        confirm = input("\n确认删除? (y/N): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            config_manager.remove_profile(name)
        else:
            print("❌ 操作取消")
            
    except KeyboardInterrupt:
        print("\n❌ 操作取消")
    except Exception as e:
        print(f"❌ 删除配置失败: {e}")


@cli.command()
def sync():
    """手动同步配置"""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.user_id:
            print("❌ 请先运行 'nv init' 初始化配置")
            return
        
        # 确保存储后端已初始化
        if not config_manager.storage_backend:
            if not config_manager.initialize_storage_backend():
                print("❌ 存储后端初始化失败")
                return
        
        print("🔄 同步配置...")
        
        # 从云端同步
        if config_manager.sync_from_cloud():
            # 同步到云端
            config_manager.sync_to_cloud()
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")


@cli.command()
def fastcc():
    """智能快速启动Claude Code（推荐使用）"""
    smart_launch()


@cli.command()
def config():
    """配置FastCC设置"""
    try:
        config_manager = ConfigManager()
        
        print("⚙️  FastCC配置管理")
        print("1. 更改同步方式")
        print("2. 查看当前配置")
        print("3. 返回")
        
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            print("\n🔄 重新选择同步方式...")
            if config_manager.initialize_storage_backend(force_choose=True):
                print("✅ 同步方式已更新")
            else:
                print("❌ 更新失败")
        
        elif choice == "2":
            backend_type = config_manager.settings.get('storage_backend_type', '未设置')
            backend_name_map = {
                'github': 'GitHub跨平台同步',
                'cloud': '本地云盘同步', 
                'local': '仅本地存储'
            }
            backend_name = backend_name_map.get(backend_type, backend_type)
            
            print(f"\n📋 当前配置:")
            print(f"  同步方式: {backend_name}")
            print(f"  用户ID: {config_manager.user_id or '未设置'}")
            print(f"  配置档案数: {len(config_manager.profiles)}")
            print(f"  默认档案: {config_manager.settings.get('default_profile', '未设置')}")
            print(f"  自动同步: {'开启' if config_manager.settings.get('auto_sync') else '关闭'}")
        
        elif choice == "3":
            return
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n❌ 操作取消")
    except Exception as e:
        print(f"❌ 配置失败: {e}")


@cli.command()
def uninstall():
    """卸载FastCC本地配置"""
    try:
        print("🗑️  FastCC本地配置卸载")
        print("")
        print("⚠️  此操作将删除：")
        print("   - 所有本地配置文件 (~/.fastcc/)")
        print("   - Claude设置文件 (~/.claude/settings.json)")
        print("")
        print("✅ 保留内容：")
        print("   - 云端配置数据（其他设备仍可使用）")
        print("   - FastCC程序本身")
        print("")
        
        # 双重确认
        confirm1 = input("确认卸载本地配置？(输入 'yes' 确认): ").strip()
        if confirm1.lower() != 'yes':
            print("❌ 操作取消")
            return
        
        print("")
        confirm2 = input("最后确认：真的要删除所有本地配置吗？(输入 'DELETE' 确认): ").strip()
        if confirm2 != 'DELETE':
            print("❌ 操作取消")
            return
        
        print("")
        print("🔄 正在卸载本地配置...")
        
        config_manager = ConfigManager()
        if config_manager.uninstall_local():
            print("")
            print("🎉 FastCC本地配置卸载完成！")
            print("")
            print("💡 后续操作：")
            print("   - 重新使用：运行 'nv init' 重新初始化")
            print("   - 完全移除：使用包管理器卸载 FastCC")
        else:
            print("❌ 卸载过程中出现错误")
            
    except KeyboardInterrupt:
        print("\n❌ 操作取消")
    except Exception as e:
        print(f"❌ 卸载失败: {e}")


@cli.command()
def status():
    """显示FastCC状态"""
    try:
        config_manager = ConfigManager()
        
        print("📊 FastCC状态:")
        print(f"  用户ID: {config_manager.user_id or '未初始化'}")
        print(f"  存储后端: {config_manager.storage_backend.backend_name if config_manager.storage_backend else '未配置'}")
        print(f"  配置档案数量: {len(config_manager.profiles)}")
        print(f"  默认配置: {config_manager.settings.get('default_profile', '未设置')}")
        print(f"  自动同步: {'开启' if config_manager.settings.get('auto_sync') else '关闭'}")
        print(f"  加密存储: {'开启' if config_manager.settings.get('encryption_enabled') else '关闭'}")
        
        # 检查Claude Code状态
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"  Claude Code: {version}")
            else:
                print("  Claude Code: 未安装")
        except FileNotFoundError:
            print("  Claude Code: 未安装")
            
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")


def main():
    """主入口函数"""
    try:
        cli()
    except KeyboardInterrupt:
        print("\n👋 再见！")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()