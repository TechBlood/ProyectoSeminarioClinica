/*
 * Pipeline de CI para el proyecto "Clínica de Imágenes Médicas" (Django).
 *
 * Qué hace:
 *   1. Crea un virtualenv e instala dependencias (requirements-dev.txt).
 *   2. Corre flake8 (no bloquea el build, lo marca UNSTABLE si hay avisos).
 *   3. Corre las pruebas con pytest + cobertura, contra clinica.settings_test.
 *      Django crea y destruye sola una base `test_<DB_NAME>` en el MySQL
 *      del agente (no toca la base real `clinica_imagenes`).
 *   4. Publica resultados JUnit y el reporte de cobertura en Jenkins.
 *
 * Requisitos en el agente de Jenkins (Windows, sin Docker):
 *   - Python 3.11+ con el módulo venv, accesible como `python` en el PATH
 *     del sistema (no solo del usuario): el servicio de Jenkins corre
 *     como LocalSystem, que no ve instalaciones de Python hechas "solo
 *     para mi usuario". Agrega la carpeta de instalación y su \Scripts
 *     al PATH de sistema (Variables de entorno > Sistema > Path) y
 *     reinicia el servicio de Jenkins.
 *   - Un servidor MySQL alcanzable en 127.0.0.1:3306 (en este agente: el
 *     servicio "MySQL80" ya instalado). El usuario debe tener privilegios
 *     CREATE/DROP DATABASE, porque Django crea y destruye la base
 *     `test_<DB_NAME>` en cada corrida.
 *   - Una credencial de Jenkins tipo "Secret text" con la contraseña de
 *     ese usuario de MySQL, registrada con el ID que tiene MYSQL_CRED_ID
 *     más abajo. NUNCA pongas la contraseña real en texto plano aquí: este
 *     archivo se sube a un repo compartido con el equipo.
 *
 * Plugins de Jenkins usados: JUnit, Cobertura (o "Coverage" moderno). Si no
 * los tienes instalados, comenta esas líneas en post{} sin que el resto del
 * pipeline se vea afectado.
 */

pipeline {
    agent any
@@ -40,14 +9,12 @@
    }

    environment {
        // ID de la credencial "Secret text" en Jenkins (Manage Jenkins >
        // Credentials) que guarda la contraseña real del usuario de MySQL.
        
        MYSQL_CRED_ID = 'mysql-root-password'

        DJANGO_SETTINGS_MODULE = 'clinica.settings_test'

        // Base de datos de pruebas: Django crea/destruye "test_<DB_NAME>"
        // sola en cada corrida; no es necesario crearla a mano.
       
        DB_NAME     = 'clinica_imagenes_ci'
        DB_USER     = 'root'
        DB_PASSWORD = credentials("${MYSQL_CRED_ID}")
@@ -99,7 +66,7 @@
                    call .venv-ci\\Scripts\\activate.bat
                    if not exist reports mkdir reports
                    python manage.py check
                    pytest ^
                    pytest2 ^
                        --junitxml=reports/junit.xml ^
                        --cov=accounts --cov=pacientes ^
                        --cov-report=xml:reports/coverage.xml ^
@@ -115,37 +82,28 @@
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

            // Requiere el plugin "Cobertura"; si usas el plugin "Coverage"
            // moderno, sustituye por: recordCoverage(...). Si el plugin no
            // está instalado, el paso "cobertura" ni siquiera existe como
            // método DSL y tira un NoSuchMethodError (que es un
            // java.lang.Error, no una Exception: un try/catch normal de
            // Groovy NO lo atrapa porque "catch (e)" sin tipo solo captura
            // Exception). Por eso se usa el step nativo "catchError" de
            // Jenkins, que sí intercepta cualquier Throwable a nivel de
            // step; con buildResult/stageResult en null, el error solo se
            // imprime en el log y no afecta el resultado del build.
         l build.
            script {
                if (fileExists('reports/coverage.xml')) {
                    catchError(buildResult: null, stageResult: null,
                               message: "Plugin 'Cobertura' no instalado en este Jenkins; se omite la publicación de cobertura.") {
                        cobertura coberturaReportFile: 'reports/coverage.xml'
                    }
                }
            }

            bat '''
                if exist .venv-ci rmdir /s /q .venv-ci
                if exist media_test rmdir /s /q media_test
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