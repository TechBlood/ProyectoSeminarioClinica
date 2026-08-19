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
                python -m venv .venv
                ".venv\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel
                ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Apply Migrations') {
            steps {
                bat '''
                ".venv\\Scripts\\python.exe" manage.py migrate --noinput
                '''
            }
        }

        stage('Run Tests') {
    steps {
        bat '''
        ".venv\\Scripts\\python.exe" manage.py test pacientes.tests.PacienteTests
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