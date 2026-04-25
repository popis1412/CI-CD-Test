pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '로컬 작업 경로')
    }

    environment {
        BASE_DIR = "${params.WORKSPACE_PATH}"
        LIBS_DIR = "${params.WORKSPACE_PATH}\\libs"
        TEST_FILE = "${params.WORKSPACE_PATH}\\Tests\\QA_Test.xlsx"
        REPORT_DIR = "${params.WORKSPACE_PATH}\\Test Results"
    }

    stages {

        // =========================
        // 1. PATH 확인
        // =========================
        stage('Workspace Init') {
            steps {
                script {
                    echo "=============================="
                    echo "BASE DIR = ${BASE_DIR}"
                    echo "=============================="

                    bat """
                    if not exist "${BASE_DIR}" mkdir "${BASE_DIR}"
                    if not exist "${BASE_DIR}\\Tests" mkdir "${BASE_DIR}\\Tests"
                    if not exist "${BASE_DIR}\\Test Results" mkdir "${BASE_DIR}\\Test Results"
                    """
                }
            }
        }

        // =========================
        // 2. LIBS 다운로드
        // =========================
        stage('Setup Libraries') {
            steps {
                script {

                    bat """
                    if not exist "${LIBS_DIR}" mkdir "${LIBS_DIR}"
                    """

                    def poi = "${LIBS_DIR}\\poi-5.2.5.jar"
                    def ooxml = "${LIBS_DIR}\\poi-ooxml-5.2.5.jar"
                    def xmlbeans = "${LIBS_DIR}\\xmlbeans-5.2.1.jar"

                    if (!fileExists(poi) || !fileExists(ooxml) || !fileExists(xmlbeans)) {

                        echo "[INFO] POI 다운로드 시작"

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/poi/poi/5.2.5/poi-5.2.5.jar -OutFile "${poi}"
                        """

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/poi/poi-ooxml/5.2.5/poi-ooxml-5.2.5.jar -OutFile "${ooxml}"
                        """

                        bat """
                        powershell -Command Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/apache/xmlbeans/xmlbeans/5.2.1/xmlbeans-5.2.1.jar -OutFile "${xmlbeans}"
                        """

                        echo "[DONE] 라이브러리 다운로드 완료"

                    } else {
                        echo "[OK] 라이브러리 이미 존재"
                    }
                }
            }
        }

        // =========================
        // 3. EXCEL 존재 확인
        // =========================
        stage('Validate Input') {
            steps {
                script {

                    if (!fileExists(TEST_FILE)) {
                        error "Excel 파일 없음: ${TEST_FILE}"
                    }

                    bat """
                    dir "${BASE_DIR}\\Tests"
                    """
                }
            }
        }

        // =========================
        // 4. JAVA 실행
        // =========================
        stage('QA Analysis') {
            steps {
                script {

                    def cmd = """
                    java -cp "${LIBS_DIR}/*;${BASE_DIR}" ExcelReader "${TEST_FILE}"
                    """

                    def output = bat(returnStdout: true, script: cmd).trim()

                    echo "=============================="
                    echo "JAVA OUTPUT"
                    echo "=============================="
                    echo output
                    echo "=============================="
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/Test Results/**', allowEmptyArchive: true
        }
    }
}