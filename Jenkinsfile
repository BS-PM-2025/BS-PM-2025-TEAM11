pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install django || true'
            }
        }

        stage('Run Django Tests') {
            steps {
                sh 'python manage.py test app'
            }
        }
    }
}
