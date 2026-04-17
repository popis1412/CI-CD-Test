pipeline {
    agent any

    stages {

        stage('Prepare') {
            steps {
                bat 'if not exist reports mkdir reports'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install pytest'
            }
        }

        stage('Run CA Tests (합기)') {
            steps {
                bat 'python -m pytest tests/test_ca.py --html=reports/CA_Report.html'
            }
        }

        stage('Run WPN Tests (무기/태그)') {
            steps {
                bat 'python -m pytest tests/test_wpn.py --html=reports/WPN_Report.html'
            }
        }

        stage('Run SKL Tests (모험스킬)') {
            steps {
                bat 'python -m pytest tests/test_skl.py --html=reports/SKL_Report.html'
            }
        }

        stage('Run GIM Tests (기믹)') {
            steps {
                bat 'python -m pytest tests/test_gim.py --html=reports/GIM_Report.html'
            }
        }

        stage('Run WLD Tests (환경)') {
            steps {
                bat 'python -m pytest tests/test_wld.py --html=reports/WLD_Report.html'
            }
        }
    }

    post {
        always {
            echo '전체 테스트 완료'

            archiveArtifacts artifacts: 'reports/*.html', fingerprint: true

            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'CA_Report.html,WPN_Report.html,SKL_Report.html,GIM_Report.html,WLD_Report.html',
                reportName: 'Test Reports',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }

        success {
            echo '모든 테스트 성공'
        }

        failure {
            echo '테스트 실패 발생'
        }
    }
}