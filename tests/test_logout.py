import pytest

from tests.conftest import tokens


@pytest.mark.parametrize('n', range(2))
def test_delete_avatar(test, client, n):
    expected_status = [200, 406][n]
    expected_success = [True, False][n]
    test(client, 'delete', '/user/avatar/', expected_status, expected_success, None, tokens)


@pytest.mark.parametrize('_', range(4))
def test_logout(test, client, _):
    test(client, 'delete', '/user/logout/', 200, True, None, tokens)
    tokens.pop(0)

