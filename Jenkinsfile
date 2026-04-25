pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    environment {
        PYTHON_EXE = "C:\\Program Files\\Python312\\python.exe"
        SLACK_CHANNEL = '새-채널'
        // [수정] 파일 업로드 안정성을 위해 절대 경로로 설정
        REPORT_FULL_PATH = "${WORKSPACE}\\Test Results\\qa_report.html"
    }

    stages {
        stage('Python 환경 검사') {
            steps {
                script {
                    def exists = bat(script: "if exist \"${PYTHON_EXE}\" (exit 0) else (exit 1)", returnStatus: true)
                    if (exists != 0) error("파이썬을 찾을 수 없습니다: ${PYTHON_EXE}")
                }
            }
        }

        stage('QA 결과 분석') {
            steps {
                script {
                    // returnStdout으로 로그를 가져오되, echo 중복은 피합니다.
                    def runLog = bat(returnStdout: true, script: """
                        @echo off
                        chcp 65001 >nul
                        set PYTHONIOENCODING=utf-8
                        "${PYTHON_EXE}" -m pip install openpyxl --quiet
                        "${PYTHON_EXE}" make_report.py "${params.BASE_PATH}"
                    """).trim()

                    // 로그에서 [FAIL_COUNT] 뒤의 숫자만 파싱
                    def matcher = (runLog =~ /\[FAIL_COUNT\]\s+(\d+)/)
                    env.ACTUAL_FAIL_COUNT = matcher.find() ? matcher.group(1) : "0"
                    
                    // 추출된 숫자만 로그에 한 번만 찍어줍니다.
                    echo "----------------------------------------------"
                    echo "최종 확인된 결함(Fail) 개수: ${env.ACTUAL_FAIL_COUNT}"
                    echo "----------------------------------------------"
                }
            }
        }
    }

    post {
        success {
            script {
                int fCount = env.ACTUAL_FAIL_COUNT.toInteger()

                if (fCount > 0) {
                    // 1. 텍스트 메시지 먼저 전송
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: "@here\n✅ **QA 빌드 완료 (결함 발견: ${fCount}건)**\n\n[고쳐야 되는 것들 목록 - 발견된 결함 상세 표]\n파이썬으로 생성된 상세 리포트를 아래에 첨부합니다."
                    )
                    
                    // 2. [중요] 파일 업로드 - 절대 경로를 사용하여 확실하게 전송
                    // 만약 여기서도 안 올라간다면 슬랙 앱의 'files:write' 권한을 확인해야 합니다.
                    slackUploadFile(
                        channel: "#${SLACK_CHANNEL}",
                        filePath: "${env.REPORT_FULL_PATH}",
                        initialComment: "qa_report.html 상세 결과 파일"
                    )
                } else {
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'good',
                        message: "@here\n✅ **QA 빌드 완료 (Clean)**\n\n발견된 결함이 없습니다. 🎉"
                    )
                }
            }
        }
        failure {
            script {
                slackSend(
                    channel: "#${SLACK_CHANNEL}",
                    color: 'danger',
                    message: "@here\n❌ **빌드를 실패했습니다.**\n로그 확인: ${env.BUILD_URL}console"
                )
            }
        }
    }
}