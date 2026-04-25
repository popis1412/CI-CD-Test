pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    stages {
        stage('QA 결과 분석 (Python 강제 설치)') {
            steps {
                script {
                    def basePath = params.BASE_PATH
                    // 젠킨스 작업 공간 내부에 파이썬을 설치하여 권한 문제를 피합니다.
                    def PYTHON_HOME = "${WORKSPACE}\\Python312"
                    def PYTHON_EXE = "${PYTHON_HOME}\\python.exe"
                    
                    bat """
                    @echo off
                    chcp 65001 >nul
                    
                    echo =========================================
                    echo 1. Python 파일 직접 검사 및 강제 설치
                    echo =========================================
                    
                    if exist "${PYTHON_EXE}" (
                        echo [로그] 파이썬이 이미 지정된 경로에 존재합니다.
                        goto PYTHON_READY
                    )

                    echo [알림] 파이썬이 없습니다. 공식 서버에서 직접 다운로드합니다.
                    
                    :: curl은 윈도우 10/11에 무조건 내장되어 있습니다.
                    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
                    
                    if not exist python_installer.exe (
                        echo [에러] 설치 파일 다운로드에 실패했습니다. 네트워크 연결을 확인하세요.
                        exit /b 1
                    )

                    echo [알림] 설치 진행 중... (약 1분 소요)
                    :: winget 대신 직접 exe를 실행합니다. 
                    :: /quiet: 화면 표시 없음, InstallAllUsers=0: 관리자 권한 없이 현재 폴더에 설치 가능하도록 함
                    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=0 TargetDir="${PYTHON_HOME}" Include_test=0
                    
                    :: 설치 후 설치 파일 삭제
                    del python_installer.exe

                    if not exist "${PYTHON_EXE}" (
                        echo [에러] 설치 시도 후에도 python.exe를 찾을 수 없습니다.
                        exit /b 1
                    )
                    
                    echo [완료] 파이썬 설치 성공! 경로: ${PYTHON_HOME}

                    :PYTHON_READY
                    echo =========================================
                    echo 2. 라이브러리(openpyxl) 세팅
                    echo =========================================
                    :: 환경 변수 무시, 설치된 실행 파일을 직접 찔러서 호출
                    "${PYTHON_EXE}" -m pip install --upgrade pip
                    "${PYTHON_EXE}" -m pip install openpyxl
                    
                    echo =========================================
                    echo 3. 정량적 리포트 생성 스크립트 실행
                    echo =========================================
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