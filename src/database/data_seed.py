import random
import os
from dotenv import load_dotenv
from faker import Faker
import faker_commerce
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.db_models import User, Product, Orders, OrderItems, orm_obj
from sqlalchemy import text

load_dotenv()

#Faker object to populate data
faker = Faker()
faker.add_provider(faker_commerce.Provider)

#Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def seed_data():
    print("Resetting database...")
    # Drop all tables and recreate them to start fresh
    orm_obj.metadata.drop_all(engine)
    #*******************************************# Used only if ghost table occurs
    # with engine.connect() as connection: 
    #     # We drop the old capitalized name AND the new lowercase name just in case
    #     connection.execute(text('DROP TABLE IF EXISTS "orderItems" CASCADE')) 
    #     connection.execute(text('DROP TABLE IF EXISTS order_items CASCADE'))
    #     connection.execute(text('DROP TABLE IF EXISTS orders CASCADE'))
    #     connection.execute(text('DROP TABLE IF EXISTS products CASCADE'))
    #     connection.execute(text('DROP TABLE IF EXISTS users CASCADE'))
    #     connection.commit()
    #*******************************************#
    orm_obj.metadata.create_all(engine)

    print("Seeding Users...")
    users = []
    # Create 20 users
    for _ in range(20):
        user = User(
            username=faker.user_name(),
            user_type=random.choice(["BUYER", "SELLER"])
        )
        users.append(user)
    
    session.add_all(users)
    session.commit()

    # Separate buyers and sellers for logic
    sellers = [u for u in users if u.user_type == "SELLER"]
    buyers = [u for u in users if u.user_type == "BUYER"]

    print("Seeding Products...")
    products = []
    categories = ["Electronics", "Groceries", "Healthcare", "Fashion", "Home"]
    
    # Create 50 products
    for _ in range(50):
        # We pick a random seller's ID
        seller = random.choice(sellers)
        
        product = Product(
            seller_id=seller.user_id,
            name=faker.ecommerce_name(),
            description=faker.paragraph(nb_sentences=2),
            price=round(random.uniform(10.0, 500.0), 2),
            stock_count=random.randint(0, 100),
            category=random.choice(categories)
        )
        products.append(product)
    
    session.add_all(products)
    session.commit()

    print("Seeding Orders & OrderItems...")
    # Create 30 Orders
    for _ in range(30):
        buyer = random.choice(buyers)
        
        # 1. Create the Order first (Status & Buyer)
        order = Orders(
            buyer_id=buyer.user_id,
            order_status=random.choice(['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED']),
            total_amount=0.0, # We will calculate this after adding items
            created_at=faker.date_time_this_year()
        )
        session.add(order)
        session.commit() # Commit to get the order_id

        # 2. Add Items to the Order
        current_order_total = 0.0
        # Randomly add 1 to 5 items per order
        for _ in range(random.randint(1, 5)):
            product = random.choice(products)
            qty = random.randint(1, 3)
            price = product.price # Snapshot of price at time of purchase
            
            order_item = OrderItems(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=qty,
                price_at_purchase=price
            )
            session.add(order_item)
            current_order_total += (price * qty)
        
        # 3. Update the Order's total amount
        order.total_amount = round(current_order_total, 2)
        session.commit()

    print("Database populated successfully!")

if __name__ == "__main__":
    seed_data()