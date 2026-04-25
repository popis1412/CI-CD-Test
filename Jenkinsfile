pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    environment {
        PYTHON_EXE = "C:\\Program Files\\Python312\\python.exe"
        SLACK_CHANNEL = '새-채널'
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
                    "${PYTHON_EXE}" -m pip install openpyxl --quiet
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

    post {
        success {
            script {
                // 리포트 파일 내부에서 'Fail' 혹은 결함을 나타내는 키워드가 있는지 검사합니다.
                // findstr을 사용하여 결함 개수가 1개 이상인지 파악합니다.
                def reportPath = "Test Results/qa_report.html"
                def hasFailures = bat(script: "findstr /C:\"Fail\" \"${reportPath}\"", returnStatus: true)

                if (hasFailures == 0) {
                    // 결함(Fail)이 1개 이상 발견된 경우 (findstr 성공 시 0 반환)
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: """@here
✅ **QA 빌드 완료 (결함 발견)**

[고쳐야 되는 것들 목록 - 발견된 결함 상세 표]
테스트 결과 결함이 발견되었습니다. 아래 링크를 통해 상세 내용을 확인하고 수정해 주세요.
🔗 리포트 확인: ${env.BUILD_URL}artifact/${reportPath}"""
                    )
                } else {
                    // 결함이 없는 경우 (findstr 실패 시 1 반환)
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'good',
                        message: "@here\n✅ **QA 빌드 완료 (Clean)**\n\n발견된 결함이 없습니다. 모든 테스트가 통과되었습니다! 🎉"
                    )
                }
            }
        }
        failure {
            script {
                slackSend(
                    channel: "#${SLACK_CHANNEL}",
                    color: 'danger',
                    message: "@here\n❌ **빌드를 실패했습니다.**\n파이프라인 로그 혹은 파이썬 경로를 확인해 주세요.\n🔗 로그 확인: ${env.BUILD_URL}console"
                )
            }
        }
    }
}