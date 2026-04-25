pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '작업 경로 입력')
    }

    environment {
        LIBS_DIR = "${params.WORKSPACE_PATH}\\libs"
        TEST_FILE = "${params.WORKSPACE_PATH}\\Tests\\QA_Test.xlsx"
        REPORT_DIR = "${params.WORKSPACE_PATH}\\Test Results"
        REPORT_FILE = "${params.WORKSPACE_PATH}\\Test Results\\qa_report.html"
    }

    stages {

        // =========================
        // 1. PATH 확인
        // =========================
        stage('Path Check') {
            steps {
                script {

                    echo "========================"
                    echo "USER PATH = ${params.WORKSPACE_PATH}"
                    echo "========================"

                    bat """
                    echo WORKSPACE_PATH = ${params.WORKSPACE_PATH}
                    if not exist "${params.WORKSPACE_PATH}" mkdir "${params.WORKSPACE_PATH}"
                    if not exist "${params.WORKSPACE_PATH}\\Tests" mkdir "${params.WORKSPACE_PATH}\\Tests"
                    """
                }
            }
        }

        // =========================
        // 2. LIBS SETUP
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
        // 3. PREPARE
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
        // 4. EXCEL 분석 (Java 실행)
        // =========================
        stage('QA Analysis') {
            steps {
                script {

                    if (!fileExists(TEST_FILE)) {
                        error "Excel 파일 없음: ${TEST_FILE}"
                    }

                    def cmd = """
                    java -cp "${LIBS_DIR}/*;${params.WORKSPACE_PATH}" ExcelReader "${TEST_FILE}"
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