from pjdev_postgres import postgres_service
from pjdev_postgres.models import Savable, History
from sqlmodel import Session, select
from utilities import init_test_db
import pytz

def test_history_item_is_created_and_saved():
    class MockObj(Savable):
        pass

    class MockTable(MockObj, table=True):
        pass

    engine = init_test_db([MockTable.__table__, History.__table__])

    with Session(engine) as session:
        obj = MockTable()
        session.add(obj)
        saved_obj = postgres_service.save(
            obj, session=session
        )

        assert saved_obj.last_modified_datetime is not None
        assert saved_obj.last_modified_by is not None
        assert saved_obj.last_modified_by_id is not None

    with Session(engine) as session2:
        mock_row: MockTable = session2.exec(
            select(MockTable).where(MockTable.id == obj.id)
        ).one_or_none()
        history_mock = session2.exec(select(History)).all()
        assert len(history_mock) == 1
        assert mock_row is not None
        assert history_mock[0].entity_name == mock_row.__tablename__

        # Must use the base model (not the model with table=True) to validate due to this:
        #   https://github.com/tiangolo/sqlmodel/issues/52#issuecomment-1311987732

        historical_mock_row = MockObj.model_validate_json(history_mock[0].value)

        # Must add the utc timezone info due to sqlite not preserving tz info
        mock_row.last_modified_datetime = pytz.utc.localize(mock_row.last_modified_datetime)
        mock_row.created_datetime = pytz.utc.localize(mock_row.created_datetime)

        assert historical_mock_row == MockObj.model_validate(mock_row)
        assert mock_row.last_modified_datetime is not None
        assert mock_row.last_modified_by is not None
        assert mock_row.last_modified_by_id is not None
