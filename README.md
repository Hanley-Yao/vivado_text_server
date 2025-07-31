# Vivado 文本编辑器跨平台调用系统

这个系统允许您在 Kubuntu 的 Vivado 中调用 Windows 端的 Sublime Text 编辑器。

## 系统架构

1. **Windows 端**: TCP 服务器，接收文件编辑请求
2. **Kubuntu 端**: 客户端程序，发送文件编辑请求到 Windows

## 安装和配置

### Windows 端配置

1. **确保 Python 3 已安装**
   ```cmd
   python --version
   ```

2. **启动 TCP 服务器**
   ```cmd
   cd win_server
   start_server.bat
   ```
   或手动运行：
   ```cmd
   python text_editor_server.py
   ```

3. **配置防火墙**
   - 允许端口 3112 的入站连接
   - 或者在 Windows 防火墙中允许 Python 程序

4. **验证 Sublime Text 路径**
   - 默认路径: `C:\Tools\Sublime_text_4\sublime_text.exe`
   - 如果路径不同，请修改 `text_editor_server.py` 中的 `sublime_path`

### Kubuntu 端配置

1. **复制文件到 Kubuntu**
   将 `kubuntu_client` 文件夹复制到 Kubuntu 系统

2. **设置执行权限**
   ```bash
   chmod +x vivado_editor.sh
   chmod +x text_editor_client.py
   ```

3. **修改服务器 IP 地址**
   编辑以下文件中的 IP 地址（当前设置为 100.114.7.121）：
   - `text_editor_client.py` 第 15 行
   - `vivado_editor.sh` 第 6 行

4. **测试连接**
   ```bash
   python3 text_editor_client.py /path/to/test/file.v
   ```

### Vivado 配置

1. **打开 Vivado**

2. **设置自定义编辑器**
   - 打开 Tools → Settings → Text Editor
   - 选择 "Custom Editor Definition"
   - 在 Editor 字段输入：
     ```
     /path/to/kubuntu_client/vivado_editor.sh [file name] +[line number]
     ```
   
   例如：
   ```
   /home/username/Desktop/text_server/kubuntu_client/vivado_editor.sh [file name] +[line number]
   ```

## 使用方法

1. **启动 Windows 服务器**
   在 Windows 端运行 `start_server.bat`（会一同启动C:\Xilinx\Vivado\2023.1\bin\hw_server.bat）

2. **在 Vivado 中双击文件**
   现在当您在 Vivado 中双击文件时，会自动在 Windows 的 Sublime Text 中打开

## 支持的文件路径格式

系统会自动转换以下路径格式：
- Kubuntu 路径: `/home/username/Desktop/project/file.v`
- Windows SMB 路径: `\\100.114.7.121\share\Desktop\project\file.v`

## 故障排除

### 连接问题
1. 检查网络连接
2. 验证 IP 地址设置
3. 检查防火墙设置
4. 确保 Windows 服务器正在运行

### 文件路径问题
1. 确保 SMB 共享正常工作
2. 验证文件路径映射
3. 检查文件权限

### 编辑器问题
1. 验证 Sublime Text 路径
2. 检查 Sublime Text 是否正常安装
3. 测试命令行调用

## 日志文件

- Windows 端日志: `win_server/text_editor_server.log`
- 包含连接信息、文件打开记录和错误信息

## 自定义配置

您可以修改 `config.ini` 文件来自定义：
- 服务器端口
- Sublime Text 路径
- SMB 挂载点
- IP 地址

## 扩展功能

此系统可以扩展支持：
- 其他文本编辑器（VS Code, Notepad++ 等）
- 多个 Windows 客户端
- 文件同步功能
- 更复杂的路径映射

## 安全注意事项

1. 确保只在可信网络中使用
2. 考虑添加身份验证机制
3. 限制服务器绑定地址
4. 定期检查日志文件

## 技术细节

### 通信协议
- 协议: TCP
- 端口: 3112
- 数据格式: JSON

### 消息格式
```json
{
  "file_path": "/path/to/file.v",
  "line_number": 123
}
```

### 响应格式
```json
{
  "success": true,
  "message": "成功打开文件"
}
```
