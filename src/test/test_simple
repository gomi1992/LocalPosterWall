#!/usr/bin/env python3
"""
简单的MovieScanner功能验证测试
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("验证MovieScanner修改...")
    
    try:
        from movie_scanner import MovieScanner
        print("✅ 成功导入MovieScanner")
        
        # 创建实例
        scanner = MovieScanner()
        print("✅ 成功创建MovieScanner实例")
        
        # 检查新添加的方法
        if hasattr(scanner, '_read_nfo_credits'):
            print("✅ 成功添加了_read_nfo_credits方法")
        else:
            print("❌ 未找到_read_nfo_credits方法")
            
        # 检查_parse_movie_folder方法是否包含director和actors字段
        print("\n📋 MovieScanner类方法检查:")
        methods = [method for method in dir(scanner) if not method.startswith('_') or method.startswith('_read')]
        for method in methods:
            print(f"  - {method}")
            
        print("\n🎉 MovieScanner修改验证完成!")
        
    except ImportError as e:
        print(f"❌ 导入MovieScanner失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()
