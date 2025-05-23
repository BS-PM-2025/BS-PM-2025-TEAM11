pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
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
                echo '🗄️ Running migrations...'
                sh 'python manage.py migrate'
            }
        }

        stage('Run Unit + Integration Tests') {
            steps {
                echo '🧪 Running Django tests with coverage...'
                sh 'pytest --junitxml=test-results.xml'
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
