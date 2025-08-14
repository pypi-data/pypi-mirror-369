from os import environ

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import declarative_base
from google.cloud.sql.connector import Connector, IPTypes

from .secrets import get_secrets_manager

db = SQLAlchemy()
BaseModel = declarative_base()
db.Model = BaseModel

connector = Connector()


def getconn():
    return connector.connect(
        environ.get("CLOUD_SQL_INSTANCE_NAME"),
        "pg8000",
        user=environ.get("CLOUD_SQL_DB_USER"),
        password="xxxxx",
        db=environ.get("CLOUD_SQL_DB_NAME"),
        enable_iam_auth=True,
        ip_type=IPTypes.PUBLIC,
    )


def init_db(app: Flask):
    """Connect `app` to the database and run migrations"""
    db.init_app(app)
    db.Model = BaseModel
    Migrate(app, db, app.config["MIGRATIONS_PATH"])
    with app.app_context():
        upgrade(app.config["MIGRATIONS_PATH"])


def get_sqlalchemy_database_uri(testing: bool = False) -> str:
    """Get the PostgreSQL DB URI from environment variables"""

    db_uri = environ.get("POSTGRES_URI")
    if testing:
        # Connect to the test database
        db_uri = environ.get("TEST_POSTGRES_URI", "fake-conn-string")
    elif not db_uri:
        # TODO: figure out why IAM authentication causes an issue with the huge filter query
        # db_uri = f"postgresql+pg8000://{environ.get('CLOUD_SQL_DB_USER')}:xxx@/{environ.get('CLOUD_SQL_DB_NAME')}"

        secrets = get_secrets_manager(testing)

        # If POSTGRES_URI env variable is not set,
        # we're connecting to a Cloud SQL instance.

        config: dict = {
            "drivername": "postgresql",
            "username": environ.get("CLOUD_SQL_DB_USER"),
            "password": secrets.get(environ.get("CLOUD_SQL_DB_PASS_ID")),
            "database": environ.get("CLOUD_SQL_DB_NAME"),
        }

        if environ.get("CLOUD_SQL_INSTANCE_NAME"):
            socket_dir = environ.get("CLOUD_SQL_SOCKET_DIR", "/cloudsql/")

            # If CLOUD_SQL_INSTANCE_NAME is defined, we're connecting
            # via a unix socket from inside App Engine.
            config["query"] = {"host": f'{socket_dir}{environ.get("CLOUD_SQL_INSTANCE_NAME")}'}
        else:
            raise RuntimeError(
                "Either POSTGRES_URI or CLOUD_SQL_INSTANCE_NAME must be defined to connect " + "to a database."
            )

        db_uri = str(URL.create(**config).render_as_string(hide_password=False))

    assert db_uri

    return db_uri


# Use SQLALCHEMY_ENGINE_OPTIONS to connect to the cloud but use uri for local db
def cloud_connector(testing: bool = False):
    return {}
    # TODO: figure out IAM authentication
    # if not testing and not environ.get("POSTGRES_URI"):
    #    return {"creator": getconn}
    # else:
    #    return {}
