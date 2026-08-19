# Shim: use PyMySQL as MySQLdb on Windows if mysqlclient is not installed.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # If pymysql is not available, keep default (mysqlclient) behavior.
    pass
