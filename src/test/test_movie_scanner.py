#!/usr/bin/env python3
"""
MovieScanner测试脚本

验证修改后的MovieScanner是否能正确提取导演和演员信息。
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from movie_scanner import MovieScanner

def test_movie_scanner():
    """测试MovieScanner的导演和演员信息提取功能"""
    print("开始测试MovieScanner导演和演员信息提取功能...")
    
    # 创建MovieScanner实例
    scanner = MovieScanner()
    
    # 测试_read_nfo_credits方法
    print("\n1. 测试_read_nfo_credits方法...")
    
    # 创建一个测试用的电影文件夹和NFO文件
    test_folder = Path("test_movie_folder")
    test_nfo_path = test_folder / "test.nfo"
    
    # 创建测试用的NFO文件内容
    test_nfo_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
  <title>测试电影</title>
  <year>2023</year>
  <rating>8.5</rating>
  <director>张三</director>
  <director>李四</director>
  <actor>
    <name>王五</name>
  </actor>
  <actor>
    <name>赵六</name>
  </actor>
  <actor>孙七</actor>
</movie>"""
    
    try:
        # 创建测试文件夹和文件
        test_folder.mkdir(exist_ok=True)
        with open(test_nfo_path, 'w', encoding='utf-8') as f:
            f.write(test_nfo_content)
        
        print(f"创建测试文件夹: {test_folder}")
        print(f"创建测试NFO文件: {test_nfo_path}")
        
        # 测试读取导演和演员信息
        credits = scanner._read_nfo_credits(test_folder)
        
        if credits:
            print(f"✅ 成功提取导演和演员信息:")
            print(f"   导演: {credits['director']}")
            print(f"   演员: {credits['actors']}")
            
            # 验证结果
            expected_directors = ['张三', '李四']
            expected_actors = ['王五', '赵六', '孙七']
            
            if credits['director'] == expected_directors:
                print("✅ 导演信息提取正确")
            else:
                print(f"❌ 导演信息提取错误: 期望 {expected_directors}, 得到 {credits['director']}")
            
            if credits['actors'] == expected_actors:
                print("✅ 演员信息提取正确")
            else:
                print(f"❌ 演员信息提取错误: 期望 {expected_actors}, 得到 {credits['actors']}")
        else:
            print("❌ 未能提取到导演和演员信息")
    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
    
    finally:
        # 清理测试文件
        try:
            if test_nfo_path.exists():
                test_nfo_path.unlink()
            if test_folder.exists():
                test_folder.rmdir()
            print(f"清理测试文件完成")
        except Exception as e:
            print(f"清理测试文件时出现错误: {str(e)}")

def test_complete_movie_info():
    """测试完整的电影信息提取，包含导演和演员"""
    print("\n2. 测试完整的电影信息提取...")
    
    # 创建一个完整的测试电影文件夹
    test_movie_folder = Path("TestMovie (2023)")
    test_nfo_path = test_movie_folder / "test.nfo"
    test_video_path = test_movie_folder / "test_video.mp4"
    
    test_nfo_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
  <title>测试电影</title>
  <year>2023</year>
  <rating>8.5</rating>
  <director>导演甲</director>
  <director>导演乙</director>
  <actor>
    <name>演员A</name>
  </actor>
  <actor>
    <name>演员B</name>
  </actor>
  <actor>
    <name>演员C</name>
  </actor>
</movie>"""
    
    try:
        # 创建测试文件夹和文件
        test_movie_folder.mkdir(exist_ok=True)
        with open(test_nfo_path, 'w', encoding='utf-8') as f:
            f.write(test_nfo_content)
        with open(test_video_path, 'w') as f:
            f.write("test video content")
        
        print(f"创建测试电影文件夹: {test_movie_folder}")
        print(f"创建测试NFO文件: {test_nfo_path}")
        print(f"创建测试视频文件: {test_video_path}")
        
        # 创建MovieScanner实例
        scanner = MovieScanner()
        
        # 解析电影文件夹
        movie_info = scanner._parse_movie_folder(test_movie_folder)
        
        if movie_info:
            print("✅ 成功解析电影文件夹:")
            print(f"   标题: {movie_info['title']}")
            print(f"   年份: {movie_info['year']}")
            print(f"   评分: {movie_info['rating']}")
            print(f"   导演: {movie_info['director']}")
            print(f"   演员: {movie_info['actors']}")
            print(f"   视频路径: {movie_info['video_path']}")
            
            # 验证结果
            expected_directors = ['导演甲', '导演乙']
            expected_actors = ['演员A', '演员B', '演员C']
            
            if movie_info['director'] == expected_directors:
                print("✅ 完整电影信息中导演信息提取正确")
            else:
                print(f"❌ 完整电影信息中导演信息提取错误")
            
            if movie_info['actors'] == expected_actors:
                print("✅ 完整电影信息中演员信息提取正确")
            else:
                print(f"❌ 完整电影信息中演员信息提取错误")
                
        else:
            print("❌ 未能解析电影文件夹")
    
    except Exception as e:
        print(f"❌ 完整测试过程中出现错误: {str(e)}")
    
    finally:
        # 清理测试文件
        try:
            files_to_remove = [test_nfo_path, test_video_path]
            for file_path in files_to_remove:
                if file_path.exists():
                    file_path.unlink()
            if test_movie_folder.exists():
                test_movie_folder.rmdir()
            print(f"清理测试文件完成")
        except Exception as e:
            print(f"清理测试文件时出现错误: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("MovieScanner导演和演员信息提取功能测试")
    print("=" * 60)
    
    test_movie_scanner()
    test_complete_movie_info()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
