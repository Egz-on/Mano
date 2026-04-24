import asyncio
import uuid
import os
import sys
from datetime import datetime

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from sqlalchemy.future import select
from mano.infrastructure.database.connection import Database
from mano.infrastructure.database.models import UserProfileModel
from mano.domain.models.user import UserRole
from mano.infrastructure.config.settings import get_settings

# Admin auth ID fetched from database
ADMIN_AUTH_ID = "54fdddee-907a-42f6-a274-cb171a8f14c9"


async def seed_data():
    settings = get_settings()
    # Override settings for local connection if running from host
    print(f"Connecting to database at {settings.database.host}:{settings.database.port}...")

    db = Database()

    # Naive UTC time
    now = datetime.utcnow()

    async for session in db.get_session():
        print("Checking for existing admin user...")

        # 1. Seed/Update Admin
        result = await session.execute(select(UserProfileModel).where(UserProfileModel.auth_user_id == ADMIN_AUTH_ID))
        admin_user = result.scalar_one_or_none()

        if admin_user:
            print(f"Admin user found (ID: {admin_user.id}). Updating role to ADMIN.")
            admin_user.role = str(UserRole.admin)
            admin_user.name = "System"
            admin_user.surname = "Admin"
            admin_user.phone = "+393470111222"
        else:
            print("Admin user not found. Creating...")
            admin_user = UserProfileModel(
                id=str(uuid.uuid4()),
                auth_user_id=ADMIN_AUTH_ID,
                name="System",
                surname="Admin",
                phone="+393470111222",
                role=str(UserRole.admin),
                city="Skopje",
                created_at=now,
                updated_at=now,
                last_login=now,
            )
            session.add(admin_user)

        # 2. Seed Dummy Providers
        providers = [
            {
                "name": "Arben",
                "surname": "Hoxha",
                "phone": "+393470222333",
                "city": "Skopje",
                "company_name": "Hoxha Electric",
                "years_of_experience": 15,
                "bio": "Experienced electrician with over 15 years in residential and commercial installations.",
                "role": str(UserRole.provider),
            },
            {
                "name": "Elena",
                "surname": "Petrovska",
                "phone": "+393470333444",
                "city": "Bitola",
                "company_name": "Elena Clean",
                "years_of_experience": 5,
                "bio": "Professional cleaning services for your home and office.",
                "role": str(UserRole.provider),
            },
            {
                "name": "Marko",
                "surname": "Stojanovic",
                "phone": "+393470444555",
                "city": "Ohrid",
                "company_name": "Marko Plumber",
                "years_of_experience": 8,
                "bio": "Expert plumbing solutions. 24/7 emergency service.",
                "role": str(UserRole.provider),
            },
        ]

        print("Seeding dummy providers...")
        for p in providers:
            # Check if exists by phone (simple dedup)
            res = await session.execute(select(UserProfileModel).where(UserProfileModel.phone == p["phone"]))
            existing = res.scalar_one_or_none()

            if not existing:
                new_provider = UserProfileModel(
                    id=str(uuid.uuid4()),
                    auth_user_id=str(uuid.uuid4()),
                    name=p["name"],
                    surname=p["surname"],
                    phone=p["phone"],
                    city=p["city"],
                    company_name=p["company_name"],
                    years_of_experience=p["years_of_experience"],
                    bio=p["bio"],
                    role=p["role"],
                    avatar_url=(f"https://ui-avatars.com/api/?name={p['name']}+{p['surname']}&background=random"),
                    created_at=now,
                    updated_at=now,
                    last_login=now,
                )
                session.add(new_provider)
                print(f"Created provider: {p['name']} {p['surname']}")
            else:
                print(f"Provider {p['name']} {p['surname']} already exists.")

        # 3. Seed Dummy Clients
        clients = [
            {
                "name": "Jeton",
                "surname": "Mazllami",
                "phone": "+393470555666",
                "city": "Tetovo",
                "role": str(UserRole.client),
            },
            {
                "name": "Ana",
                "surname": "Nikolovska",
                "phone": "+393470666777",
                "city": "Skopje",
                "role": str(UserRole.client),
            },
        ]

        print("Seeding dummy clients...")
        for c in clients:
            res = await session.execute(select(UserProfileModel).where(UserProfileModel.phone == c["phone"]))
            existing = res.scalar_one_or_none()

            if not existing:
                new_client = UserProfileModel(
                    id=str(uuid.uuid4()),
                    auth_user_id=str(uuid.uuid4()),
                    name=c["name"],
                    surname=c["surname"],
                    phone=c["phone"],
                    city=c["city"],
                    role=c["role"],
                    avatar_url=f"https://ui-avatars.com/api/?name={c['name']}+{c['surname']}&background=random",
                    created_at=now,
                    updated_at=now,
                    last_login=now,
                )
                session.add(new_client)
                print(f"Created client: {c['name']} {c['surname']}")
            else:
                print(f"Client {c['name']} {c['surname']} already exists.")

        await session.commit()
        print("Database seeding completed successfully!")

    await db.close()


if __name__ == "__main__":
    asyncio.run(seed_data())
