pipeline {
  agent any
  tools { nodejs 'nodejs' }   // Jenkins 관리 > Global Tool Configuration에 등록된 Node.js 이름

  stages {
    stage('Prepare') {
      steps {
        // 테스트 결과물(HTML)이 저장될 폴더가 없으면 생성
        bat 'if not exist newman mkdir newman'
      }
    }

    stage('Install Newman') {
      steps {
        // 글로벌 설치 대신 현재 워크스페이스에 로컬 설치하여 경로 충돌 방지
        bat 'npm install newman newman-reporter-htmlextra'
      }
    }

    stage('Run Automated Test Collections') {
      steps {
        // 환경 변수(-e) 옵션을 제거하고 컬렉션 파일만 직접 실행합니다.
        
        // 1. [전투] 합기(CA) 테스트 실행
        bat '''
        chcp 65001
        npx newman run "C:\\QA\\CI-CD-Test\\Combat_CA_Test.postman_collection.json" -r cli,htmlextra --reporter-htmlextra-export newman\\Combat_CA_Report.html
        '''
        
        // 2. [모험] 기믹/상호작용 테스트 실행
        bat '''
        chcp 65001
        npx newman run "C:\\QA\\CI-CD-Test\\Adventure_Gimmick_Test.postman_collection.json" -r cli,htmlextra --reporter-htmlextra-export newman\\Adventure_Gimmick_Report.html
        '''
      }
    }
  }

  post {
    always {
      // Newman 실행 결과로 생성된 HTML 리포트들을 젠킨스에 저장
      archiveArtifacts artifacts: 'newman/*.html', fingerprint: true
      
      // 젠킨스 빌드 화면에서 리포트를 바로 볼 수 있도록 시각화 설정
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