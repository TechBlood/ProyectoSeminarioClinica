pipeline {
    agent any

    options {
        // Evita que Jenkins descargue el repositorio dos veces.
        skipDefaultCheckout()

        // Muestra la hora de ejecución en la consola.
        timestamps()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        DJANGO_SETTINGS_MODULE = 'clinica.settings'

        // Jenkins utilizará SQLite durante las pruebas.
        DJANGO_USE_SQLITE = '1'

        // Evita mensajes innecesarios de actualización de pip.
        PIP_DISABLE_PIP_VERSION_CHECK = '1'

        // Ruta de Python instalada en la computadora.
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
                    if exist test-reports rmdir /s /q test-reports

                    ".venv\\Scripts\\python.exe" manage.py test --verbosity=2
                '''
            }
        }
    }

    post {
        always {
            echo 'El Pipeline de Jenkins ha finalizado.'

            // Publica los archivos XML y genera la gráfica de pruebas.
            junit testResults: 'test-reports/**/*.xml',
                  allowEmptyResults: false

            // Elimina el entorno virtual temporal de Jenkins.
            bat '''
                if exist .venv rmdir /s /q .venv
            '''
        }

        success {
            echo 'Todas las pruebas de Django finalizaron correctamente.'
        }

        failure {
            echo 'Una o más etapas fallaron. Revisa la salida de consola de Jenkins.'
        }

        unstable {
            echo 'Algunas pruebas no fueron aprobadas. Revisa los resultados publicados.'
        }
    }
}