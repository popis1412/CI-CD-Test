pipeline {
    agent any

    stages {
        stage('Prepare') {
            steps {
                echo '이전 리포트 정리 및 폴더 생성...'
                // 윈도우 환경에 맞춰 경로 수정 및 폴더 비우기
                bat '''
                if not exist reports mkdir reports
                del /q reports\\*
                '''
            }
        }

        stage('Generate Tag Battle QA Report') {
            steps {
                echo '태그 전투 시스템 QA 리포트 생성 중...'
                
                script {
                    // 1. 데이터 설정 (정량적 지표 계산)
                    def f_total = 5, f_pass = 4, f_fail = 1, f_defect = 1
                    def c_total = 3, c_pass = 3, c_fail = 0, c_defect = 0
                    def e_total = 3, e_pass = 2, e_fail = 1, e_defect = 2
                    def u_total = 3, u_pass = 3, u_fail = 0, u_defect = 0

                    // 실패율 계산 로직
                    def calculateFailRate = { fail, total -> 
                        return total > 0 ? String.format("%.1f", (fail / total) * 100) : "0"
                    }

                    // 2. HTML 내용 작성 (특수문자 에러 방지를 위해 변수에 담기)
                    def htmlContent = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: 'Malgun Gothic', sans-serif; padding: 20px; line-height: 1.6; background: #f4f7f6; }
                            .header { background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; text-align: center; }
                            .summary-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                            .summary-table th, .summary-table td { border: 1px solid #ddd; padding: 12px; text-align: center; }
                            .summary-table th { background: #ecf0f1; font-weight: bold; }
                            .status-pass { color: #27ae60; font-weight: bold; }
                            .status-fail { color: #e74c3c; font-weight: bold; }
                            .card { background: white; border-radius: 5px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #3498db; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                            .priority-critical { background: #ffeded; color: #c0392b; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; font-weight: bold; }
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>태그 전투 시스템 QA 분석 리포트</h1>
                            <p>실행 일시: ${new Date().format('yyyy-MM-dd HH:mm:ss')}</p>
                        </div>

                        <h2>1. 테스트 결과 요약 (정량 지표)</h2>
                        <table class="summary-table">
                            <tr><th>대분류</th><th>시나리오 수</th><th>성공</th><th>실패</th><th>실패율(%)</th><th>발견 결함</th></tr>
                            <tr><td>1. 기능 테스트</td><td>${f_total}</td><td>${f_pass}</td><td class="status-fail">${f_fail}</td><td>${calculateFailRate(f_fail, f_total)}%</td><td>${f_defect}</td></tr>
                            <tr><td>2. 전투 연계 테스트</td><td>${c_total}</td><td>${c_pass}</td><td>${c_fail}</td><td>${calculateFailRate(c_fail, c_total)}%</td><td>${c_defect}</td></tr>
                            <tr><td>3. 예외 상황 테스트</td><td>${e_total}</td><td>${e_pass}</td><td class="status-fail">${e_fail}</td><td>${calculateFailRate(e_fail, e_total)}%</td><td>${e_defect}</td></tr>
                            <tr><td>4. UX / 피드백 테스트</td><td>${u_total}</td><td>${u_pass}</td><td>${u_fail}</td><td>${calculateFailRate(u_fail, u_total)}%</td><td>${u_defect}</td></tr>
                        </table>

                        <h2>2. 상세 실패 시나리오 및 결함</h2>
                        <div class="card">
                            <span class="priority-critical">1순위 (Critical)</span>
                            <h3>[기능] 캐릭터 상태(넉백, 피격 등)에 따른 교체 가능 여부 확인</h3>
                            <p>결과: <span class="status-fail">FAILED</span> (피격 애니메이션 중 교체 입력 무시 현상 발생)</p>
                            <p>관련 결함: [BUG-1021] 피격 상태 프레임 태그 인터럽트 불가</p>
                        </div>
                        <div class="card">
                            <h3>[예외] 스킬 사용 중 교체 시 충돌 여부</h3>
                            <p>결과: <span class="status-fail">FAILED</span> (특정 광역기 사용 중 교체 시 캐릭터 증발)</p>
                            <p>관련 결함: [BUG-1025] 스킬 리소스 해제 전 캐릭터 스왑 시 널 참조 에러</p>
                        </div>

                        <h2>3. 테스트 환경</h2>
                        <ul><li>AOS: 갤럭시 S20</li><li>iOS: iPhone 12 Pro</li><li>PC: i5 / 16GB</li></ul>
                    </body>
                    </html>
                    """

                    // 3. 파일 생성 (Groovy writeFile 사용으로 에러 방지)
                    writeFile file: 'reports/Tag_Battle_QA_Report.html', text: htmlContent, encoding: 'UTF-8'
                }
            }
        }
    }

    post {
        always {
            // 아카이빙 및 리포트 게시
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'Tag_Battle_QA_Report.html',
                reportName: 'Tag Battle QA Analysis Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }
        
        success {
            // 슬랙 알림 (기존 설정 유지하되 메시지 정리)
            slackSend (
                channel: '#qa-alert', 
                color: '#00FF00', 
                message: "✅ 태그 전투 시스템 테스트 완료\n성공률: 85%\n리포트 확인: ${env.BUILD_URL}Tag_20Battle_20QA_20Analysis_20Report/"
            )
        }
        
        failure {
            slackSend (
                channel: '#qa-alert', 
                color: '#FF0000', 
                message: "❌ 테스트 빌드 실패! 로그를 확인하세요: ${env.BUILD_URL}"
            )
        }
    }
}