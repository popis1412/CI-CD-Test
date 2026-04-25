pipeline {
    agent any

    environment {
        LIBS_DIR = "${env.WORKSPACE}\\libs"
        TEST_FILE = "${env.WORKSPACE}\\Tests\\QA_Test.xlsx"
        REPORT_DIR = "${env.WORKSPACE}\\Test Results"
        REPORT_FILE = "${env.WORKSPACE}\\Test Results\\qa_report.html"
    }

    stages {

        // =========================
        // 1. WORKSPACE 확인 (UTF-8 안정화)
        // =========================
        stage('Workspace Check') {
            steps {
                script {

                    echo "========================"
                    echo "WORKSPACE = ${env.WORKSPACE}"
                    echo "========================"

                    bat """
                    chcp 65001
                    echo WORKSPACE = %WORKSPACE%
                    dir %WORKSPACE%
                    """
                }
            }
        }

        // =========================
        // 2. LIBS 자동 다운로드
        // =========================
        stage('Setup Libraries') {
            steps {
                script {

                    bat """
                    if not exist "${LIBS_DIR}" mkdir "${LIBS_DIR}"
                    """

                    def poiJar = "${LIBS_DIR}\\poi-5.2.5.jar"
                    def ooxmlJar = "${LIBS_DIR}\\poi-ooxml-5.2.5.jar"
                    def xmlbeansJar = "${LIBS_DIR}\\xmlbeans-5.2.1.jar"

                    if (!fileExists(poiJar) || !fileExists(ooxmlJar) || !fileExists(xmlbeansJar)) {

                        echo "[INFO] POI 다운로드 시작"

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/poi/poi/5.2.5/poi-5.2.5.jar -OutFile "${poiJar}"
                        """

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/poi/poi-ooxml/5.2.5/poi-ooxml-5.2.5.jar -OutFile "${ooxmlJar}"
                        """

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/xmlbeans/xmlbeans/5.2.1/xmlbeans-5.2.1.jar -OutFile "${xmlbeansJar}"
                        """

                        echo "[DONE] 라이브러리 다운로드 완료"

                    } else {
                        echo "[OK] 라이브러리 이미 존재"
                    }
                }
            }
        }

        // =========================
        // 3. 결과 폴더 준비
        // =========================
        stage('Prepare') {
            steps {
                bat """
                if exist "${REPORT_DIR}" rmdir /s /q "${REPORT_DIR}"
                mkdir "${REPORT_DIR}"
                """
            }
        }

        // =========================
        // 4. Excel 분석 (Git 기반 Java 실행)
        // =========================
        stage('QA Analysis') {
            steps {
                script {

                    if (!fileExists(TEST_FILE)) {
                        error "Excel 파일 없음: ${TEST_FILE}"
                    }

                    // Java 실행 (Git에서 가져온 ExcelReader 사용)
                    def cmd = """
                    java -cp "${LIBS_DIR}/*;${env.WORKSPACE}" ExcelReader "${TEST_FILE}"
                    """

                    def output = bat(returnStdout: true, script: cmd).trim()

                    echo "========================="
                    echo output
                    echo "========================="
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/Test Results/**'
        }
    }
}