pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\파일경로')
    }

    environment {
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        LIBS_DIR = "${WORKSPACE_PATH}\\libs"
        TEST_FILE = "${WORKSPACE_PATH}\\Tests\\QA_Test.xlsx"
        REPORT_DIR = "${WORKSPACE_PATH}\\Test Results"
        REPORT_FILE = "${REPORT_DIR}\\qa_report.html"
    }

    stages {

        // =========================
        // 1. LIBS SETUP
        // =========================
        stage('Setup Libraries') {
            steps {
                script {

                    bat """
                    if not exist "${LIBS_DIR}" mkdir "${LIBS_DIR}"
                    """

                    def poiJar = "${LIBS_DIR}\\poi-5.2.5.jar"
                    def ooxmlJar = "${LIBS_DIR}\\poi-ooxml-5.2.5.jar"
                    def xmlbeansJar = "${LIBS_DIR}\\xmlbeans.jar"

                    if (!fileExists(poiJar) || !fileExists(ooxmlJar) || !fileExists(xmlbeansJar)) {

                        echo "[INFO] POI 라이브러리 없음 → 다운로드 시작"

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/poi/poi/5.2.5/poi-5.2.5.jar -OutFile "${poiJar}"
                        """

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/poi/poi-ooxml/5.2.5/poi-ooxml-5.2.5.jar -OutFile "${ooxmlJar}"
                        """

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/xmlbeans/xmlbeans/5.2.1/xmlbeans-5.2.1.jar -OutFile "${xmlbeansJar}"
                        """

                        echo "[DONE] POI 다운로드 완료"

                    } else {
                        echo "[OK] POI 라이브러리가 이미 있습니다"
                    }
                }
            }
        }

        // =========================
        // 2. PREPARE
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
        // 3. EXCEL ANALYSIS (JAVA)
        // =========================
        stage('QA Analysis (Excel)') {
            steps {
                script {

                    if (!fileExists(TEST_FILE)) {
                        error "Excel 파일 없음"
                    }

                    // =========================
                    // 1. 컴파일 (FIXED)
                    // =========================
                    bat """
                    javac -cp "${LIBS_DIR}/*" "${WORKSPACE_PATH}\\ExcelReader.java"
                    """

                    // =========================
                    // 2. 실행 (FIXED)
                    // =========================
                    def cmd = """
                    java -cp "${LIBS_DIR}/*;." ExcelReader "${TEST_FILE}" "${REPORT_FILE}"
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