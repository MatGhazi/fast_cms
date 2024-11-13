import asyncio
from datetime import datetime
from app.models.user import User

async def populate_db():
    await User.get_motor_collection().delete_many({})

    users = [
        User(
            username="user1",
            mobile="1234567890",
            email="user1@example.com",
            password="hashed_password_1",
            registration_datetime=datetime.utcnow(),
            is_user_active=True,
            is_admin=False,
            first_name="John",
            last_name="Doe",
            bio="Hello, I'm John!",
            # avatar="path/to/avatar1.png"
        ),
        User(
            username="admin1",
            mobile="0987654321",
            email="admin1@example.com",
            password="hashed_password_2",
            registration_datetime=datetime.utcnow(),
            is_user_active=True,
            is_admin=True,
            first_name="Admin",
            last_name="One",
            bio="I'm the admin!",
            # avatar="path/to/avatar2.png"
        ),
        User(
            username="user2",
            mobile="1122334455",
            email="user2@example.com",
            password="hashed_password_3",
            registration_datetime=datetime.utcnow(),
            is_user_active=False,  # Inactive user
            is_admin=False,
            first_name="Jane",
            last_name="Smith",
            bio="Hi, I'm Jane.",
            # avatar="path/to/avatar3.png"
        )
    ]

    # Insert users into the database
    await User.insert_many(users)
    print("Database populated with test users.")
    # user = await User.find_one(User.username == 'admin1')
    # print(user)
