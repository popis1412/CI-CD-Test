pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    environment {
        PYTHON_EXE = "C:\\Program Files\\Python312\\python.exe"
        SLACK_CHANNEL = '새-채널'
        // 리포트 파일 위치
        REPORT_FILE_PATH = "Test Results\\qa_report.html"
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
                    
                    echo [로그] 리포트 생성 시작...
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
                // 1. 정확한 결함 개수 계산 (HTML 태그 내의 Fail만 추출)
                // 단순히 'Fail'을 세는 것이 아니라 <td>Fail</td> 처럼 데이터 셀에 있는 것만 필터링하여 정확도를 높입니다.
                def failCountStr = powershell(
                    returnStdout: true, 
                    script: "(Get-Content -Path '${REPORT_FILE_PATH}' -Encoding UTF8 | Select-String -Pattern '<td>Fail</td>' | Measure-Object).Count"
                ).trim()
                
                int failCount = failCountStr ? failCountStr.toInteger() : 0
                echo "[확인] 정밀 필터링된 Fail 개수: ${failCount}"

                if (failCount > 0) {
                    // 2. 결함이 있는 경우: 메시지 전송 후 파일 직접 업로드
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: "@here\n✅ **QA 빌드 완료 (결함 발견: ${failCount}건)**\n\n[고쳐야 되는 것들 목록 - 발견된 결함 상세 표]\n리포트 파일(${REPORT_FILE_PATH})을 아래에 첨부합니다. 다운로드하여 확인해 주세요."
                    )
                    
                    // 3. 생성된 HTML 파일 자체를 슬랙 채널에 업로드 (다른 사람도 즉시 확인 가능)
                    slackUploadFile(
                        channel: "#${SLACK_CHANNEL}",
                        filePath: "${REPORT_FILE_PATH}",
                        initialComment: "상세 결함 리포트 파일입니다."
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
                    message: "@here\n❌ **빌드를 실패했습니다.**\n파이프라인 로그를 확인해 주세요.**\n파이프라인 로그를 확인해 주세요.\n🔗 로그: ${env.BUILD_URL}console"
                )
            }
        }
    }
}