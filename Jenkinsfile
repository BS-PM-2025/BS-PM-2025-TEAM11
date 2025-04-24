pipeline {
    agent any

    stages {
        stage('Install dependencies') {
            steps {
                sh 'pip install -r requirements.txt || true' // Will not fail if requirements.txt doesn't exist
            }
        }

        stage('Run Django Tests') {
            steps {
                sh 'python manage.py test app'
            }
        }
    }
}
