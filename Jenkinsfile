pipeline {
    agent any

    stages {
        stage('Install dependencies') {
            steps {
                sh 'pip install -r requirements.txt || true' // if no file, continue anyway
            }
        }

        stage('Run Django Tests') {
            steps {
                sh 'python manage.py test app'
            }
        }
    }
}
