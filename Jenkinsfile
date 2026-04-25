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
                    chcp 65001 >nul
                    
                    echo =========================================
                    echo 1. Python 설치 여부 확인 및 자동 설치
                    echo =========================================
                    
                    :: 방법 1: 현재 PATH에서 확인
                    python --version >nul 2>&1
                    IF %ERRORLEVEL% EQU 0 (
                        echo [확인] 파이썬이 이미 있습니다. (PATH 인식)
                        GOTO PYTHON_READY
                    )

                    :: 방법 2: 윈도우 표준 설치 경로에 파일이 직접 존재하는지 확인
                    IF EXIST "C:\\Program Files\\Python312\\python.exe" (
                        echo [확인] 파이썬이 이미 있습니다. (C:\\Program Files)
                        set "PATH=%PATH%;C:\\Program Files\\Python312\\;C:\\Program Files\\Python312\\Scripts\\"
                        GOTO PYTHON_READY
                    )
                    
                    :: 위 방법들로 확인이 안 되면 설치 진행 (winget 사용)
                    echo [알림] 파이썬을 찾을 수 없습니다. winget을 통해 설치를 시도합니다.
                    
                    :: winget은 최신 윈도우에 내장된 패키지 매니저입니다.
                    :: --exact: 정확한 이름 찾기, --silent: 조용히 설치
                    winget install --id Python.Python.3.12 --exact --silent --accept-source-agreements --accept-package-agreements
                    
                    IF %ERRORLEVEL% NEQ 0 (
                        echo [에러] winget 설치에 실패했습니다. 수동 설치가 필요할 수 있습니다.
                        exit /b 1
                    )

                    echo [완료] Python 설치가 끝났습니다. 세션을 업데이트합니다.
                    :: 설치 직후에는 PATH가 바로 반영 안 될 수 있으므로 수동으로 추가
                    set "PATH=%PATH%;C:\\Program Files\\Python312\\;C:\\Program Files\\Python312\\Scripts\\"

                    :PYTHON_READY
                    echo [로그] 다음 단계를 진행합니다.

                    echo =========================================
                    echo 2. 라이브러리(openpyxl) 세팅
                    echo =========================================
                    python -m pip install --upgrade pip >nul 2>&1
                    python -c "import openpyxl" 2>nul || python -m pip install openpyxl
                    
                    echo =========================================
                    echo 3. 파이썬 스크립트 실행
                    echo =========================================
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