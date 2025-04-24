pipeline {
    agent any

    stages {
        stage('Install Django') {
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
