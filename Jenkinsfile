pipeline {
    agent any
    
    // 환경 파라미터로 베이스 경로를 입력받습니다.
    parameters {
        string(name: 'BASE_PATH', defaultValue: '/your/default/workspace/path', description: '프로젝트 최상위 경로를 입력하세요.')
    }

    stages {
        stage('QA 결과 분석 및 HTML 생성') {
            steps {
                script {
                    // BASE_PATH를 파라미터로 가져옵니다.
                    def basePath = params.BASE_PATH\\
                    
                    // 미리 빌드된 jar 파일의 경로 (예: 프로젝트 루트 디렉토리에 위치한다고 가정)
                    def jarPath = "QAReportGenerator.jar"
                    
                    // java -jar 명령어로 실행하며 파라미터로 basePath를 넘깁니다.
                    // -Dfile.encoding=UTF-8 옵션으로 한글 깨짐을 원천 차단합니다.
                    sh """
                        java -Dfile.encoding=UTF-8 -jar ${jarPath} "${basePath}"
                    """
                }
            }
        }
        
        stage('리포트 아카이빙') {
            steps {
                // 젠킨스 빌드 화면에서 생성된 HTML 리포트를 바로 확인할 수 있도록 아카이빙합니다.
                archiveArtifacts artifacts: '**/Test Results/qa_report.html', allowEmptyArchive: true
            }
        }
    }
}