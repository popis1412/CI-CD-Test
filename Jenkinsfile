/*
================================================================================
JENKINSFILE - 단순 파라미터 버전 (WORKSPACE_PATH만 사용)
파일명: Jenkinsfile
위치: Git 저장소 루트
================================================================================
*/

pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'Jenkins workspace path (e.g., C:\\파일 경로)')
    }

    environment {
        PROJECT_NAME = "7DS Origin QA"
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        RESULT_DIR = "${params.WORKSPACE_PATH}\\Test Results"
        TEST_FILE_PATH = "${params.WORKSPACE_PATH}\\Tests\\QA_Test.csv"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    bat """
                    echo [INFO] Result directory: ${RESULT_DIR}
                    if exist "${RESULT_DIR}" (
                        rmdir /s /q "${RESULT_DIR}"
                    )
                    mkdir "${RESULT_DIR}"
                    echo [INFO] Directory created successfully
                    """
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def WORK_DIR = env.WORKSPACE_PATH
                    def RESULT_DIR = env.RESULT_DIR
                    def TEST_FILE = env.TEST_FILE_PATH

                    echo "[INFO] WORKSPACE: ${WORK_DIR}"
                    echo "[INFO] RESULT DIR: ${RESULT_DIR}"
                    echo "[INFO] TEST FILE: ${TEST_FILE }"

                    if (!fileExists(TEST_FILE)) {
                        error "[ERR-FILE-001] 테스트 파일 없음: ${TEST_FILE}"
                    }

                    def content = readFile(TEST_FILE)
                    def lines = content.split("\r?\n")

                    def testResults = []

                    // ======================
                    // CSV PARSE
                    // ======================
                    for (int i = 1; i < lines.size(); i++) {
                        if (lines[i].trim().isEmpty()) continue
                        
                        def cols = lines[i].split(",")

                        if (cols.size() >= 4) {
                            testResults << [
                                major: cols[0]?.trim() ?: "",
                                minor: cols[1]?.trim() ?: "",
                                scenario: cols[2]?.trim() ?: "",
                                result: cols[3]?.trim() ?: ""
                            ]
                        }
                    }

                    // ======================
                    // 상태 정규화
                    // ======================
                    def normalize = { r ->
                        if (r == null || r.isEmpty()) return "Not Test"
                        def v = r.trim().toLowerCase()

                        if (v == "pass") return "Pass"
                        if (v == "fail") return "Fail"
                        if (v == "blocked") return "Blocked"
                        if (v == "n/a" || v == "na") return "N/A"
                        return "Not Test"
                    }

                    // ======================
                    // 상태 정규화 적용
                    // ======================
                    testResults.each { t ->
                        t.result = normalize(t.result)
                    }

                    // ======================
                    // 전체 통계
                    // ======================
                    def stats = [
                        "Total": testResults.size(),
                        "Pass": 0,
                        "Fail": 0,
                        "Blocked": 0,
                        "Not Test": 0,
                        "N/A": 0
                    ]

                    testResults.each { t ->
                        stats[t.result] = (stats[t.result] ?: 0) + 1
                    }

                    def failRate = stats["Total"] > 0 ?
                            (stats["Fail"] * 100.0 / stats["Total"]) : 0

                    // ======================
                    // 대/중분류별 분류 데이터
                    // ======================
                    def classificationMap = [:]
                    
                    testResults.each { t ->
                        def key = "${t.major}|${t.minor}"
                        if (!classificationMap[key]) {
                            classificationMap[key] = [
                                major: t.major,
                                minor: t.minor,
                                Total: 0,
                                Pass: 0,
                                Fail: 0,
                                Blocked: 0,
                                "Not Test": 0,
                                "N/A": 0,
                                scenarios: [:]
                            ]
                        }
                        
                        def cls = classificationMap[key]
                        cls.Total++
                        cls[t.result] = (cls[t.result] ?: 0) + 1
                        
                        // 시나리오별 결과 추적
                        if (!cls.scenarios[t.scenario]) {
                            cls.scenarios[t.scenario] = [:]
                        }
                        cls.scenarios[t.scenario][t.result] = (cls.scenarios[t.scenario][t.result] ?: 0) + 1
                    }

                    // ======================
                    // 대분류별 분류 데이터
                    // ======================
                    def majorMap = [:]
                    
                    classificationMap.each { k, v ->
                        if (!majorMap[v.major]) {
                            majorMap[v.major] = [:]
                        }
                        majorMap[v.major][v.minor] = v
                    }

                    // ======================
                    // Fail 리스트
                    // ======================
                    def fails = testResults.findAll { it.result == "Fail" }
                    
                    // ======================
                    // 대분류별 Fail 분류
                    // ======================
                    def failsByMajor = [:]
                    fails.each { f ->
                        if (!failsByMajor[f.major]) {
                            failsByMajor[f.major] = []
                        }
                        failsByMajor[f.major] << f
                    }

                    // ======================
                    // HTML 생성
                    // ======================
                    def html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${PROJECT_NAME} QA Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 50px;
        }
        
        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-icon {
            font-size: 1.5em;
        }
        
        /* 통계 박스 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .stat-rate {
            font-size: 1.1em;
            opacity: 0.8;
        }
        
        /* 테이블 스타일 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: #f5f7fa;
            color: #333;
            padding: 15px;
            text-align: center;
            font-weight: 600;
            border-bottom: 2px solid #667eea;
            font-size: 0.95em;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            text-align: center;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tr:hover {
            background: #f9fafb;
        }
        
        .text-left {
            text-align: left;
        }
        
        /* 상태별 색상 */
        .status-pass {
            background: #e8f5e9;
            color: #2e7d32;
            font-weight: 600;
        }
        
        .status-fail {
            background: #ffebee;
            color: #c62828;
            font-weight: 600;
        }
        
        .status-blocked {
            background: #fff3e0;
            color: #e65100;
            font-weight: 600;
        }
        
        .status-nottest {
            background: #f5f5f5;
            color: #616161;
            font-weight: 600;
        }
        
        .status-na {
            background: #e3f2fd;
            color: #1565c0;
            font-weight: 600;
        }
        
        /* 분류 서브섹션 */
        .classification-section {
            background: #f9fafb;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }
        
        .classification-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }
        
        .fail-detail {
            background: #ffebee;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #c62828;
        }
        
        .fail-detail-title {
            font-weight: 600;
            color: #c62828;
            margin-bottom: 8px;
        }
        
        .fail-detail-item {
            font-size: 0.95em;
            color: #333;
            padding: 5px 0;
        }
        
        .fail-detail-item strong {
            color: #c62828;
        }
        
        .no-data {
            text-align: center;
            padding: 30px;
            color: #999;
            font-style: italic;
        }
        
        .metric {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-right: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>${PROJECT_NAME}</h1>
            <p>QA Test Report</p>
        </div>
        
        <div class="content">
            <!-- 섹션 1: 전체 테스트 현황 -->
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">📊</span>
                    전체 테스트 현황
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <div class="stat-label">Total</div>
                        <div class="stat-value">${stats["Total"]}</div>
                        <div class="stat-rate">100.00%</div>
                    </div>
                    <div class="stat-box" style="background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);">
                        <div class="stat-label">Pass</div>
                        <div class="stat-value">${stats["Pass"]}</div>
                        <div class="stat-rate">${String.format("%.2f%%", stats["Pass"] * 100.0 / stats["Total"])}</div>
                    </div>
                    <div class="stat-box" style="background: linear-gradient(135deg, #c62828 0%, #880e4f 100%);">
                        <div class="stat-label">Fail</div>
                        <div class="stat-value">${stats["Fail"]}</div>
                        <div class="stat-rate">${String.format("%.2f%%", stats["Fail"] * 100.0 / stats["Total"])}</div>
                    </div>
                    <div class="stat-box" style="background: linear-gradient(135deg, #e65100 0%, #bf360c 100%);">
                        <div class="stat-label">Blocked</div>
                        <div class="stat-value">${stats["Blocked"]}</div>
                        <div class="stat-rate">${String.format("%.2f%%", stats["Blocked"] * 100.0 / stats["Total"])}</div>
                    </div>
                    <div class="stat-box" style="background: linear-gradient(135deg, #616161 0%, #212121 100%);">
                        <div class="stat-label">Not Test</div>
                        <div class="stat-value">${stats["Not Test"]}</div>
                        <div class="stat-rate">${String.format("%.2f%%", stats["Not Test"] * 100.0 / stats["Total"])}</div>
                    </div>
                    <div class="stat-box" style="background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);">
                        <div class="stat-label">N/A</div>
                        <div class="stat-value">${stats["N/A"]}</div>
                        <div class="stat-rate">${String.format("%.2f%%", stats["N/A"] * 100.0 / stats["Total"])}</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Count</th>
                            <th>Progress</th>
                            <th>Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-left"><strong>Total</strong></td>
                            <td>${stats["Total"]}</td>
                            <td><div style="width:100%; background:#667eea; height:20px; border-radius:10px;"></div></td>
                            <td>100.00%</td>
                        </tr>
                        <tr>
                            <td class="text-left"><strong>Pass</strong></td>
                            <td>${stats["Pass"]}</td>
                            <td><div style="width:${stats["Pass"] * 100 / stats["Total"]}%; background:#2e7d32; height:20px; border-radius:10px;"></div></td>
                            <td>${String.format("%.2f%%", stats["Pass"] * 100.0 / stats["Total"])}</td>
                        </tr>
                        <tr>
                            <td class="text-left"><strong>Fail</strong></td>
                            <td>${stats["Fail"]}</td>
                            <td><div style="width:${stats["Fail"] * 100 / stats["Total"]}%; background:#c62828; height:20px; border-radius:10px;"></div></td>
                            <td>${String.format("%.2f%%", stats["Fail"] * 100.0 / stats["Total"])}</td>
                        </tr>
                        <tr>
                            <td class="text-left"><strong>Blocked</strong></td>
                            <td>${stats["Blocked"]}</td>
                            <td><div style="width:${stats["Blocked"] * 100 / stats["Total"]}%; background:#e65100; height:20px; border-radius:10px;"></div></td>
                            <td>${String.format("%.2f%%", stats["Blocked"] * 100.0 / stats["Total"])}</td>
                        </tr>
                        <tr>
                            <td class="text-left"><strong>NotTest</strong></td>
                            <td>${stats["Not Test"]}</td>
                            <td><div style="width:${stats["Not Test"] * 100 / stats["Total"]}%; background:#616161; height:20px; border-radius:10px;"></div></td>
                            <td>${String.format("%.2f%%", stats["Not Test"] * 100.0 / stats["Total"])}</td>
                        </tr>
                        <tr>
                            <td class="text-left"><strong>N/A</strong></td>
                            <td>${stats["N/A"]}</td>
                            <td><div style="width:${stats["N/A"] * 100 / stats["Total"]}%; background:#1565c0; height:20px; border-radius:10px;"></div></td>
                            <td>${String.format("%.2f%%", stats["N/A"] * 100.0 / stats["Total"])}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- 섹션 2: 대분류별 테스트 현황 -->
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">🏷️</span>
                    대/중분류별 테스트 현황
                </div>
                """

                    majorMap.keySet().sort().each { major ->
                        html += """
                <div class="classification-section">
                    <div class="classification-title">대분류: ${major}</div>
                    <table>
                        <thead>
                            <tr>
                                <th class="text-left">중분류</th>
                                <th>Total</th>
                                <th>Pass</th>
                                <th>Fail</th>
                                <th>Blocked</th>
                                <th>NotTest</th>
                                <th>N/A</th>
                            </tr>
                        </thead>
                        <tbody>
                        """

                        majorMap[major].keySet().sort().each { minor ->
                            def v = majorMap[major][minor]
                            def total = v.Total ?: 1
                            
                            html += """
                            <tr>
                                <td class="text-left">${minor}</td>
                                <td><strong>${v.Total}</strong></td>
                                <td><span class="metric">${String.format("%.1f%%", v.Pass * 100.0 / total)}</span></td>
                                <td><span class="metric" style="background:#c62828;">${String.format("%.1f%%", v.Fail * 100.0 / total)}</span></td>
                                <td><span class="metric" style="background:#e65100;">${String.format("%.1f%%", v.Blocked * 100.0 / total)}</span></td>
                                <td><span class="metric" style="background:#616161;">${String.format("%.1f%%", v["Not Test"] * 100.0 / total)}</span></td>
                                <td><span class="metric" style="background:#1565c0;">${String.format("%.1f%%", v["N/A"] * 100.0 / total)}</span></td>
                            </tr>
                            """
                        }
                        
                        html += """
                        </tbody>
                    </table>
                </div>
                        """
                    }

                    html += """
            </div>
            """

                    // 섹션 3: 분류별 실패한 시나리오 비율
                    html += """
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">❌</span>
                    분류별 실패한 시나리오
                </div>
                """

                    def hasFailures = false
                    majorMap.keySet().sort().each { major ->
                        def majorFailures = failsByMajor[major] ?: []
                        if (majorFailures.size() > 0) {
                            hasFailures = true
                            html += """
                <div class="classification-section">
                    <div class="classification-title">대분류: ${major}</div>
                    <table>
                        <thead>
                            <tr>
                                <th class="text-left">중분류</th>
                                <th class="text-left">시나리오</th>
                                <th>상태</th>
                            </tr>
                        </thead>
                        <tbody>
                            """
                            
                            majorFailures.each { fail ->
                                html += """
                            <tr>
                                <td class="text-left">${fail.minor}</td>
                                <td class="text-left">${fail.scenario}</td>
                                <td><span class="status-fail">FAIL</span></td>
                            </tr>
                                """
                            }
                            
                            html += """
                        </tbody>
                    </table>
                </div>
                            """
                        }
                    }

                    if (!hasFailures) {
                        html += "<div class='no-data'>실패한 시나리오가 없습니다.</div>"
                    }

                    html += """
            </div>
            """

                    // 섹션 4: 분류별 발견된 결함 상세
                    html += """
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">🔍</span>
                    분류별 발견된 결함 상세 정보
                </div>
                """

                    def hasDefects = false
                    majorMap.keySet().sort().each { major ->
                        def majorDefects = failsByMajor[major] ?: []
                        if (majorDefects.size() > 0) {
                            hasDefects = true
                            
                            // 중분류별로 그룹화
                            def minorDefects = [:]
                            majorDefects.each { defect ->
                                if (!minorDefects[defect.minor]) {
                                    minorDefects[defect.minor] = []
                                }
                                minorDefects[defect.minor] << defect
                            }
                            
                            html += """
                <div class="classification-section">
                    <div class="classification-title">대분류: ${major}</div>
                            """
                            
                            minorDefects.keySet().sort().each { minor ->
                                def defects = minorDefects[minor]
                                html += """
                    <div style="margin-bottom: 20px;">
                        <h4 style="color:#c62828; margin-bottom:10px;">중분류: ${minor} (${defects.size()}건)</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th class="text-left">시나리오</th>
                                    <th class="text-left">상태</th>
                                </tr>
                            </thead>
                            <tbody>
                                """
                                
                                defects.each { defect ->
                                    html += """
                                <tr>
                                    <td class="text-left">${defect.scenario}</td>
                                    <td><span class="status-fail">FAIL</span></td>
                                </tr>
                                    """
                                }
                                
                                html += """
                            </tbody>
                        </table>
                    </div>
                                """
                            }
                            
                            html += """
                </div>
                            """
                        }
                    }

                    if (!hasDefects) {
                        html += "<div class='no-data'>발견된 결함이 없습니다.</div>"
                    }

                    html += """
            </div>
        </div>
    </div>
</body>
</html>
                    """

                    writeFile file: "${RESULT_DIR}\\QA_Report.html", text: html

                    println "[INFO] HTML Report generated: ${RESULT_DIR}\\QA_Report.html"
                    println "[INFO] Total Tests: ${stats["Total"]}"
                    println "[INFO] Passed: ${stats["Pass"]}"
                    println "[INFO] Failed: ${stats["Fail"]}"
                    println "[INFO] Fail Rate: ${String.format("%.2f%%", failRate)}"

                    if (fails.size() > 0) {
                        echo "[WARN] FAIL ${fails.size()}건 발견됨"
                        error "[ERR-QA-002] FAIL ${fails.size()}건 발견"
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'Test Results/**', fingerprint: true
        }

        success {
            slackSend(channel: "#새-채널", message: "✅ QA 성공\n총 ${stats["Total"]}개 테스트 중 모두 통과")
        }

        failure {
            slackSend(channel: "#새-채널", message: "❌ QA 실패\n총 ${stats["Total"]}개 테스트 중 ${stats["Fail"]}개 실패")
        }
    }
}