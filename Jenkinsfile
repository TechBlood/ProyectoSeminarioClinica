pipeline {
    agent any

    options {
        // Evita que Jenkins descargue el repositorio dos veces.
        skipDefaultCheckout()
        timestamps()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'clinica.settings'

        // Indica al proyecto que use SQLite durante las pruebas de Jenkins.
        DJANGO_USE_SQLITE = '1'

        // Evita mensajes innecesarios de actualización de pip.
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
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
                    python --version
                    python -m pip --version
                '''
            }
        }

        stage('Preparar entorno virtual') {
            steps {
                bat '''
                    if exist .venv rmdir /s /q .venv

                    python -m venv .venv

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