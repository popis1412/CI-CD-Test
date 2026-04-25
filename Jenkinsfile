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
                // 파이썬에서 추출된 실제 결함 개수
                int fCount = env.ACTUAL_FAIL_COUNT.toInteger()

                if (fCount > 0) {
                    // 결함이 1개 이상인 경우
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: """@here
✅ **QA 빌드 완료**
발견된 결함이 **${fCount}개** 있습니다.
`Test Results\\qa_report.html` 파일을 확인해 주세요."""
                    )
                    
                    // 파일 업로드 (슬랙 앱 권한이 허용되어 있어야 함)
                    slackUploadFile(
                        channel: "#${SLACK_CHANNEL}",
                        filePath: "${env.REPORT_FULL_PATH}",
                        initialComment: "상세 결함 리포트(qa_report.html)입니다."
                    )
                } else {
                    // 결함이 0개인 경우
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'good',
                        message: "@here\n✅ **QA 빌드 완료**\n발견된 결함이 없습니다. 🎉"
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