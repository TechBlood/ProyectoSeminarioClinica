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
                @echo off
                echo --- Checking Python 3.12 Installation ---
                "C:\\Users\\Marilin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --version || (echo "Python not found at specified path" & exit /b 1)

                echo --- Create virtualenv (.venv) ---
                "C:\\Users\\Marilin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m venv .venv

                echo --- Upgrade pip ---
                ".venv\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel

                echo --- Install requirements ---
                ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Apply Migrations') {
            steps {
                bat '''
                @echo off
                set DJANGO_USE_SQLITE=1
                ".venv\\Scripts\\python.exe" manage.py migrate --noinput
                '''
            }
        }

        stage('Run Login Tests') {
            steps {
                bat '''
                @echo off
                set DJANGO_USE_SQLITE=1
                ".venv\\Scripts\\python.exe" manage.py test accounts.tests.LoginViewTests
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