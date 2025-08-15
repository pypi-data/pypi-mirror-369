#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse

from autoterminal.config.loader import ConfigLoader
from autoterminal.config.manager import ConfigManager
from autoterminal.llm.client import LLMClient
from autoterminal.utils.helpers import clean_command

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AutoTerminal - 智能终端工具')
    parser.add_argument('user_input', nargs='*', help='用户输入的自然语言命令')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--base-url', help='Base URL')
    parser.add_argument('--model', help='模型名称')
    
    args = parser.parse_args()
    
    # 合并用户输入
    user_input = ' '.join(args.user_input).strip()
    
    # 加载配置
    config_loader = ConfigLoader()
    config = config_loader.get_config()
    
    # 命令行参数优先级最高
    if args.api_key:
        config['api_key'] = args.api_key
    if args.base_url:
        config['base_url'] = args.base_url
    if args.model:
        config['model'] = args.model
    
    # 如果配置不完整，使用配置管理器初始化
    config_manager = ConfigManager()
    if not all([config.get('api_key'), config.get('base_url'), config.get('model')]):
        config = config_manager.get_or_create_config()
        if not config:
            print("错误: 缺少必要的配置参数，请通过命令行参数或配置文件提供API密钥、Base URL和模型名称。")
            return 1
    # 如果有命令行参数输入，直接处理
    if user_input:
        # 初始化LLM客户端
        try:
            llm_client = LLMClient(config)
        except Exception as e:
            print(f"LLM客户端初始化失败: {e}")
            return 1
        
        # 调用LLM生成命令
        try:
            generated_command = llm_client.generate_command(user_input)
            cleaned_command = clean_command(generated_command)
            
            # 优化输出格式
            print(f"\033[1;32m$\033[0m {cleaned_command}")
            print("\033[1;37mPress Enter to execute...\033[0m")
            
            # 等待用户回车确认执行
            input()
            
            # 在用户的环境中执行命令
            os.system(cleaned_command)
            
        except Exception as e:
            print(f"命令生成失败: {e}")
            return 1
            
        return 0
    else:
        print("错误: 请提供要执行的命令，例如: python main.py \"查看当前目录\"")
        return 1

if __name__ == "__main__":
    sys.exit(main())
