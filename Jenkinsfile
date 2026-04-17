pipeline {
  agent any
  tools { nodejs 'nodejs' }   // Manage Jenkins > Global Tool Configuration에서 등록한 이름

  stages {
    stage('Prepare') {
      steps {
        // 테스트 결과물(HTML)이 저장될 빈 폴더 생성
        bat 'if not exist newman mkdir newman'
      }
    }

    stage('Install Newman') {
      steps {
        // 환경 변수 충돌을 막기 위해 -g를 제외하고 프로젝트 내부에 로컬 설치
        bat 'npm install newman newman-reporter-htmlextra'
      }
    }

    stage('Run Automated Test Collections') {
      steps {
        // chcp 65001: 젠킨스 로그 한글 깨짐 방지용 UTF-8 설정
        // npx: 로컬에 설치된 newman을 강제로 찾아 실행
        // 실제 파일이 존재하는 C:\QA\CI-CD-Test 절대 경로 적용
        
        // 1. [전투] 합기(CA) 테스트 실행
        bat '''
        chcp 65001
        npx newman run "C:\\QA\\CI-CD-Test\\Combat_CA_Test.postman_collection.json" -e "C:\\QA\\CI-CD-Test\\7DS_Origin_ENV.postman_environment.json" -r cli,htmlextra --reporter-htmlextra-export newman\\Combat_CA_Report.html --export-environment 7DS_Origin_ENV.postman_environment.json
        '''
        
        // 2. [모험] 기믹/상호작용 테스트 실행
        bat '''
        chcp 65001
        npx newman run "C:\\QA\\CI-CD-Test\\Adventure_Gimmick_Test.postman_collection.json" -e "C:\\QA\\CI-CD-Test\\7DS_Origin_ENV.postman_environment.json" -r cli,htmlextra --reporter-htmlextra-export newman\\Adventure_Gimmick_Report.html
        '''
      }
    }
  }

  post {
    always {
      // 1. Newman이 newman 폴더 안에 만들어낸 HTML 파일들을 젠킨스로 가져옴
      archiveArtifacts artifacts: 'newman/*.html', fingerprint: true
      
      // 2. 가져온 HTML 파일들을 젠킨스 빌드 페이지의 대시보드(버튼)로 시각화 연결
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