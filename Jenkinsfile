pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    stages {
        stage('QA 결과 분석 (Python)') {
            steps {
                script {
                    def basePath = params.BASE_PATH
                    
                    bat """
                    @echo off
                    :: 젠킨스 윈도우 터미널의 한글 깨짐을 방지하고 UTF-8로 강제 고정합니다.
                    chcp 65001 >nul
                    
                    :: 파이썬 스크립트가 있는 원래 작업 공간 경로를 임시로 저장해 둡니다.
                    set "WORKSPACE_DIR=%CD%"
                    
                    :: cmd 실행기를 유저 홈 디렉터리로 이동시킵니다.                    
		    cd /d "%USERPROFILE%"
                    
                    echo =========================================
                    echo 1. Python 설치 여부 확인 및 자동 설치
                    echo =========================================
                    
                    :: 파이썬이 정상 작동하면 ALREADY_EXISTS 라벨로 즉시 점프합니다.
                    python --version >nul 2>&1 && GOTO ALREADY_EXISTS
                    
                    echo [알림] 시스템에 Python이 없습니다. 자동 다운로드 및 설치를 시작합니다.
                    curl -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
                    
                    echo [알림] 설치 진행 중... (약 1~2분 정도 소요됩니다)
                    :: 권한 문제 우회를 위해 InstallAllUsers=0(현재 사용자 전용)으로 설치
                    start /wait python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
                    
                    echo [완료] Python 설치가 성공적으로 끝났습니다!
                    set "PATH=%PATH%;C:\\Program Files\\Python312\\;C:\\Program Files\\Python312\\Scripts\\"
                    set "PATH=%PATH%;%USERPROFILE%\\AppData\\Local\\Programs\\Python\\Python312\\;%USERPROFILE%\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\"
                    
                    :: 설치가 끝났으므로 ALREADY_EXISTS를 건너뛰고 바로 PYTHON_READY로 갑니다.
                    GOTO PYTHON_READY
                    
                    :ALREADY_EXISTS
                    echo [확인] 파이썬이 이미 있습니다.
                    
                    :PYTHON_READY
                    echo =========================================
                    echo 2. pip 및 필수 라이브러리(openpyxl) 세팅
                    echo =========================================
                    :: 라이브러리가 있다면 건너뛰고, 없다면 다운로드합니다. (에러 방지를 위해 python -m pip 사용)
                    python -c "import openpyxl" 2>nul || python -m pip install openpyxl
                    
                    echo =========================================
                    echo 3. 파이썬 스크립트 실행 (리포트 생성)
                    echo =========================================
                    
                    :: 다시 스크립트가 있는 원래 젠킨스 작업 공간으로 복귀합니다.
                    cd /d "%WORKSPACE_DIR%"
                    
                    IF NOT EXIST make_report.py (
                        echo [에러] 현재 경로에 make_report.py 파일이 없습니다! 깃허브에서 파일이 잘 체크아웃되었는지 확인해주세요.
                        exit /b 1
                    )
                    
                    python make_report.py "${basePath}"
                    """
                }
            }
        }
        
        stage('리포트 아카이빙') {
            steps {
                archiveArtifacts artifacts: '**/Test Results/qa_report.html', allowEmptyArchive: true
            }
        }
    }
}