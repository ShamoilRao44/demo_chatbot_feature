"""Script to seed the database with test data"""
from app.db import SessionLocal, init_db
from app.models import Restaurant, MenuGroup, MenuItem


def seed_database():
    """Seed database with test data"""
    
    # Initialize database
    init_db()
    print("Database initialized")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if restaurant already exists
        existing = db.query(Restaurant).filter(Restaurant.id == 1).first()
        if existing:
            print("Test data already exists. Skipping...")
            return
        
        # Create restaurant
        restaurant = Restaurant(
            id=1,
            owner_id=1,
            name="Demo Restaurant",
            address="123 Main St, Anytown, State 12345",
            business_hours={
                "monday": "09:00-21:00",
                "tuesday": "09:00-21:00",
                "wednesday": "09:00-21:00",
                "thursday": "09:00-21:00",
                "friday": "09:00-22:00",
                "saturday": "10:00-22:00",
                "sunday": "10:00-20:00"
            },
            prep_time_minutes=30,
            is_paused=False
        )
        db.add(restaurant)
        db.commit()
        print(f"✓ Created restaurant: {restaurant.name}")
        
        # Create menu groups
        appetizers = MenuGroup(restaurant_id=1, name="Appetizers")
        mains = MenuGroup(restaurant_id=1, name="Main Courses")
        desserts = MenuGroup(restaurant_id=1, name="Desserts")
        beverages = MenuGroup(restaurant_id=1, name="Beverages")
        
        db.add_all([appetizers, mains, desserts, beverages])
        db.commit()
        db.refresh(appetizers)
        db.refresh(mains)
        db.refresh(desserts)
        db.refresh(beverages)
        print(f"✓ Created menu groups: Appetizers, Main Courses, Desserts, Beverages")
        
        # Create menu items - Appetizers
        items = [
            MenuItem(
                restaurant_id=1,
                group_id=appetizers.id,
                name="Spring Rolls",
                description="Fresh vegetables wrapped in rice paper with peanut sauce",
                price=850,  # $8.50
                tags=["vegetarian", "vegan"]
            ),
            MenuItem(
                restaurant_id=1,
                group_id=appetizers.id,
                name="Buffalo Wings",
                description="Crispy chicken wings tossed in spicy buffalo sauce",
                price=1299,  # $12.99
                tags=["spicy"]
            ),
            MenuItem(
                restaurant_id=1,
                group_id=appetizers.id,
                name="Caesar Salad",
                description="Romaine lettuce with parmesan, croutons, and caesar dressing",
                price=950,  # $9.50
                tags=["vegetarian"]
            ),
            
            # Main Courses
            MenuItem(
                restaurant_id=1,
                group_id=mains.id,
                name="Grilled Salmon",
                description="Fresh Atlantic salmon with lemon butter sauce and vegetables",
                price=2499,  # $24.99
                tags=["gluten-free"]
            ),
            MenuItem(
                restaurant_id=1,
                group_id=mains.id,
                name="Beef Burger",
                description="Angus beef patty with lettuce, tomato, and special sauce",
                price=1599,  # $15.99
                tags=[]
            ),
            MenuItem(
                restaurant_id=1,
                group_id=mains.id,
                name="Vegetable Stir Fry",
                description="Seasonal vegetables in savory sauce over jasmine rice",
                price=1399,  # $13.99
                tags=["vegetarian", "vegan"]
            ),
            
            # Desserts
            MenuItem(
                restaurant_id=1,
                group_id=desserts.id,
                name="Chocolate Lava Cake",
                description="Warm chocolate cake with molten center and vanilla ice cream",
                price=899,  # $8.99
                tags=["vegetarian"]
            ),
            MenuItem(
                restaurant_id=1,
                group_id=desserts.id,
                name="New York Cheesecake",
                description="Classic creamy cheesecake with berry compote",
                price=799,  # $7.99
                tags=["vegetarian"]
            ),
            
            # Beverages
            MenuItem(
                restaurant_id=1,
                group_id=beverages.id,
                name="Fresh Lemonade",
                description="House-made lemonade with fresh lemon juice",
                price=399,  # $3.99
                tags=["vegan"]
            ),
            MenuItem(
                restaurant_id=1,
                group_id=beverages.id,
                name="Iced Coffee",
                description="Cold brew coffee served over ice",
                price=449,  # $4.49
                tags=["vegan"]
            ),
        ]
        
        db.add_all(items)
        db.commit()
        print(f"✓ Created {len(items)} menu items")
        
        print("\n" + "="*60)
        print("Test data seeded successfully!")
        print("="*60)
        print("\nRestaurant Details:")
        print(f"  ID: 1")
        print(f"  Owner ID: 1")
        print(f"  Name: {restaurant.name}")
        print(f"  Address: {restaurant.address}")
        print(f"  Prep Time: {restaurant.prep_time_minutes} minutes")
        print(f"  Status: {'Paused' if restaurant.is_paused else 'Active'}")
        print(f"\nMenu Groups: {len([appetizers, mains, desserts, beverages])}")
        print(f"Menu Items: {len(items)}")
        print("\nYou can now start the server and test the chatbot!")
        print("Example: python -m app.main")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
