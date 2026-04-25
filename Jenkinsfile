pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '프로젝트 경로')
    }

    stages {
        stage('QA 결과 분석 (Python)') {
            steps {
                script {
                    def basePath = params.BASE_PATH
                    
                    bat """
                    @echo off
                    echo =========================================
                    echo 1. Python 설치 여부 확인 및 자동 설치
                    echo =========================================
                    
                    :: python 명령어가 작동하는지 확인
                    python --version >nul 2>&1
                    IF %ERRORLEVEL% NEQ 0 (
                        echo [알림] 시스템에 Python이 없습니다. 자동 다운로드 및 설치를 시작합니다.
                        
                        :: 공식 파이썬 3.12 설치 파일 다운로드
                        curl -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
                        
                        echo 설치 진행 중... (약 1~2분 정도 소요됩니다)
                        :: /quiet: 창을 띄우지 않고 백그라운드 설치
                        :: PrependPath=1: 윈도우 환경 변수(PATH)에 자동 추가
                        start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
                        echo [완료] Python 설치가 성공적으로 끝났습니다!
                        
                        :: 방금 설치한 파이썬을 현재 젠킨스 세션에서 즉시 쓸 수 있도록 PATH 강제 주입
                        set PATH=%PATH%;C:\\Program Files\\Python312\\;C:\\Program Files\\Python312\\Scripts\\
                    ) ELSE (
                        echo [확인] Python이 이미 정상적으로 설치되어 있습니다.
                    )

                    echo =========================================
                    echo 2. pip 및 필수 라이브러리(openpyxl) 세팅
                    echo =========================================
                    :: 파이썬이 설치/인식되었으므로 라이브러리 유무 확인 및 설치
                    python -c "import openpyxl" 2>nul || pip install openpyxl
                    
                    echo =========================================
                    echo 3. 파이썬 스크립트 실행 (리포트 생성)
                    echo =========================================
                    
                    :: 혹시라도 Git에서 make_report.py를 못 가져온 상황을 대비한 방어 코드
                    IF NOT EXIST make_report.py (
                        echo [에러] 현재 경로에 make_report.py 파일이 없습니다!
                        exit /b 1
                    )
                    
                    :: 분리해둔 파이썬 파일 실행 (basePath를 인자로 전달)
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