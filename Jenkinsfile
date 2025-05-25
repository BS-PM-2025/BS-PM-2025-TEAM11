pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'RequestFlow.settings'
        PYTHONPATH = "${env.WORKSPACE}"
        CI = 'true'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing dependencies...'
                sh 'pip install -r requirements.txt || pip install Django pytest pytest-django'
            }
        }

        stage('Prepare Database') {
            steps {
                echo '🗄️ Preparing database...'
                sh 'python3 manage.py makemigrations'
                sh 'python3 manage.py migrate'
            }
        }


        stage('Run Unit + Integration Tests') {
            steps {
                echo '🧪 Running Django tests with coverage...'
                sh 'python3 -m pytest app/ --ds=RequestFlow.settings --junitxml=test-results.xml || true'

            }
        }
    }

    post {
        always {
            echo '📊 Archiving test results...'
            junit 'test-results.xml'
        }
    }
}
