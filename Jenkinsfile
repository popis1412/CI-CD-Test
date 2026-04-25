pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    environment {
        PYTHON_EXE = "C:\\Program Files\\Python312\\python.exe"
        SLACK_CHANNEL = '새-채널'
        REPORT_FILE_PATH = "Test Results\\qa_report.html"
    }

    stages {
        stage('Python 환경 검사') {
            steps {
                script {
                    def exists = bat(script: "if exist \"${PYTHON_EXE}\" (exit 0) else (exit 1)", returnStatus: true)
                    if (exists != 0) error("파이썬을 찾을 수 없습니다.")
                }
            }
        }

        stage('QA 결과 분석') {
            steps {
                script {
                    // 1. 파이썬 실행 로그를 변수에 담습니다.
                    def runLog = bat(returnStdout: true, script: """
                        @echo off
                        chcp 65001 >nul
                        set PYTHONIOENCODING=utf-8
                        "${PYTHON_EXE}" -m pip install openpyxl --quiet
                        "${PYTHON_EXE}" make_report.py "${params.BASE_PATH}"
                    """).trim()

                    echo "${runLog}" // 전체 로그 출력

                    // 2. 로그에서 [FAIL_COUNT] 뒤의 숫자를 정규표현식으로 찾아냅니다.
                    def matcher = (runLog =~ /\[FAIL_COUNT\]\s+(\d+)/)
                    if (matcher.find()) {
                        env.ACTUAL_FAIL_COUNT = matcher.group(1)
                    } else {
                        env.ACTUAL_FAIL_COUNT = "0"
                    }
                    echo "[확인] 추출된 결함 개수: ${env.ACTUAL_FAIL_COUNT}"
                }
            }
        }
    }

    post {
        success {
            script {
                int fCount = env.ACTUAL_FAIL_COUNT.toInteger()

                if (fCount > 0) {
                    // 결함이 1개 이상일 때
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: """@here
✅ **QA 빌드 완료 (결함 발견: ${fCount}건)**

[고쳐야 되는 것들 목록 - 발견된 결함 상세 표]
테스트 결과 총 **${fCount}개**의 결함이 발견되었습니다. 첨부된 리포트를 확인해 주세요."""
                    )
                    
                    slackUploadFile(
                        channel: "#${SLACK_CHANNEL}",
                        filePath: "${REPORT_FILE_PATH}",
                        initialComment: "발견된 결함 리스트입니다."
                    )
                } else {
                    // 결함이 0개일 때
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'good',
                        message: "@here\n✅ **QA 빌드 완료 (Clean)**\n\n결함이 발견되지 않았습니다. 🎉"
                    )
                }
            }
        }
        failure {
            script {
                slackSend(
                    channel: "#${SLACK_CHANNEL}",
                    color: 'danger',
                    message: "@here\n❌ **빌드를 실패했습니다.**\n로그를 확인하세요: ${env.BUILD_URL}console"
                )
            }
        }
    }
}