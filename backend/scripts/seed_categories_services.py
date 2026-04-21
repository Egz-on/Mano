import asyncio
import uuid
import os
import sys
from datetime import datetime

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from sqlalchemy.future import select
from workmate.infrastructure.database.connection import Database
from workmate.infrastructure.database.models import CategoryModel, ServiceModel, UserProfileModel
from workmate.domain.models.user import UserRole
from workmate.infrastructure.config.settings import get_settings

async def seed_data():
    settings = get_settings()
    # Override settings for local connection if running from host
    print(f"Connecting to database at {settings.database.host}:{settings.database.port}...")
    
    db = Database()
    
    # Naive UTC time
    now = datetime.utcnow()

    async for session in db.get_session():
        
        # 1. Create Categories
        categories_data = [
            {"name": "Cleaning", "slug": "cleaning", "icon": "lucide:broom", "description": "Professional cleaning services"},
            {"name": "Electrical", "slug": "electrical", "icon": "lucide:zap", "description": "Expert electrical services"},
            {"name": "Plumbing", "slug": "plumbing", "icon": "lucide:droplets", "description": "Reliable plumbing solutions"}
        ]
        
        category_map = {}
        print("Seeding categories...")
        for cat in categories_data:
            res = await session.execute(select(CategoryModel).where(CategoryModel.slug == cat["slug"]))
            existing = res.scalar_one_or_none()
            
            if not existing:
                new_cat = CategoryModel(
                    id=str(uuid.uuid4()),
                    name=cat["name"],
                    slug=cat["slug"],
                    icon=cat["icon"],
                    description=cat["description"],
                    is_active=True,
                    display_order=0,
                    created_at=now,
                    updated_at=now
                )
                session.add(new_cat)
                category_map[cat["slug"]] = new_cat
                print(f"Created category: {cat['name']}")
            else:
                category_map[cat["slug"]] = existing
                print(f"Category {cat['name']} already exists.")
                
        # 2. Get dummy providers
        res = await session.execute(select(UserProfileModel).where(UserProfileModel.role == str(UserRole.provider)))
        providers = res.scalars().all()
        provider_map = {p.phone: p for p in providers}
        
        services_data = []
        if "+38970222333" in provider_map:
            services_data.append({
                "title": "Electrical Wiring Repair",
                "description": "Professional repairing and installation of electrical wirings.",
                "price": 1500.0,
                "currency": "MKD",
                "pricing_type": "hourly",
                "category_id": category_map["electrical"].id,
                "provider_id": provider_map["+38970222333"].id,
                "service_areas": ["Skopje", "Tetovo"],
                "images": ["https://images.unsplash.com/photo-1621905251189-08b45d6a269e?q=80&w=2069&auto=format&fit=crop"]
            })
            
        if "+38970333444" in provider_map:
            services_data.append({
                "title": "Full Home Deep Cleaning",
                "description": "Comprehensive cleaning of your entire house including windows.",
                "price": 3000.0,
                "currency": "MKD",
                "pricing_type": "fixed",
                "category_id": category_map["cleaning"].id,
                "provider_id": provider_map["+38970333444"].id,
                "service_areas": ["Bitola", "Ohrid"],
                "images": ["https://images.unsplash.com/photo-1581578731548-c64695cc6952?q=80&w=2070&auto=format&fit=crop"]
            })
            
        if "+38970444555" in provider_map:
            services_data.append({
                "title": "Emergency Plumbing & Pipe Repair",
                "description": "24/7 service for pipe leaks, unblocking drains, and more.",
                "price": 2000.0,
                "currency": "MKD",
                "pricing_type": "hourly",
                "category_id": category_map["plumbing"].id,
                "provider_id": provider_map["+38970444555"].id,
                "service_areas": ["Ohrid", "Skopje"],
                "images": ["https://images.unsplash.com/photo-1607472586893-edb57cbca132?q=80&w=2070&auto=format&fit=crop"]
            })
            
        print("Seeding services...")
        for s in services_data:
            res = await session.execute(
                select(ServiceModel).where(
                    (ServiceModel.title == s["title"]) & (ServiceModel.provider_id == s["provider_id"])
                )
            )
            existing = res.scalar_one_or_none()
            
            if not existing:
                new_service = ServiceModel(
                    id=str(uuid.uuid4()),
                    provider_id=str(s["provider_id"]),
                    category_id=str(s["category_id"]),
                    title=s["title"],
                    description=s["description"],
                    price=s["price"],
                    currency=s["currency"],
                    pricing_type=s["pricing_type"],
                    service_areas=s["service_areas"],
                    images=s["images"],
                    is_active=True,
                    is_featured=True,
                    rating=5.0,
                    review_count=1,
                    created_at=now,
                    updated_at=now
                )
                session.add(new_service)
                print(f"Created service: {s['title']}")
            else:
                print(f"Service {s['title']} already exists.")

        await session.commit()
        print("Database seeding completed successfully!")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
