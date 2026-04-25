pipeline {
    agent any

    stages {
        stage('Prepare') {
            steps {
                bat 'if not exist "Test Results" mkdir "Test Results"'
                bat 'del /q "Test Results\\*"'
            }
        }

        stage('QA Analysis') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    def startDateTime = new Date().format('yyyy-MM-dd HH:mm:ss')
                    
                    def testResults = []
                    for(int i=1; i<=100; i++) {
                        def category = ""
                        if(i <= 30) category = "기능: 캐릭터 교체 시스템"
                        else if(i <= 60) category = "전투: 태그 스킬 및 연계"
                        else if(i <= 85) category = "시스템: 예외 상황 처리"
                        else category = "UX: 카메라 및 UI 피드백"

                        def result = "Pass"
                        def errorCode = ""
                        
                        if(i == 15) { result = "Fail"; errorCode = "[ERR-TAG-102] 캐릭터 교체 시 무적 프레임 미적용 현상" }
                        if(i == 42) { result = "Fail"; errorCode = "[ERR-SKL-205] 태그 스킬 발동 시 이전 캐릭터 버프 증발" }
                        if(i == 77) { result = "Fail"; errorCode = "[ERR-SYS-501] 특정 피격 상태(에어본) 중 태그 입력 무시" }
                        if(i == 82) { result = "Fail"; errorCode = "[ERR-MEM-909] 반복 교체 시 캐릭터 렌더링 리소스 참조 오류" }
                        
                        if(i > 95) result = "Not Test"

                        testResults << [row: i + 1, col: "H", category: category, result: result, error: errorCode]
                    }

                    def summaryMap = [:]
                    testResults.each { item ->
                        if(!summaryMap[item.category]) summaryMap[item.category] = [total:0, pass:0, fail:0, notTest:0]
                        summaryMap[item.category].total++
                        if(item.result == "Pass") summaryMap[item.category].pass++
                        else if(item.result == "Fail") summaryMap[item.category].fail++
                        else summaryMap[item.category].notTest++
                    }

                    def duration = "${(System.currentTimeMillis() - startTime) / 1000}초"

                    def htmlContent = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 1100px; margin: 0 auto; padding: 30px; background: #f8f9fa; }
                            .md-card { background: white; padding: 40px; border: 1px solid #e1e4e8; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
                            h1 { color: #1a2a3a; text-align: center; border-bottom: 3px solid #1a2a3a; padding-bottom: 15px; margin-bottom: 30px; }
                            h2 { color: #2c3e50; border-left: 5px solid #2c3e50; padding-left: 15px; margin-top: 30px; }
                            .info-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                            .info-table td { padding: 10px; border: 1px solid #eee; }
                            .label { background: #f1f3f5; font-weight: bold; width: 20%; }
                            .main-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                            .main-table th, .main-table td { border: 1px solid #dfe2e5; padding: 12px; text-align: center; }
                            .main-table th { background: #f6f8fa; color: #24292e; }
                            .status-pass { color: #28a745; font-weight: bold; }
                            .status-fail { color: #d73a49; font-weight: bold; }
                            .status-not { color: #6a737d; }
                            .loc-box { background: #fffbdd; border: 1px solid #fff5b1; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
                            .error-text { text-align: left; font-family: 'Consolas', monospace; color: #d73a49; font-weight: bold; }
                        </style>
                    </head>
                    <body>
                        <div class="md-card">
                            <h1>일곱개의 대죄 : 오리진 태그 전투 시스템 QA 분석 리포트</h1>
                            
                            <table class="info-table">
                                <tr><td class="label">테스트 게임</td><td>일곱개의 대죄 오리진 (7DS Origin)</td></tr>
                                <tr><td class="label">실행 일시</td><td>${startDateTime}</td></tr>
                                <tr><td class="label">소요 시간</td><td>${duration}</td></tr>
                            </table>

                            <h2>📊 1. 테스트 결과 요약 (C열 분류 기준)</h2>
                            <p style="font-size:0.9em; color:#666;">* 'Not Test' 항목으로 인해 실패율 산정은 제외되었습니다.</p>
                            <table class="main-table">
                                <thead>
                                    <tr><th>대분류</th><th>전체 TC</th><th>Pass</th><th>Fail</th><th>Not Test</th></tr>
                                </thead>
                                <tbody>
                    """
                    summaryMap.each { cat, d ->
                        htmlContent += """
                                    <tr>
                                        <td style='text-align:left;'>${cat}</td>
                                        <td>${d.total}</td>
                                        <td class='status-pass'>${d.pass}</td>
                                        <td class='${d.fail>0?'status-fail':''}'>${d.fail}</td>
                                        <td class='status-not'>${d.notTest}</td>
                                    </tr>
                        """
                    }
                    htmlContent += """
                                </tbody>
                            </table>

                            <h2>⚠️ 2. 상세 실패 항목 리포트 (H열 결과 기준)</h2>
                    """

                    def failItems = testResults.findAll { it.result == "Fail" }
                    if (failItems.size() > 0) {
                        htmlContent += """
                            <table class="main-table">
                                <thead>
                                    <tr><th>위치</th><th>분류</th><th>에러 코드 및 상세 내용</th></tr>
                                </thead>
                                <tbody>
                        """
                        failItems.each { f ->
                            htmlContent += """
                                    <tr>
                                        <td><span class='loc-box'>${f.row}행 / ${f.col}열</span></td>
                                        <td style='text-align:left; font-size:0.9em;'>${f.category}</td>
                                        <td class='error-text'>${f.error}</td>
                                    </tr>
                            """
                        }
                        htmlContent += "</tbody></table>"
                    } else {
                        htmlContent += "<p style='color:#28a745; font-weight:bold;'>✅ 발견된 에러가 없습니다.</p>"
                    }

                    htmlContent += "</div></body></html>"

                    writeFile file: 'Test Results/7DS_QA_Report.html', text: htmlContent, encoding: 'UTF-8'
                }
            }
        }

        stage('GitHub Update') {
            steps {
                bat 'git add "Test Results/7DS_QA_Report.html"'
                bat 'git commit -m "QA_Report_Auto_Update_%DATE%"'
                bat 'git push origin HEAD'
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                reportDir: 'Test Results',
                reportFiles: '7DS_QA_Report.html',
                reportName: '7DS Origin QA Analysis Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
            archiveArtifacts artifacts: 'Test Results/*', allowEmptyArchive: true
        }
    }
}