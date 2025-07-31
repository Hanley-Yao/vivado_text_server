#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kubuntu 端文本编辑器客户端
连接到 Windows TCP 服务器，请求打开文件
用于 Vivado Custom Editor Definition
"""

import socket
import json
import sys
import os
import argparse
import re

class TextEditorClient:
    def __init__(self, server_host='0.0.0.0', server_port=3112):
        # 注意：这里使用 Windows 机器的 IP 地址
        # 您需要根据实际情况修改这个 IP 地址
        self.server_host = server_host
        self.server_port = server_port
    
    def parse_vivado_args(self, args):
        """
        解析 Vivado 传递的参数
        Vivado 格式可能是: [file_name] +[line_number] 或 [file_name] -l[line_number]
        """
        file_path = None
        line_number = None
        
        for i, arg in enumerate(args):
            if arg.startswith('+'):
                # Vivado VI 格式: +行号
                try:
                    line_number = int(arg[1:])
                except ValueError:
                    pass
            elif arg.startswith('-l'):
                # Sublime 格式: -l行号
                try:
                    line_number = int(arg[2:])
                except ValueError:
                    pass
            elif not arg.startswith('-') and not arg.startswith('+'):
                # 文件路径（不以 - 或 + 开头）
                if file_path is None:
                    file_path = arg
        
        return file_path, line_number
    
    def send_request(self, file_path, line_number=None):
        """
        向 Windows 服务器发送文件打开请求
        """
        try:
            # 创建 socket 连接
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)  # 10秒超时
            
            # 连接到服务器
            client_socket.connect((self.server_host, self.server_port))
            
            # 准备请求数据
            request = {
                'file_path': file_path,
                'line_number': line_number
            }
            
            # 发送请求
            request_data = json.dumps(request, ensure_ascii=False).encode('utf-8')
            client_socket.send(request_data)
            
            # 接收响应
            response_data = client_socket.recv(1024).decode('utf-8')
            response = json.loads(response_data)
            
            return response
            
        except socket.timeout:
            return {'success': False, 'message': '连接超时'}
        except ConnectionRefusedError:
            return {'success': False, 'message': '连接被拒绝，请检查 Windows 服务器是否运行'}
        except Exception as e:
            return {'success': False, 'message': f'连接错误: {str(e)}'}
        finally:
            try:
                client_socket.close()
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description='Kubuntu 文本编辑器客户端')
    parser.add_argument('--server', default='100.114.7.121', help='Windows 服务器 IP 地址')
    parser.add_argument('--port', type=int, default=3112, help='服务器端口')
    parser.add_argument('file', nargs='?', help='要打开的文件路径')
    parser.add_argument('line', nargs='?', help='行号（可选）')
    
    # 如果没有提供参数，使用 sys.argv 的剩余部分
    if len(sys.argv) == 1:
        print("用法:")
        print("  python3 text_editor_client.py <文件路径> [行号]")
        print("  python3 text_editor_client.py <文件路径> +<行号>")
        print("  python3 text_editor_client.py <文件路径> -l<行号>")
        print("")
        print("示例:")
        print("  python3 text_editor_client.py /home/user/Desktop/test.v")
        print("  python3 text_editor_client.py /home/user/Desktop/test.v +100")
        print("  python3 text_editor_client.py /home/user/Desktop/test.v -l100")
        return
    
    # 解析命令行参数
    args = parser.parse_args()
    
    client = TextEditorClient(args.server, args.port)
    
    # 如果通过 argparse 获得了文件路径
    if args.file:
        file_path = args.file
        line_number = None
        
        if args.line:
            try:
                # 尝试解析行号
                if args.line.startswith('+'):
                    line_number = int(args.line[1:])
                elif args.line.startswith('-l'):
                    line_number = int(args.line[2:])
                else:
                    line_number = int(args.line)
            except ValueError:
                pass
    else:
        # 从 sys.argv 解析 Vivado 格式的参数
        vivado_args = sys.argv[1:]  # 跳过脚本名称
        
        # 过滤掉已知的参数
        filtered_args = []
        i = 0
        while i < len(vivado_args):
            arg = vivado_args[i]
            if arg in ['--server', '--port']:
                i += 2  # 跳过参数名和值
            elif arg.startswith('--'):
                i += 1  # 跳过长选项
            else:
                filtered_args.append(arg)
                i += 1
        
        file_path, line_number = client.parse_vivado_args(filtered_args)
    
    if not file_path:
        print("错误: 未指定文件路径")
        return
    
    # 转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    print(f"请求打开文件: {file_path}")
    if line_number:
        print(f"跳转到行号: {line_number}")
    
    # 发送请求
    response = client.send_request(file_path, line_number)
    
    # 处理响应
    if response['success']:
        print(f"成功: {response['message']}")
    else:
        print(f"失败: {response['message']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
