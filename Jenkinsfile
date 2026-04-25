pipeline {
    agent any
    
    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '프로젝트 최상위 경로를 입력하세요.')
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
                    :: 윈도우 터미널 및 출력을 UTF-8(65001)로 설정
                    chcp 65001 >nul
                    
                    :: 파이썬 실행 시에도 UTF-8 인코딩을 강제하는 환경변수 설정
                    set PYTHONIOENCODING=utf-8
                    
                    echo [로그] 라이브러리 설치 및 리포트 생성 시작...
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
                // [수정] 윈도우 bat 대신 파워쉘을 사용하여 UTF-8 파일을 정확히 읽습니다.
                // 리포트 파일 내에 'Fail'이라는 단어가 포함된 줄의 개수를 셉니다.
                def reportPath = "Test Results/qa_report.html"
                
                // 파워쉘을 통해 UTF8 인코딩으로 파일을 읽고 'Fail'이 포함된 라인 수를 가져옵니다.
                def failCountStr = powershell(
                    returnStdout: true, 
                    script: "(Get-Content -Path '${reportPath}' -Encoding UTF8 | Select-String -Pattern 'Fail' | Measure-Object).Count"
                ).trim()
                
                int failCount = failCountStr ? failCountStr.toInteger() : 0
                echo "[확인] 리포트 내 발견된 Fail 키워드 개수: ${failCount}"

                if (failCount > 0) {
                    // 결함이 1개 이상인 경우
                    slackSend(
                        channel: "#${SLACK_CHANNEL}",
                        color: 'warning',
                        message: """@here
✅ **QA 빌드 완료 (결함 발견: ${failCount}건)**

[고쳐야 되는 것들 목록 - 발견된 결함 상세 표]
테스트 결과 총 **${failCount}개**의 결함항목이 발견되었습니다. 내용을 확인하고 수정해 주세요.
🔗 리포트 확인: ${env.BUILD_URL}artifact/${reportPath}"""
                    )
                } else {
                    // 결함이 정말 0개인 경우
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
                    message: "@here\n❌ **빌드를 실패했습니다.**\n파이프라인 로그를 확인해 주세요.\n🔗 로그 확인: ${env.BUILD_URL}console"
                )
            }
        }
    }
}