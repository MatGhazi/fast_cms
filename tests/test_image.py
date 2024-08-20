import pytest

from tests.conftest import tokens


@pytest.fixture
def avatar_id(test, client):
    r = test(client, 'get', '/user/profile/', 200, True, None, tokens)
    return r['data']['avatar']


def test_get_avatar_1(client, avatar_id):
    headers = {'Authorization': f'Bearer {tokens[0]}'}
    r = client.get(f'/media/image/{avatar_id}/thumbnail/', headers=headers)
    assert r.headers['content-type'] == 'image/webp'
    assert r.status_code == 200


def test_get_avatar_2(client, avatar_id):
    headers = {'Authorization': f'Bearer {tokens[0]}'}
    r = client.get(f'/media/image/{avatar_id}/full/', headers=headers)
    assert r.headers['content-type'] == 'image/webp'
    assert r.status_code == 200


def test_get_avatar_3(client, avatar_id):
    headers = {'Authorization': f'Bearer {tokens[0]}'}
    r = client.get(f'/media/image/{avatar_id}/', headers=headers)
    assert r.headers['content-type'] != 'image/webp'
    assert r.status_code == 405


def test_get_avatar_4(client, avatar_id):
    r = client.get(f'/media/image/{avatar_id}/thumbnail/')
    assert r.json().get('detail')
    assert r.status_code != 200


def test_get_avatar_5(client, avatar_id):
    r = client.get(f'/media/image/{avatar_id}/full/')
    assert r.json().get('detail')
    assert r.status_code != 200


def test_get_avatar_6(client, avatar_id):
    r = client.get(f'/media/image/{avatar_id}/')
    assert r.headers['content-type'] != 'image/webp'
    assert r.status_code == 405


def test_get_avatar_7(client):
    avatar_id = '12345'
    r = client.get(f'/media/image/{avatar_id}/full/')
    assert r.headers['content-type'] != 'image/webp'
    assert r.status_code == 401
