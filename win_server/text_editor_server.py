#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 端文本编辑器 TCP 服务器
接收来自 Kubuntu 的文件编辑请求，调用 Sublime Text 打开文件
"""

import socket
import subprocess
import os
import json
import threading
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('text_editor_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TextEditorServer:
    def __init__(self, host='0.0.0.0', port=3112, sublime_path=r'C:\Tools\Sublime_text_4\sublime_text.exe'):
        self.host = host
        self.port = port
        self.sublime_path = sublime_path
        self.smb_mount_point = r'\\100.114.7.121\share\Desktop'
        self.running = False
        
    def convert_path(self, kubuntu_path):
        """
        将 Kubuntu 路径转换为 Windows SMB 路径
        """
        # 移除可能的 /home/username/Desktop 前缀，替换为 SMB 路径
        if kubuntu_path.startswith('/home/'):
            # 提取 Desktop 后的路径
            parts = kubuntu_path.split('/')
            try:
                desktop_index = parts.index('Desktop')
                relative_path = '/'.join(parts[desktop_index + 1:])
                windows_path = os.path.join(self.smb_mount_point, relative_path.replace('/', '\\'))
                return windows_path
            except ValueError:
                # 如果没有找到 Desktop，直接使用相对路径
                pass
        
        # 如果路径已经是相对于 Desktop 的，直接转换
        clean_path = kubuntu_path.lstrip('/')
        windows_path = os.path.join(self.smb_mount_point, clean_path.replace('/', '\\'))
        return windows_path
    
    def open_file_in_editor(self, file_path, line_number=None):
        """
        使用 Sublime Text 打开文件
        """
        try:
            # 转换路径
            windows_path = self.convert_path(file_path)
            logging.info(f"转换路径: {file_path} -> {windows_path}")
            
            # 检查文件是否存在
            if not os.path.exists(windows_path):
                logging.warning(f"文件不存在: {windows_path}")
                return False, f"文件不存在: {windows_path}"
            
            # 构建命令
            cmd = [self.sublime_path, windows_path]
            if line_number:
                cmd.extend([f"-l{line_number}"])
            
            logging.info(f"执行命令: {' '.join(cmd)}")
            
            # 启动 Sublime Text
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return True, f"成功打开文件: {windows_path}"
            
        except Exception as e:
            error_msg = f"打开文件失败: {str(e)}"
            logging.error(error_msg)
            return False, error_msg
    
    def handle_client(self, client_socket, client_address):
        """
        处理客户端连接
        """
        try:
            logging.info(f"客户端连接: {client_address}")
            
            # 接收数据
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                return
            
            logging.info(f"接收到数据: {data}")
            
            # 解析 JSON 数据
            try:
                request = json.loads(data)
                file_path = request.get('file_path', '')
                line_number = request.get('line_number', None)
                
                if not file_path:
                    response = {'success': False, 'message': '文件路径为空'}
                else:
                    success, message = self.open_file_in_editor(file_path, line_number)
                    response = {'success': success, 'message': message}
                
            except json.JSONDecodeError as e:
                response = {'success': False, 'message': f'JSON 解析错误: {str(e)}'}
                logging.error(f"JSON 解析错误: {str(e)}")
            
            # 发送响应
            response_data = json.dumps(response, ensure_ascii=False).encode('utf-8')
            client_socket.send(response_data)
            
        except Exception as e:
            logging.error(f"处理客户端请求时出错: {str(e)}")
            error_response = {'success': False, 'message': f'服务器错误: {str(e)}'}
            try:
                response_data = json.dumps(error_response, ensure_ascii=False).encode('utf-8')
                client_socket.send(response_data)
            except:
                pass
        
        finally:
            client_socket.close()
            logging.info(f"客户端断开连接: {client_address}")
    
    def start_server(self):
        """
        启动 TCP 服务器
        """
        try:
            # 检查 Sublime Text 是否存在
            if not os.path.exists(self.sublime_path):
                logging.error(f"Sublime Text 未找到: {self.sublime_path}")
                print(f"错误: Sublime Text 未找到: {self.sublime_path}")
                return
            
            # 创建 socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 绑定地址和端口
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.running = True
            logging.info(f"文本编辑器服务器启动，监听 {self.host}:{self.port}")
            print(f"文本编辑器服务器启动，监听 {self.host}:{self.port}")
            print(f"Sublime Text 路径: {self.sublime_path}")
            print(f"SMB 挂载点: {self.smb_mount_point}")
            print("按 Ctrl+C 停止服务器")
            
            while self.running:
                try:
                    # 接受客户端连接
                    client_socket, client_address = server_socket.accept()
                    
                    # 创建线程处理客户端
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logging.error(f"Socket 错误: {str(e)}")
        
        except KeyboardInterrupt:
            logging.info("收到停止信号")
        except Exception as e:
            logging.error(f"服务器启动失败: {str(e)}")
        finally:
            self.running = False
            try:
                server_socket.close()
            except:
                pass
            logging.info("服务器已停止")
            print("服务器已停止")

def main():
    # 可以通过命令行参数自定义配置
    import sys
    
    sublime_path = r'C:\Tools\Sublime_text_4\sublime_text.exe'
    if len(sys.argv) > 1:
        sublime_path = sys.argv[1]
    
    server = TextEditorServer(sublime_path=sublime_path)
    server.start_server()

if __name__ == '__main__':
    main()
