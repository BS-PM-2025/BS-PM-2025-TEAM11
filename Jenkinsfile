pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing dependencies...'
                sh '''
                    if [ -f requirements.txt ]; then
                        pip3 install -r requirements.txt
                    else
                        echo "⚠️ requirements.txt not found, installing manually..."
                        pip3 install Django pytest pytest-django
                    fi
                '''
            }
        }

        stage('Prepare Database') {
            steps {
                echo '🗄️ Running migrations...'
                sh 'python3 manage.py migrate'
            }
        }

        stage('Run Unit + Integration Tests') {
            steps {
                echo '🧪 Running Django tests with coverage...'
                sh 'pytest --junitxml=test-results.xml || python3 manage.py test'
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
