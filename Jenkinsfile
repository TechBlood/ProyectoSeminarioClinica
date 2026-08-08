pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'clinica.settings'
        DJANGO_USE_SQLITE = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python') {
            steps {
                bat '''
                python -m venv .venv
                call .venv\Scripts\activate
                python -m pip install --upgrade pip setuptools wheel
                pip install -r requirements.txt
                '''
            }
        }

        stage('Apply Migrations') {
            steps {
                bat '''
                call .venv\Scripts\activate
                python manage.py migrate --noinput
                '''
            }
        }

        stage('Run Login Tests') {
            steps {
                bat '''
                call .venv\Scripts\activate
                python manage.py test accounts.tests.LoginViewTests
                '''
            }
        }
    }

    post {
        always {
            echo 'Jenkins pipeline finished.'
        }
        success {
            echo 'Login tests passed successfully.'
        }
        failure {
            echo 'Login tests failed. Review the console output for details.'
        }
    }
}
