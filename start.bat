@echo off
echo 启动 ShiningHunter - DeSmuME闪光刷取辅助工具
echo ================================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查依赖包是否安装
echo 检查依赖包...
python -c "import pynput, mss, cv2, PIL, skimage" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 启动程序
echo 启动程序...
python main.py

pause
