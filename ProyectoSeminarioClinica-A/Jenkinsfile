pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

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
                echo --- Python launcher version ---
                py -3 --version || (echo "py launcher not found" & exit /b 1)

                echo --- Create virtualenv (.venv) ---
                py -3 -m venv .venv

                echo --- Activate virtualenv and install deps ---
                call .venv\\Scripts\\activate

                echo --- Upgrade pip ---
                .venv\\Scripts\\python.exe -m pip install --upgrade pip setuptools wheel

                echo --- Install requirements ---
                .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Apply Migrations') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                set DJANGO_USE_SQLITE=1
                .venv\\Scripts\\python.exe manage.py migrate --noinput
                '''
            }
        }

        stage('Run Login Tests') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                set DJANGO_USE_SQLITE=1
                .venv\\Scripts\\python.exe manage.py test accounts.tests.LoginViewTests
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