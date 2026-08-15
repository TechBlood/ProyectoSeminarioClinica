
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        
        MYSQL_CRED_ID = 'mysql-root-password'

        DJANGO_SETTINGS_MODULE = 'clinica.settings_test'

       
        DB_NAME     = 'clinica_imagenes_ci'
        DB_USER     = 'root'
        DB_PASSWORD = credentials("${MYSQL_CRED_ID}")
        DB_HOST     = '127.0.0.1'
        DB_PORT     = '3306'

        SECRET_KEY = 'clave-temporal-solo-para-pruebas-de-ci'
        DEBUG      = 'False'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Preparar entorno Python') {
            steps {
                bat '''
                    python -m venv .venv-ci
                    call .venv-ci\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint (flake8)') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat '''
                        call .venv-ci\\Scripts\\activate.bat
                        flake8 . --output-file=flake8-report.txt
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Migraciones y pruebas') {
            steps {
                bat '''
                    call .venv-ci\\Scripts\\activate.bat
                    if not exist reports mkdir reports
                    python manage.py check
                    pytest ^
                        --junitxml=reports/junit.xml ^
                        --cov=accounts --cov=pacientes ^
                       
                '''
            }
        }
    }

    
}
