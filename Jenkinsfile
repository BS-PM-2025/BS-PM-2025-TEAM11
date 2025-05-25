pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'BS_PM_2025.settings'  // ← שים כאן את הנתיב של settings.py שלך
        CI = 'true'  // ← זה יסמן ל־settings.py להשתמש ב־ci_db.sqlite3
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
                echo '🗄️ Preparing database...'
                sh 'python manage.py makemigrations'
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
