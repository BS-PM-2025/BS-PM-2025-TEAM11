pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt || pip install Django'
            }
        }

        stage('Run Django Tests') {
            steps {
                sh 'python manage.py test app'
            }
        }
    }
}
