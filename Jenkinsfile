pipeline {
    agent any

    environment {
        // GitHub 인증 정보 ID (젠킨스 Credentials에 등록된 ID)
        // 만약 ID가 다르다면 아래 'github-credentials-id'를 실제 ID로 수정하세요.
        GIT_CRED = 'github-credentials-id' 
        REPO_URL = 'https://github.com/popis1412/CI-CD-Test.git'
    }

    stages {
        stage('Prepare') {
            steps {
                echo '기존 Test Results 폴더 정리...'
                // 윈도우 환경에서 공백이 있는 폴더 생성 및 정리
                bat '''
                if not exist "Test Results" mkdir "Test Results"
                del /q "Test Results"\\*
                '''
            }
        }

        stage('QA Analysis & Create Report') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    def startDateTime = new Date().format('yyyy-MM-dd HH:mm:ss')
                    
                    // 데이터 시뮬레이션 (100개)
                    def testResults = []
                    for(int i=1; i<=100; i++) {
                        def category = (i <= 30) ? "기능: 캐릭터 교체" : (i <= 60) ? "전투: 스킬 연계" : "기타: 시스템"
                        def result = "Pass"
                        def errorCode = ""
                        
                        if(i == 15) { result = "Fail"; errorCode = "[ERROR 101] 네트워크 연결이 끊겼습니다." }
                        if(i == 55) { result = "Fail"; errorCode = "[ERROR 404] 리소스 참조 오류" }
                        if(i > 95) result = "Not Test"

                        testResults << [row: i + 1, col: "H", category: category, result: result, error: errorCode]
                    }

                    // 요약 데이터 계산
                    def summaryMap = [:]
                    testResults.each { item ->
                        if(!summaryMap[item.category]) summaryMap[item.category] = [total:0, pass:0, fail:0, notTest:0]
                        summaryMap[item.category].total++
                        if(item.result == "Pass") summaryMap[item.category].pass++
                        else if(item.result == "Fail") summaryMap[item.category].fail++
                        else summaryMap[item.category].notTest++
                    }

                    def duration = "${(System.currentTimeMillis() - startTime) / 1000}초"

                    // HTML 리포트 내용 작성
                    def htmlContent = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: 'Malgun Gothic', sans-serif; padding: 30px; background: #f4f6f8; }
                            .container { background: white; padding: 40px; border-radius: 10px; border: 1px solid #d1d5da; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
                            h1 { border-bottom: 3px solid #24292e; padding-bottom: 10px; text-align: center; }
                            .info-table, .data-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                            .info-table td { padding: 8px; border: 1px solid #eee; }
                            .info-label { background: #f6f8fa; font-weight: bold; width: 20%; }
                            .data-table th, .data-table td { border: 1px solid #dfe2e5; padding: 12px; text-align: center; }
                            .data-table th { background: #f6f8fa; }
                            .status-pass { color: #28a745; font-weight: bold; }
                            .status-fail { color: #d73a49; font-weight: bold; }
                            .location-tag { background: #fffbdd; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; border: 1px solid #fff5b1; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>일곱개의 대죄 : 오리진 태그 전투 시스템 QA 분석 리포트</h1>
                            <table class="info-table">
                                <tr><td class="info-label">테스트 게임</td><td>일곱개의 대죄 오리진 (7DS Origin)</td></tr>
                                <tr><td class="info-label">실행 일시</td><td>${startDateTime}</td></tr>
                                <tr><td class="info-label">소요 시간</td><td>${duration}</td></tr>
                            </table>

                            <h2>📊 분류별 결과 요약</h2>
                            <table class="data-table">
                                <thead><tr><th>대분류</th><th>전체</th><th>Pass</th><th>Fail</th><th>Not Test</th></tr></thead>
                                <tbody>
                    """
                    summaryMap.each { cat, d ->
                        htmlContent += "<tr><td>${cat}</td><td>${d.total}</td><td class='status-pass'>${d.pass}</td><td class='${d.fail>0?'status-fail':''}'>${d.fail}</td><td>${d.notTest}</td></tr>"
                    }
                    htmlContent += "</tbody></table>"

                    htmlContent += "<h2>⚠️ 실패 항목 상세 리스트</h2>"
                    def failItems = testResults.findAll { it.result == "Fail" }
                    if(failItems.size() > 0) {
                        htmlContent += "<table class='data-table'><thead><tr><th>위치</th><th>분류</th><th>에러 메시지</th></tr></thead><tbody>"
                        failItems.each { item ->
                            htmlContent += "<tr><td><span class='location-tag'>${item.row}행 / ${item.col}열</span></td><td>${item.category}</td><td style='text-align:left; color:#d73a49;'>${item.error}</td></tr>"
                        }
                        htmlContent += "</tbody></table>"
                    } else {
                        htmlContent += "<p>발견된 에러가 없습니다.</p>"
                    }

                    htmlContent += "</div></body></html>"

                    // 파일 저장 경로 변경: "Test Results" 폴더 안으로
                    writeFile file: 'Test Results/7DS_QA_Report.html', text: htmlContent, encoding: 'UTF-8'
                }
            }
        }

        stage('Push to GitHub') {
            steps {
                echo 'GitHub의 Test Results 폴더에 리포트 업로드 중...'
                // 깃 허브에 변경사항 저장
                bat '''
                git add "Test Results/7DS_QA_Report.html"
                git commit -m "QA Report 자동 업데이트: %DATE% %TIME%"
                git push origin master
                '''
            }
        }
    }

    post {
        always {
            // 젠킨스 대시보드에서도 볼 수 있게 게시
            publishHTML(target: [
                reportDir: 'Test Results',
                reportFiles: '7DS_QA_Report.html',
                reportName: '7DS Origin QA Analysis Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
            archiveArtifacts artifacts: 'Test Results/*', allowEmptyArchive: true
        }
        
        success {
            slackSend (
                channel: '#qa-alert', 
                color: '#00FF00', 
                message: "✅ [7DS Origin] 테스트 완료 및 GitHub 업로드 성공\n경로: /Test Results/7DS_QA_Report.html\n리포트: ${env.BUILD_URL}7DS_20Origin_20QA_20Analysis_20Report/"
            )
        }
    }
}