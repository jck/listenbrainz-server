import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# This value must be incremented after schema changes on replicated tables!
SCHEMA_VERSION = 1

engine = None


def init_db_connection(connect_str):
    """Initializes database connection using the specified Flask app.

    Configuration file must contain `SQLALCHEMY_DATABASE_URI` key. See
    https://pythonhosted.org/Flask-SQLAlchemy/config.html#configuration-keys
    for more info.
    """
    global engine
    engine = create_engine(connect_str, poolclass=NullPool)


def run_sql_script(sql_file_path):
    with open(sql_file_path) as sql:
        with engine.connect() as connection:
            connection.execute(sql.read())


def run_sql_script_without_transaction(sql_file_path):
    with open(sql_file_path) as sql:
        connection = engine.connect()
        connection.connection.set_isolation_level(0)
        lines = sql.read().splitlines()
        try:
            for line in lines:
                # TODO: Not a great way of removing comments. The alternative is to catch
                # the exception sqlalchemy.exc.ProgrammingError "can't execute an empty query"
                if line and not line.startswith("--"):
                    connection.execute(line)
        except sqlalchemy.exc.ProgrammingError as e:
            print("Error: {}".format(e))
            return False
        finally:
            connection.connection.set_isolation_level(1)
            connection.close()
        return True
