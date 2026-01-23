import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import database  # I import my new database module

fake = Faker('en_US')
Faker.seed(42)
np.random.seed(42)

def generate_simulation(demand_factor=1.0, price_increase=0.0):
    """
    I generate the simulation accepting parameters:
    - demand_factor: Multiplier for transaction volume (1.0 = normal, 0.5 = crisis)
    - price_increase: Percentage added to base prices (0.10 = 10% inflation)
    """
    print(f"--- Starting Simulation (Demand: {demand_factor}x, Price Shock: +{price_increase:.0%}) ---")

    # 1. PRODUCTS
    print("1. Generating Product Catalog...")
    products_data = [
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
    
    df_products = pd.DataFrame(products_data, columns=['product_id', 'name', 'category', 'cost', 'price'])
    
    # I apply the price shock simulation
    df_products['price'] = df_products['price'] * (1 + price_increase)
    
    # I save to SQL instead of CSV
    database.save_to_sql(df_products, 'products')

    # 2. CUSTOMERS
    print("2. Generating B2B Customers...")
    b2b_clients = []
    for _ in range(50):
        b2b_clients.append({
            'client_id': fake.unique.random_number(digits=8),
            'name': fake.company(),
            'email': fake.company_email(),
            'signup_date': fake.date_between(start_date='-3y', end_date='-2y')
        })
    df_b2b = pd.DataFrame(b2b_clients)
    database.save_to_sql(df_b2b, 'customers')

    # 3. TRANSACTIONS
    print("3. Generating Transactions...")
    transactions = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    days_range = (end_date - start_date).days
    
    client_ids = df_b2b['client_id'].tolist()
    product_ids = df_products['product_id'].tolist()
    
    # I calculate total transactions based on the demand factor
    base_transactions = 5000
    total_transactions = int(base_transactions * demand_factor)

    for _ in range(total_transactions):
        date = start_date + timedelta(days=random.randint(0, days_range))
        is_b2b = random.random() < 0.3
        
        prod_id = random.choice(product_ids)
        qty = random.randint(1, 20)
        
        # I get the price (already inflated if applicable)
        unit_price = df_products.loc[df_products['product_id'] == prod_id, 'price'].values[0]
        total = round(qty * unit_price, 2)
        
        client = random.choice(client_ids) if is_b2b else None
        doc_type = 'Invoice' if is_b2b else 'Receipt'

        transactions.append({
            'date': date, # Use datetime object for SQL
            'type': doc_type,
            'client_id': client,
            'product_id': prod_id,
            'quantity': qty,
            'total_amount': total
        })

    df_trans = pd.DataFrame(transactions)
    df_trans = df_trans.sort_values('date')
    database.save_to_sql(df_trans, 'transactions')
    
    print("--- Simulation Completed and Saved to SQL ---")
    return len(df_trans)

if __name__ == "__main__":
    generate_simulation()