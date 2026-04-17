pipeline {
  agent any
  tools { nodejs 'nodejs' }   // Manage Jenkins > Global Tool Configuration에서 등록한 이름

  stages {
    stage('Prepare') {
      steps {
        bat 'if not exist newman mkdir newman'
      }
    }

    stage('Install Newman') {
      steps {
        bat 'npm install -g newman newman-reporter-htmlextra'
      }
    }

    stage('Run Automated Test Collections') {
      steps {
        // 게임 환경 변수 파일 적용 (예: DEV, QA, STG 환경 분리용)
        // 1. [전투] 합기(CA) 관련 백엔드/API 검증 (예: 게이지 충전량, 피격 판정 데이터 등)
        bat 'newman run Combat_CA_Test.postman_collection.json -e 7DS_Origin_ENV.postman_environment.json -r cli,htmlextra --reporter-htmlextra-export newman\\Combat_CA_Report.html --export-environment 7DS_Origin_ENV.postman_environment.json'
        
        // 2. [모험] 기믹/상호작용 관련 백엔드/API 검증 (예: 기믹 해결 후 보상 스폰, 상태 초기화 로직 등)
        bat 'newman run Adventure_Gimmick_Test.postman_collection.json -e 7DS_Origin_ENV.postman_environment.json -r cli,htmlextra --reporter-htmlextra-export newman\\Adventure_Gimmick_Report.html'
      }
    }
  }

  post {
    always {
      // Newman 테스트 결과물(HTML 리포트) 아카이빙
      archiveArtifacts artifacts: 'newman/*.html', fingerprint: true
      
      // HTML Publisher 플러그인을 통한 대시보드 시각화
      publishHTML(target: [
        reportDir: 'newman',
        reportFiles: 'Combat_CA_Report.html,Adventure_Gimmick_Report.html',
        reportName: '7DS Origin QA Automation Reports',
        keepAll: true,
        alwaysLinkToLastBuild: true
      ])
    }
  }
}