pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt || pip3 install Django'
            }
        }

        stage('Run Django Tests') {
            steps {
                sh 'python3 manage.py test app'
            }
        }
    }
}
