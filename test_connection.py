#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证文本编辑器系统
"""

import os
import sys
import subprocess
import time
import socket
import json

def test_server_connection(host='100.119.115.23', port=3112):
    """测试与服务器的连接"""
    print(f"测试连接到 {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✓ 服务器连接成功")
            return True
        else:
            print("✗ 无法连接到服务器")
            return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def test_client_request(host='100.114.7.121', port=3112):
    """测试客户端请求"""
    print("测试客户端请求...")
    
    try:
        # 创建测试请求
        test_request = {
            'file_path': '/home/test/Desktop/test.v',
            'line_number': 100
        }
        
        # 连接服务器
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # 发送请求
        request_data = json.dumps(test_request).encode('utf-8')
        sock.send(request_data)
        
        # 接收响应
        response_data = sock.recv(1024).decode('utf-8')
        response = json.loads(response_data)
        
        sock.close()
        
        print(f"服务器响应: {response}")
        
        if response.get('success'):
            print("✓ 请求处理成功")
        else:
            print(f"✗ 请求处理失败: {response.get('message')}")
        
        return response.get('success', False)
        
    except Exception as e:
        print(f"✗ 请求测试失败: {e}")
        return False

def main():
    print("=== Vivado 文本编辑器系统测试 ===\n")
    
    # 获取服务器地址
    server_host = input("请输入 Windows 服务器 IP 地址 (默认: 100.119.115.23): ").strip()
    if not server_host:
        server_host = '100.119.115.23'
    
    # 测试连接
    if not test_server_connection(server_host):
        print("\n请检查:")
        print("1. Windows 服务器是否正在运行")
        print("2. 防火墙设置是否正确")
        print("3. IP 地址是否正确")
        return
    
    print()
    
    # 测试请求
    test_client_request(server_host)
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    main()
