import pytest
from datetime import datetime, UTC
from dotenv import load_dotenv
from os import getenv, path

from bcrypt import hashpw, gensalt
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.utils.user import create_token
from tests.data.user import test_admin
import app.settings as settings


TEST_ORDER = [
    'server_time',
    'user',
    'image',
    'admin',
    'logout',
]
load_dotenv('env/.env.test')
tokens = []


def pytest_collection_modifyitems(session, config, items):
    file_order = []
    for i in TEST_ORDER:
        if not i.startswith('test_'): i = 'test_' + i
        if not i.endswith('.py'): i += '.py'
        i = path.normpath(path.join('tests', i))
        file_order.append(i)
    #
    order_lookup = {name: index for index, name in enumerate(file_order)}
    filtered_items = [i for i in items if path.normpath(i.location[0]) in order_lookup]
    #
    def get_order(item):
        file_path = path.normpath(item.location[0])
        return order_lookup.get(file_path, 1000)  # Default order if not specified
    #
    filtered_items.sort(key=get_order)
    items[:] = filtered_items


@pytest.fixture(scope='session', autouse=True)
async def teardown_db():
    yield
    client = AsyncIOMotorClient(getenv('MONGO_URI'))
    db_name = client.get_default_database().name
    await client.drop_database(db_name)


@pytest.fixture(scope='module')
async def admin():
    client = AsyncIOMotorClient(getenv('MONGO_URI'))
    db = client.get_default_database()
    #
    hashed_password = hashpw(test_admin['password'].encode('utf-8'), gensalt(rounds=settings.HASHING_COST))
    test_admin['password'] = hashed_password.decode('utf-8')
    test_admin['registration_datetime'] = datetime.now(UTC)
    test_admin['is_user_active'] = True
    test_admin['is_admin'] = True
    # 
    admin_user = await db.User.insert_one(test_admin)
    #
    token = create_token(str(admin_user.inserted_id))
    hashed_token = hashpw(token.encode('utf-8'), gensalt(rounds=settings.HASHING_COST)).decode('utf-8')
    # 
    await db.User.update_one(
        {'_id': admin_user.inserted_id},
        {'$push': {'tokens': hashed_token}}
    )
    # 
    yield token


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test():
    def general_test(client, method, url, status, success, data=None, tokens=None):
        method = getattr(client, method)
        if tokens:
            headers = {'Authorization': f'Bearer {tokens[0]}'}
        if data and tokens:
            response = method(url, json=data, headers=headers)
        elif data and not tokens:
            response = method(url, json=data)
        elif not data and tokens:
            response = method(url, headers=headers)
        else:
            response = method(url)
        # ~~~~~ ~~~~~ ~~~~~ #
        if tokens:
            for token in tokens:
                print(token[:32]+'...')
            print()
        print(response.json())
        # ~~~~~ ~~~~~ ~~~~~ #
        assert response.status_code == status
        assert bool(response.json().get('success')) == success
        return response.json()
    return general_test


@pytest.fixture
def admin_test():
    def general_test(client, admin, method, url, status, success, data=None):
        method = getattr(client, method)
        headers = {'Authorization': f'Bearer {admin}'}
        if data:
            response = method(url, json=data, headers=headers)
        else:
            response = method(url, headers=headers)
        # ~~~~~ ~~~~~ ~~~~~ #
        print(response.json())
        # ~~~~~ ~~~~~ ~~~~~ #
        assert response.status_code == status
        assert bool(response.json().get('success')) == success
        return response.json()
    return general_test

