from oslo_db.sqlalchemy import enginefacade

from certx.db.sqlalchemy import models


def create_schema(config=None, engine=None):
    if engine is None:
        engine = enginefacade.writer.get_engine()

    models.Base.metadata.create_all(engine)
