#!/bin/bash

# 簡單的 HTTP 伺服器啟動腳本

echo "正在啟動前端伺服器..."
echo "請在瀏覽器開啟 http://localhost:8080"
echo "按 Ctrl+C 停止伺服器"
echo ""

# 檢查 Python 版本
if command -v python3 &> /dev/null; then
    python3 -m http.server 8080
elif command -v python &> /dev/null; then
    python -m http.server 8080
else
    echo "錯誤：找不到 Python，請安裝 Python 或使用其他方法啟動伺服器"
    exit 1
fi

