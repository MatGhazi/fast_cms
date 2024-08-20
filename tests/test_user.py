import pytest
import os

from app.utils.user import otp_store
from tests.conftest import tokens
from tests.data import user


DATA_PATH = 'tests/data/'
SCHEMA = 'data, expected_status, expected_success'


@pytest.mark.parametrize(SCHEMA, user.username_data)
def test_username(test, client, data, expected_status, expected_success):
    test(client, 'post', '/user/available/', expected_status, expected_success, data)


@pytest.mark.parametrize(SCHEMA, user.join_data)
def test_join(test, client, data, expected_status, expected_success):
    r = test(client, 'post', '/user/join/', expected_status, expected_success, data)
    if r.get('success'): tokens.append(r['data']['token'])


def test_get_delete_account_reasons(test, client):
    test(client, 'get', '/user/reasons/', 200, True, None, tokens)


@pytest.mark.parametrize(SCHEMA, user.deleteme_data)
def test_delete_me(test, client, data, expected_status, expected_success):
    r1 = test(client, 'post', '/user/deleteme/', expected_status, expected_success, data, tokens)
    login_data = {
        'usemo': user.test_user['username'],
        'password': user.test_user['password'],
    }
    if r1.get('success') == True:
        tokens.pop(0)
        r2 = test(client, 'post', '/user/login/', expected_status, expected_success, login_data)
        if r2.get('success'):
            tokens.append(r2['data']['token'])
            assert r2['data']['deletion_canceled'] == True


@pytest.mark.parametrize(SCHEMA, user.login_data)
def test_login(test, client, data, expected_status, expected_success):
    r = test(client, 'post', '/user/login/', expected_status, expected_success, data)
    if r.get('success'): tokens.append(r['data']['token'])


@pytest.mark.parametrize(SCHEMA, user.profile_data)
def test_update_profile(test, client, data, expected_status, expected_success):
    test(client, 'put', '/user/profile/', expected_status, expected_success, data, tokens)


def test_get_profile(test, client):
    test(client, 'get', '/user/profile/', 200, True, None, tokens)


@pytest.mark.parametrize('_', range(2))
def test_update_avater(client, _):
    headers = {'Authorization': f'Bearer {tokens[0]}'}
    test_file = 'avatar_1.jpg'
    with open(os.path.join(DATA_PATH, test_file), 'rb') as file:
        files = {'file': (test_file, file, 'image/jpeg')}
        response = client.put('/user/avatar/', headers=headers, files=files)
        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('data').get('image_id')


@pytest.mark.parametrize(SCHEMA, user.otp_request_data)
def test_request_for_an_otp(test, client, data, expected_status, expected_success):
    test(client, 'patch', '/user/otp/', expected_status, expected_success, data)


@pytest.mark.parametrize(SCHEMA, user.reset_password_data)
def test_reset_password(test, client, data, expected_status, expected_success):
    data['otp'] = otp_store[user.test_user.get('email')]
    test(client, 'put', '/user/password/', expected_status, expected_success, data)

