/*
 * Pipeline de CI para el proyecto "Clínica de Imágenes Médicas" (Django).
 *
 * Qué hace:
 *   1. Levanta un MySQL 8 desechable en Docker (no toca la base real del
 *      proyecto; Django crea y destruye sola una base `test_<DB_NAME>`).
 *   2. Crea un virtualenv e instala dependencias (requirements-dev.txt).
 *   3. Corre flake8 (no bloquea el build, lo marca UNSTABLE si hay avisos).
 *   4. Corre las pruebas con pytest + cobertura, contra clinica.settings_test.
 *   5. Publica resultados JUnit y el reporte de cobertura en Jenkins.
 *
 * Requisitos en el agente de Jenkins:
 *   - Docker disponible (para el contenedor de MySQL de pruebas).
 *   - Python 3.11+ con el módulo venv.
 *   - Librerías de compilación de mysqlclient: en Debian/Ubuntu
 *     `default-libmysqlclient-dev build-essential pkg-config`
 *     (si el agente ya las tiene, o mysqlclient trae wheel precompilado
 *     para tu plataforma, este paso es un no-op).
 *
 * Plugins de Jenkins usados: JUnit, Cobertura (o "Coverage" moderno). Si no
 * los tienes instalados, comenta esas líneas en post{} sin que el resto del
 * pipeline se vea afectado.
 */

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        // Contenedor MySQL de pruebas, aislado del MySQL real del proyecto.
        MYSQL_TEST_CONTAINER = "clinica-mysql-test-${env.BUILD_NUMBER}"
        MYSQL_TEST_PORT       = '3307'
        DJANGO_SETTINGS_MODULE = 'clinica.settings_test'

        // Credenciales de la base de datos de pruebas (no son secretas: la
        // base vive y muere dentro del mismo build).
        DB_NAME     = 'clinica_imagenes_ci'
        DB_USER     = 'root'
        DB_PASSWORD = 'root_ci_password'
        DB_HOST     = '127.0.0.1'
        DB_PORT     = "${MYSQL_TEST_PORT}"

        SECRET_KEY = 'clave-temporal-solo-para-pruebas-de-ci'
        DEBUG      = 'False'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Levantar MySQL de pruebas') {
            steps {
                sh '''
                    docker rm -f "$MYSQL_TEST_CONTAINER" >/dev/null 2>&1 || true
                    docker run -d --name "$MYSQL_TEST_CONTAINER" \
                        -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" \
                        -e MYSQL_DATABASE="$DB_NAME" \
                        -p "$MYSQL_TEST_PORT":3306 \
                        mysql:8.0 --default-authentication-plugin=mysql_native_password

                    echo "Esperando a que MySQL acepte conexiones..."
                    for i in $(seq 1 30); do
                        if docker exec "$MYSQL_TEST_CONTAINER" mysqladmin ping -uroot -p"$DB_PASSWORD" --silent; then
                            echo "MySQL listo."
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "MySQL no respondió a tiempo." >&2
                    exit 1
                '''
            }
        }

        stage('Preparar entorno Python') {
            steps {
                sh '''
                    python3 -m venv .venv-ci
                    . .venv-ci/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint (flake8)') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh '''
                        . .venv-ci/bin/activate
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
                sh '''
                    . .venv-ci/bin/activate
                    mkdir -p reports
                    python manage.py check
                    pytest \
                        --junitxml=reports/junit.xml \
                        --cov=accounts --cov=pacientes \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/htmlcov \
                        --cov-report=term-missing
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

            // Requiere el plugin "Cobertura"; si usas el plugin "Coverage"
            // moderno, sustituye por: recordCoverage(...)
            script {
                if (fileExists('reports/coverage.xml')) {
                    cobertura coberturaReportFile: 'reports/coverage.xml'
                }
            }

            sh '''
                docker rm -f "$MYSQL_TEST_CONTAINER" >/dev/null 2>&1 || true
                rm -rf .venv-ci media_test
            '''
        }
        success {
            echo 'Pipeline OK: pruebas y lint completados.'
        }
        unstable {
            echo 'Pipeline inestable: revisa el reporte de flake8.'
        }
        failure {
            echo 'Pipeline falló: revisa reports/junit.xml y la consola.'
        }
    }
}
