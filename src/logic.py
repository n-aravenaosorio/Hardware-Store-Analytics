import pandas as pd
import datetime


def load_data():
    """
    I created this function to load all CSV files at once.
    It returns a dictionary with the three dataframes
    """
    try:
        # I force pandas to parse dates specifically for the transactions file
        df_trans = pd.read_csv('data/transactions.csv', parse_dates=['date'])
        df_products = pd.read_csv('data/products.csv')
        df_b2b = pd.read_csv('data/b2b_customers.csv')
        
        print("Data loaded successfully.")
        return df_trans, df_products, df_b2b
    except FileNotFoundError:
        print("Error: CSV files not found. Please run etl.py first.")
        return None, None, None



def calculate_kpis(df_trans, df_products):
    """
    I merge transactions with products to calculate profit margins.
    """
    # I join the tables to get the cost of each sold item
    df_merged = df_trans.merge(df_products, on='product_id', how='left')
    
    # I calculate the total revenue (Price * Qty)
    total_sales = df_merged['total_amount'].sum()
    
    # I calculate the total cost (Cost * Qty) to determine the profit
    df_merged['total_cost'] = df_merged['cost'] * df_merged['quantity']
    total_cost = df_merged['total_cost'].sum()
    
    # I calculate the net margin
    total_margin = total_sales - total_cost
    margin_percent = (total_margin / total_sales) * 100 if total_sales > 0 else 0
    
    # I calculate the average ticket (Average sale per transaction)
    avg_ticket = df_trans['total_amount'].mean()

    return {
        "total_sales": total_sales,
        "total_margin": total_margin,
        "margin_percent": margin_percent,
        "avg_ticket": avg_ticket
    }


def analyze_b2b_churn(df_trans, df_b2b, days_threshold=90):
    """
    I identify B2B clients who haven't bought anything in the last 90 days.
    """
    # I filter only 'Invoice' transactions (B2B)
    b2b_trans = df_trans[df_trans['type'] == 'Invoice'].copy()
    
    # I find the last purchase date for each client
    last_purchase = b2b_trans.groupby('client_id')['date'].max().reset_index()
    last_purchase.columns = ['client_id', 'last_date']
    
    # I define "today" as the last date in the dataset (end of simulation)
    # In a real scenario, this would be datetime.today()
    simulation_end_date = df_trans['date'].max()
    
    # I merge with the client list to see who is missing
    churn_analysis = df_b2b.merge(last_purchase, on='client_id', how='left')
    
    # I calculate days since last purchase
    churn_analysis['days_inactive'] = (simulation_end_date - churn_analysis['last_date']).dt.days
    
    # I fill NaN values (clients who never bought) with a high number
    churn_analysis['days_inactive'] = churn_analysis['days_inactive'].fillna(999)
    
    # I flag clients as 'Risk' if they exceeded the threshold
    churn_list = churn_analysis[churn_analysis['days_inactive'] > days_threshold].sort_values('days_inactive', ascending=False)
    
    return churn_list

# ---------------------------------------------------------
# 3. FORECASTING (SIMPLE MOVING AVERAGE)
# ---------------------------------------------------------
def forecast_sales(df_trans, weeks=4):
    """
    I implement a simple Weekly Forecast using the average of the last 8 weeks.
    """
    # I resample data by Week (W) and sum the sales
    weekly_sales = df_trans.set_index('date').resample('W')['total_amount'].sum()
    
    # I take the last 8 weeks to calculate a moving average
    last_8_weeks_avg = weekly_sales.tail(8).mean()
    
    # I project this average for the next 'weeks' (default 4)
    forecast_dates = [weekly_sales.index[-1] + datetime.timedelta(weeks=i+1) for i in range(weeks)]
    forecast_values = [last_8_weeks_avg] * weeks
    
    df_forecast = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted_Sales': forecast_values
    })
    
    return df_forecast

# ---------------------------------------------------------
# MAIN TEST BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Testing Business Logic")
    
    # 1. Load
    t, p, b = load_data()
    
    if t is not None:
        # 2. Test KPIs
        kpis = calculate_kpis(t, p)
        print(f"Total Sales: ${kpis['total_sales']:,.2f}")
        print(f"Margin: {kpis['margin_percent']:.1f}%")
        
        # 3. Test Churn
        churn = analyze_b2b_churn(t, b)
        print(f"Clients at Risk: {len(churn)}")
        
        # 4. Test Forecast
        forecast = forecast_sales(t)
        print(f"Forecast for next week: ${forecast.iloc[0]['Predicted_Sales']:,.2f}")