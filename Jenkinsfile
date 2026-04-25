pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    stages {
        stage('QA 결과 분석 (Python 신규 설치)') {
            steps {
                script {
                    def basePath = params.BASE_PATH
                    // 1. 우리가 목표로 하는 절대 경로 정의 (가장 찾기 쉬운 경로)
                    def PYTHON_HOME = "C:\\Python312"
                    def PYTHON_EXE = "${PYTHON_HOME}\\python.exe"
                    
                    bat """
                    @echo off
                    chcp 65001 >nul
                    
                    echo =========================================
                    echo 1. Python 파일 존재 확인 및 winget 설치
                    echo =========================================
                    
                    :: 파일이 진짜로 없는지 체크
                    if exist "${PYTHON_EXE}" (
                        echo [로그] 파이썬 파일이 이미 존재합니다.
                        goto PYTHON_READY
                    )

                    echo [알림] python.exe 파일이 없습니다. winget으로 설치를 시작합니다.
                    
                    :: winget으로 설치 (정확한 ID 사용)
                    :: --location: 설치 경로를 우리가 원하는 곳으로 강제 지정
                    :: --silent: 백그라운드에서 조용히 설치
                    winget install --id Python.Python.3.12 -e --silent --accept-source-agreements --accept-package-agreements --location "${PYTHON_HOME}"
                    
                    :: 설치 직후 파일이 생겼는지 최종 확인
                    if not exist "${PYTHON_EXE}" (
                        echo [에러] winget 설치 후에도 "${PYTHON_EXE}" 파일을 찾을 수 없습니다.
                        exit /b 1
                    )
                    
                    echo [완료] 파이썬 파일이 생성되었습니다!

                    :PYTHON_READY
                    echo =========================================
                    echo 2. 라이브러리(openpyxl) 세팅
                    echo =========================================
                    :: 환경 변수를 믿지 않고, 방금 확인한 절대 경로의 python.exe를 직접 호출합니다.
                    "${PYTHON_EXE}" -m pip install --upgrade pip >nul 2>&1
                    "${PYTHON_EXE}" -m pip install openpyxl
                    
                    echo =========================================
                    echo 3. 정량적 리포트 생성 스크립트 실행
                    echo =========================================
                    :: 스크립트 실행 시에도 반드시 절대 경로를 사용합니다.
                    "${PYTHON_EXE}" make_report.py "${basePath}"
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