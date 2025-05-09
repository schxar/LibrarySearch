
@echo off
:: MySQL自动安装脚本
:: 下载并安装MySQL社区版

:: 设置变量
set MYSQL_VERSION=8.0.36
set MYSQL_INSTALLER=mysql-installer-community-%MYSQL_VERSION%.msi
set DOWNLOAD_URL=https://dev.mysql.com/get/Downloads/MySQLInstaller/%MYSQL_INSTALLER%

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 请以管理员身份运行此脚本
    pause
    exit /b
)

:: 下载MySQL安装程序
echo 正在下载MySQL安装程序...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%DOWNLOAD_URL%', '%MYSQL_INSTALLER%')"

:: 安装MySQL
echo 正在安装MySQL...
msiexec /i %MYSQL_INSTALLER% /quiet /qn /norestart ^
    ADDLOCAL=Server,Client ^
    INSTALLDIR="C:\Program Files\MySQL\MySQL Server 8.0" ^
    DATADIR="C:\ProgramData\MySQL\MySQL Server 8.0\Data" ^
    SERVERROOTPASSWORD=13380008373

:: 添加MySQL到系统PATH
setx PATH "%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin" /M

echo MySQL安装完成!
echo 用户名: root
echo 密码: 13380008373
pause
