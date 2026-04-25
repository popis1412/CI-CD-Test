pipeline {
    agent any

    environment {
        LIBS_DIR = "${env.WORKSPACE}\\libs"
        TEST_FILE = "${env.WORKSPACE}\\Tests\\QA_Test.xlsx"
        REPORT_DIR = "${env.WORKSPACE}\\Test Results"
        REPORT_FILE = "${env.WORKSPACE}\\Test Results\\qa_report.html"
        JAVA_FILE = "${env.WORKSPACE}\\ExcelReader.java"
    }

    stages {

        // =========================
        // 1. WORKSPACE DEBUG + JAVA 자동 생성
        // =========================
        stage('Workspace Check & Java Generate') {
            steps {
                script {

                    echo "=============================="
                    echo "[WORKSPACE] ${env.WORKSPACE}"
                    echo "=============================="

                    bat """
                    echo WORKSPACE PATH = %WORKSPACE%
                    dir %WORKSPACE%
                    """

                    // =========================
                    // Java 파일 없으면 자동 생성
                    // =========================
                    if (!fileExists(JAVA_FILE)) {

                        echo "[INFO] ExcelReader.java 없음 → 자동 생성"

                        writeFile file: JAVA_FILE, text: """
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.File;
import java.io.FileInputStream;

public class ExcelReader {

    public static void main(String[] args) throws Exception {

        String filePath = args[0];

        FileInputStream fis = new FileInputStream(new File(filePath));
        Workbook workbook = new XSSFWorkbook(fis);

        int total = 0;

        for (int s = 0; s < workbook.getNumberOfSheets(); s++) {

            Sheet sheet = workbook.getSheetAt(s);

            for (int i = 1; i <= sheet.getLastRowNum(); i++) {

                Row row = sheet.getRow(i);
                if (row == null) continue;

                Cell cell = row.getCell(4);
                if (cell == null) continue;

                total++;
            }
        }

        workbook.close();

        System.out.println("TOTAL = " + total);
    }
}
"""

                        echo "[DONE] ExcelReader.java 생성 완료"

                    } else {
                        echo "[OK] ExcelReader.java 이미 존재"
                    }
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
                    def xmlbeansJar = "${LIBS_DIR}\\xmlbeans.jar"

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
        // 4. EXCEL ANALYSIS
        // =========================
        stage('QA Analysis') {
            steps {
                script {

                    if (!fileExists(TEST_FILE)) {
                        error "Excel 파일 없음"
                    }

                    // compile
                    bat """
                    javac -cp "${LIBS_DIR}/*" "${JAVA_FILE}"
                    """

                    // run
                    def cmd = """
                    java -cp "${LIBS_DIR}/*;." ExcelReader "${TEST_FILE}"
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