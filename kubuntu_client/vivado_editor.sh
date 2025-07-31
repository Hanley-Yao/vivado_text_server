#!/bin/bash
# Kubuntu 端文本编辑器调用脚本
# 用于 Vivado Custom Editor Definition

# 设置 Windows 服务器的 IP 地址（请根据实际情况修改）
WINDOWS_SERVER_IP="100.119.115.23"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 调用 Python 客户端
python3 "$SCRIPT_DIR/text_editor_client.py" --server "$WINDOWS_SERVER_IP" "$@"
