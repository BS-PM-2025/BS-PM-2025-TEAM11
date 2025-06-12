pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'RequestFlow.settings'
        PYTHONPATH = "${env.WORKSPACE}"
        CI = 'true'
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
                sh 'python3 manage.py makemigrations'
                sh 'python3 manage.py migrate'
            }
        }

        stage('Run Unit + Integration Tests') {
            steps {
                echo '🧪 Running Django tests with coverage...'
                sh 'python3 -m pytest app/tests.py --ds=RequestFlow.settings --junitxml=test-results.xml || true'
            }
        }

        stage('Calculate Defect Density') {
            steps {
                echo '📊 Calculating Defect Density...'
                sh '''
                    # Count test failures from pytest results
                    FAILURES=$(grep -o 'failures="\\?[0-9]\\+"' test-results.xml | grep -o '[0-9]')

                    # Count lines of code (excluding tests/migrations/venv)
                    LOC=$(find app -name "*.py" ! -path "*tests*" ! -path "*migrations*" ! -path "*venv*" | xargs wc -l | tail -n1 | awk '{print $1}')

                    if [ "$LOC" -gt 0 ]; then
                        DEFECT_DENSITY=$(echo "scale=2; $FAILURES / $LOC * 1000" | bc)
                    else
                        DEFECT_DENSITY=0
                    fi

                    echo "📈 Defect Density: $DEFECT_DENSITY defects per 1000 LOC"
                '''
            }
        }


        stage('Code Coverage') {
            steps {
                echo '📊 Measuring code coverage with pytest-cov...'
                sh '''
                    pip install pytest-cov || true
                    python3 -m pytest app/tests.py --ds=RequestFlow.settings --cov=app --cov-report=term-missing --cov-report=xml || true
                '''
            }
        }


        stage('Static Code Check: flake8') {
          steps {
            echo '🔍 Running flake8...'
              sh '''
                  pip install flake8 || true
                  export PATH=$PATH:~/.local/bin
                  flake8 app --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics
        '''
    }
}
        stage('Static Code Check: pylint') {
          steps {
             echo '📎 Running pylint...'
            sh '''
              pip install pylint || true
              export PATH=$PATH:~/.local/bin
              pylint app --exit-zero || true
               '''
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
