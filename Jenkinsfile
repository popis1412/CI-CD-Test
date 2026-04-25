pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '프로젝트 최상위 경로를 입력하세요.')
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
                    
                    echo =========================================
                    echo 1. Python 설치 여부 확인 및 자동 설치
                    echo =========================================
                    
                    :: python 명령어가 작동하는지 확인
                    python --version >nul 2>&1
                    
                    :: 에러코드가 0(정상)이면 설치 단계를 건너뛰고 PYTHON_EXISTS 라벨로 이동합니다.
                    IF %ERRORLEVEL% EQU 0 GOTO PYTHON_EXISTS
                    
                    echo [알림] 시스템에 Python이 없습니다. 자동 다운로드 및 설치를 시작합니다.
                    curl -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
                    
                    echo [알림] 설치 진행 중... (약 1~2분 정도 소요됩니다)
                    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
                    
                    echo [완료] Python 설치가 성공적으로 끝났습니다!
                    :: 방금 설치한 파이썬을 현재 세션에서 즉시 쓸 수 있도록 PATH 강제 주입
                    set PATH=%PATH%;C:\\Program Files\\Python312\\;C:\\Program Files\\Python312\\Scripts\\
                    
                    :PYTHON_EXISTS
                    echo [확인] Python이 정상적으로 준비되었습니다.

                    echo =========================================
                    echo 2. pip 및 필수 라이브러리(openpyxl) 세팅
                    echo =========================================
                    python -c "import openpyxl" 2>nul || pip install openpyxl
                    
                    echo =========================================
                    echo 3. 파이썬 스크립트 실행 (리포트 생성)
                    echo =========================================
                    
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