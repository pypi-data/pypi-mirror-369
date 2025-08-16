from typing import List

from sqlalchemy import create_engine, Engine, Table


def init_test_db(tables: List[Table]) -> Engine:
    engine = create_engine("sqlite:///", echo=False)
    for t in tables:
        t.create(bind=engine, checkfirst=True)

    return engine
