import pytest

from tests.data.user import user_pagination_data, image_pagination_data


users = []


def attrs_to_url_params(attrs):
    url_params = '?'
    params = [f'{k}={v}' for k,v in attrs.items()]
    url_params += '&'.join(params)
    return url_params


def test_get_all_users(admin_test, client, admin):
    global users
    r = admin_test(client, admin, 'get', '/admin/user/', 200, True)
    users = [i['id'] for i in r.get('data').get('items')]


@pytest.mark.parametrize('attrs', user_pagination_data)
def test_get_all_users_pagination(admin_test, client, admin, attrs):
    url_params = attrs_to_url_params(attrs)
    admin_test(client, admin, 'get', f'/admin/user/{url_params}', 200, True)


@pytest.mark.parametrize('n', range(2))
def test_get_user_by_id(admin_test, client, admin, n):
    admin_test(client, admin, 'get', f'/admin/user/{users[n]}', 200, True)


@pytest.mark.parametrize('n', range(2))
def test_active_or_deactive_a_user(admin_test, client, admin, n):
    r = admin_test(client, admin, 'patch', f'/admin/user/activate/{users[0]}', 200, True)
    assert r.get('data').get('is_user_active') == [False, True][n]


@pytest.mark.parametrize('attrs', image_pagination_data)
def test_get_all_images(admin_test, client, admin, attrs):
    url_params = attrs_to_url_params(attrs)
    admin_test(client, admin, 'get', f'/admin/media/image/{url_params}', 200, True)

