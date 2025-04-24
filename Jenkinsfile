pipeline {
    agent any

    stages {
        stage('Setup Environment') {
            steps {
                // Install pip and Django
                sh 'python -m pip install --upgrade pip'
                sh 'pip install Django'
            }
        }

        stage('Run Django Tests') {
            steps {
                // Run the tests for your Django app
                sh 'python manage.py test'
            }
        }
    }
}
