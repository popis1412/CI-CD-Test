pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/popis1412/CI-CD-Test.git'
            }
        }

        stage('Install') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('CA Tests (합기)') {
            steps {
                bat 'pytest tests/test_ca.py'
            }
        }

        stage('WPN Tests (무기/태그)') {
            steps {
                bat 'pytest tests/test_wpn.py'
            }
        }

        stage('SKL Tests (모험스킬)') {
            steps {
                bat 'pytest tests/test_skl.py'
            }
        }

        stage('GIM Tests (기믹)') {
            steps {
                bat 'pytest tests/test_gim.py'
            }
        }

        stage('WLD Tests (환경)') {
            steps {
                bat 'pytest tests/test_wld.py'
            }
        }
    }

    post {
        always {
            echo '전체 테스트 완료'
        }
        success {
            echo '모든 테스트 성공'
        }
        failure {
            echo '테스트 실패 발생'
        }
    }
}