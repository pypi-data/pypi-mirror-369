#!/usr/bin/env python3
import json
import os
from pathlib import Path


def get_user_input():
    """获取用户输入的API配置"""
    print("Claude API 配置工具")
    print("=" * 30)
    
    base_url = input("请输入 ANTHROPIC_BASE_URL: ").strip()
    if not base_url:
        print("错误: BASE_URL 不能为空")
        return None, None
    
    api_key = input("请输入 ANTHROPIC_API_KEY: ").strip()
    if not api_key:
        print("错误: API_KEY 不能为空")
        return None, None
    
    return base_url, api_key


def update_claude_config(base_url, api_key):
    """更新 ~/.claude/settings.json 配置文件"""
    config_dir = Path.home() / ".claude"
    config_path = config_dir / "settings.json"
    
    # 确保 .claude 目录存在
    config_dir.mkdir(exist_ok=True)
    
    # 读取现有配置或创建新配置
    config = {
        "env": {},
        "permissions": {
            "allow": [],
            "deny": []
        }
    }
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"找到现有配置文件: {config_path}")
        except json.JSONDecodeError:
            print(f"警告: 配置文件格式错误，将创建新配置")
            config = {
                "env": {},
                "permissions": {
                    "allow": [],
                    "deny": []
                }
            }
        except Exception as e:
            print(f"读取配置文件时出错: {e}")
            return False
    else:
        print(f"将创建新配置文件: {config_path}")
    
    # 确保 env 对象存在
    if "env" not in config:
        config["env"] = {}
    
    # 更新配置
    config["env"]["ANTHROPIC_BASE_URL"] = base_url
    config["env"]["ANTHROPIC_API_KEY"] = api_key
    config["apiKeyHelper"] = f"echo '{api_key}'"
    
    # 写入配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 设置文件权限 (仅所有者可读写)
        os.chmod(config_path, 0o600)
        
        print(f"✅ 配置已成功保存到 {config_path}")
        return True
    except Exception as e:
        print(f"❌ 保存配置文件时出错: {e}")
        return False


def main():
    """主函数"""
    try:
        base_url, api_key = get_user_input()
        if base_url and api_key:
            print("\n确认配置信息:")
            print(f"BASE_URL: {base_url}")
            print(f"API_KEY: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
            
            confirm = input("\n确认保存配置? (y/N): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                if update_claude_config(base_url, api_key):
                    print("\n🎉 Claude API 配置完成！")
                else:
                    print("\n💥 配置失败，请检查错误信息")
                    return 1
            else:
                print("取消保存配置")
                return 0
        else:
            print("💥 输入无效，程序退出")
            return 1
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        return 0
    except Exception as e:
        print(f"💥 程序运行出错: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())