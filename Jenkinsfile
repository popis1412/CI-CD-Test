pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    environment {
        PYTHON_EXE = "C:\\Program Files\\Python312\\python.exe"
        SLACK_CHANNEL = '새-채널'
        // [수정] 생성된 리포트가 저장되는 실제 로컬/네트워크 전체 경로
        REPORT_FULL_PATH = "${WORKSPACE}\\Test Results\\qa_report.html"
    }

    stages {
        stage('Python 환경 검사') {
            steps {
                script {
                    def pythonExists = bat(script: "if exist \"${PYTHON_EXE}\" (exit 0) else (exit 1)", returnStatus: true)
                    if (pythonExists != 0) {
                        error("지정된 경로에 파이썬이 없습니다: ${PYTHON_EXE}")
                    }
                }
            }
        }

        stage('QA 결과 분석') {
            steps {
                script {
                    def basePath = params.BASE_PATH
                    bat """
                    @echo off
                    chcp 65001 >nul
                    set PYTHONIOENCODING=utf-8
                    
                    echo [로그] 라이브러리 설치 및 리포트 생성 시작...
                    "${PYTHON_EXE}" -m pip install openpyxl --quiet
                    "${PYTHON_EXE}" make_report.py "${basePath}"
                    """
                }
            }
        }
    }

    post {
        success {
            script {
                // PowerShell을 사용하여 UTF-8 리포트 내 'Fail' 키워드 개수 정밀 체크
                def failCountStr = powershell(
                    returnStdout: true, 
                    script: "(Get-Content -Path '${env.REPORT_FULL_PATH}' -Encoding UTF8 | Select-String -Pattern 'Fail' | Measure-Object).Count"
                ).trim()
                
                int failCount = failCountStr ? failCountStr.toInteger() : 0
                
                // 슬랙에 표시될 로컬 파일 경로 URL 형식 (file:///)
                def fileUrl = "file:///${env.REPORT_FULL_PATH.replace('\\', '/')}"

                if (failCount > 0) {
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: """@here
✅ **QA 빌드 완료 (결함 발견: ${failCount}건)**

[고쳐야 되는 것들 목록 - 발견된 결함 상세 표]
테스트 결과 총 **${failCount}개**의 결함항목이 발견되었습니다. 내용을 확인하고 수정해 주세요.
🔗 리포트 파일 경로: ${fileUrl}"""
                    )
                } else {
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'good',
                        message: "@here\n✅ **QA 빌드 완료 (Clean)**\n\n발견된 결함이 없습니다. 모든 항목이 통과되었습니다! 🎉"
                    )
                }
            }
        }
        failure {
            script {
                slackSend(
                    channel: "#${SLACK_CHANNEL}",
                    color: 'danger',
                    message: "@here\n❌ **빌드를 실패했습니다.**\n파이프라인 로그를 확인하거나 파이썬 설치 경로를 점검해 주세요."
                )
            }
        }
    }
}