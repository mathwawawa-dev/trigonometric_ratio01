@echo off
chcp 65001 >nul
echo.
echo  ╔══════════════════════════════════════╗
echo  ║   삼각비 마스터 — 로컬 서버 시작     ║
echo  ╚══════════════════════════════════════╝
echo.

:: Python 3 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo  [오류] Python 3 이 설치되어 있지 않습니다.
    echo  https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

echo  ✅ Python 감지 완료
echo  📡 포트 8080 에서 서버를 시작합니다...
echo  🌐 브라우저에서 자동으로 열립니다.
echo.
echo  ※ 서버를 종료하려면 이 창을 닫거나 Ctrl+C 를 누르세요.
echo.

:: 1초 후 브라우저 열기 (서버 기동 대기)
start "" /b cmd /c "timeout /t 1 >nul && start http://localhost:8080/index.html"

:: 현재 디렉토리에서 HTTP 서버 실행
python -m http.server 8080
pause
