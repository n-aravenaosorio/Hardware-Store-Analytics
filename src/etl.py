import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# I initialize Faker and set seeds for reproducibility
fake = Faker('en_US')
Faker.seed(42)
np.random.seed(42)

def generate_simulation():
    print("Starting Hardware Store Simulation...")
    
    # I make sure the data folder exists to avoid errors
    os.makedirs("data", exist_ok=True)

    
    # 1. GENERATING PRODUCT CATALOG
    print("1. Generating Product Catalog...")
    
    # I defined the product list
    # Categories: Structural, Tools, Finishing
    products_data = [
        # ID, Name, Category, Cost ($), Price ($)
        (101, 'Portland Cement 50lb', 'Structural', 5.00, 8.50),
        (102, 'Red Clay Brick', 'Structural', 0.50, 0.85),
        (103, 'Rebar 1/2 inch', 'Structural', 6.00, 9.50),
        (104, 'Construction Sand 1 ton', 'Structural', 25.00, 40.00),
        (105, 'Hammer Drill 700W', 'Tools', 45.00, 79.99),
        (106, 'Angle Grinder 4.5"', 'Tools', 30.00, 55.00),
        (107, 'Screwdriver Set Pro', 'Tools', 15.00, 24.99),
        (108, 'Claw Hammer', 'Tools', 8.00, 14.50),
        (109, 'White Enamel Paint 1gal', 'Finishing', 20.00, 35.00),
        (110, 'Grey Floor Tiles Box', 'Finishing', 12.00, 19.99),
        (111, 'Waterproof Grout', 'Finishing', 4.00, 7.50),
        (112, 'Paint Brush 2 inch', 'Finishing', 2.00, 4.50)
    ]
    
    # I create the DataFrame and save it as a CSV file
    df_products = pd.DataFrame(products_data, columns=['product_id', 'name', 'category', 'cost', 'price'])
    df_products.to_csv('data/products.csv', index=False)
    print(f"   -> Saved data/products.csv ({len(df_products)} products)")

    
    # 2. GENERATING B2B CUSTOMERS (Contractors)
    print("2. Generating B2B Customers...")
    b2b_clients = []
    
    # I generate 50 fake companies using Faker to simulate contractors
    for _ in range(50):
        b2b_clients.append({
            'client_id': fake.unique.random_number(digits=8),
            'name': fake.company(),
            'tax_id': fake.ssn(),  # I used SSN/ID as a generic Tax ID for the simulation
            'email': fake.company_email(),
            'phone': fake.phone_number(),
            'signup_date': fake.date_between(start_date='-3y', end_date='-2y')
        })
    
    df_b2b = pd.DataFrame(b2b_clients)
    df_b2b.to_csv('data/b2b_customers.csv', index=False)
    print(f"   -> Saved data/b2b_customers.csv ({len(df_b2b)} customers)")


    # 3. GENERATING TRANSACTIONS (2 Years)
    print("3. Generating 5000 Transactions...")
    
    transactions = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    days_range = (end_date - start_date).days

    # I convert IDs to lists to ensure I pick existing IDs later
    client_ids = df_b2b['client_id'].tolist()
    product_ids = df_products['product_id'].tolist()

    for _ in range(5000):
        # I pick a random date within the 2-year range
        date = start_date + timedelta(days=random.randint(0, days_range))
        
        # I define the mix: 30% B2B (Invoice), 70% B2C (Receipt)
        is_b2b = random.random() < 0.3
        
        if is_b2b:
            doc_type = 'Invoice'
            client = random.choice(client_ids)
        else:
            doc_type = 'Receipt'
            client = None # Anonymous customer
            
        # I select a random product and a random quantity
        prod_id = random.choice(product_ids)
        qty = random.randint(1, 20)
        
        # I fetch the real unit price to calculate the total amount correctly
        unit_price = df_products.loc[df_products['product_id'] == prod_id, 'price'].values[0]
        total = round(qty * unit_price, 2) # Rounded to 2 decimals for USD

        transactions.append({
            'date': date.strftime('%Y-%m-%d'),
            'type': doc_type,
            'client_id': client,
            'product_id': prod_id,
            'quantity': qty,
            'total_amount': total
        })

    # I sort the transactions by date and save the final CSV
    df_trans = pd.DataFrame(transactions)
    df_trans = df_trans.sort_values('date') 
    df_trans.to_csv('data/transactions.csv', index=False)
    print(f"   -> Saved data/transactions.csv ({len(df_trans)} transactions)")
    print("--- Simulation Completed ---")

if __name__ == "__main__":
    generate_simulation()