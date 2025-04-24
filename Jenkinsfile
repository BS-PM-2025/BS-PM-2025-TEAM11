pipeline {
    agent {
        docker {
            image 'python:3.10'
        }
    }

    stages {
        stage('Install Django') {
            steps {
                sh 'pip install Django'
            }
        }

        stage('Run Django Tests') {
            steps {
                sh 'python manage.py test app.tests --verbosity=2'
            }
        }
    }
}
