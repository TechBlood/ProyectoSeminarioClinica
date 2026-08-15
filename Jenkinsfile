pipeline {
    agent any

    options {
        skipDefaultCheckout()
        timestamps()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'clinica.settings'
        DJANGO_USE_SQLITE = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'

        PYTHON_EXE = 'C:\\Users\\DanielMancilla 98\\AppData\\Local\\Python\\bin\\python.exe'
    }

    stages {
        stage('Descargar proyecto') {
            steps {
                checkout scm
            }
        }

        stage('Comprobar Python') {
            steps {
                bat '''
                    "%PYTHON_EXE%" --version
                    "%PYTHON_EXE%" -m pip --version
                '''
            }
        }

        stage('Preparar entorno virtual') {
            steps {
                bat '''
                    if exist .venv rmdir /s /q .venv

                    "%PYTHON_EXE%" -m venv .venv

                    ".venv\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel

                    ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Verificar proyecto Django') {
            steps {
                bat '''
                    ".venv\\Scripts\\python.exe" manage.py check
                '''
            }
        }

        stage('Aplicar migraciones') {
            steps {
                bat '''
                    ".venv\\Scripts\\python.exe" manage.py migrate --noinput
                '''
            }
        }

        stage('Ejecutar pruebas Django') {
            steps {
                bat '''
                    ".venv\\Scripts\\python.exe" manage.py test --verbosity=2
                '''
            }
        }
    }

    post {
        success {
            echo 'Todas las pruebas de Django finalizaron correctamente.'
        }

        failure {
            echo 'Una o más etapas fallaron. Revisa la salida de consola de Jenkins.'
        }

        always {
            echo 'El Pipeline de Jenkins ha finalizado.'

            bat '''
                if exist .venv rmdir /s /q .venv
            '''
        }
    }
}