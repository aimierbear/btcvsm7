#!/bin/bash
# BTC vs M7 相对强弱指数 Dashboard 启动脚本

cd "$(dirname "$0")"

echo "======================================"
echo "  BTC vs Magnificent 7 强弱指数"
echo "======================================"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件！"
    echo ""
    echo "请先设置 Twelve Data API Key："
    echo "1. 访问 https://twelvedata.com/pricing 注册免费账号"
    echo "2. 复制你的 API Key"
    echo "3. 在当前目录创建 .env 文件，内容如下："
    echo ""
    echo "   TWELVE_DATA_API_KEY=你的API密钥"
    echo ""
    echo "或者复制 .env.example 并修改："
    echo "   cp .env.example .env"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

echo "正在启动 Dashboard..."
echo "按 Ctrl+C 停止服务"
echo "--------------------------------------"
echo ""

# 3秒后自动打开浏览器
(sleep 3 && open "http://localhost:8501") &

# 启动 Streamlit
python3 -m streamlit run app.py --server.headless true

# 如果运行失败，保持窗口打开
if [ $? -ne 0 ]; then
    echo ""
    echo "启动失败！请检查："
    echo "1. 是否已安装依赖: pip install -r requirements.txt"
    echo "2. .env 文件中的 API Key 是否正确"
    echo ""
    read -p "按回车键退出..."
fi
