from datetime import datetime, timedelta, UTC


def test_username(test, client):
    r = test(client, 'get', '/time/', 200, True)
    now = datetime.now(UTC)
    time = datetime.fromisoformat(r.get('data'))
    assert now - time < timedelta(minutes=1)

