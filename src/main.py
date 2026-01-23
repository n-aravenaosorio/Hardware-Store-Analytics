import streamlit as st
import etl  # I import the ETL script to run simulations
import database # I import database to read results

st.set_page_config(page_title="Hardware Store Simulator", layout="wide")

def main():
    st.title("⚙️ Hardware Store Simulation Lab")
    st.markdown("Use this panel to generate synthetic market scenarios for Power BI.")

    # --- SIDEBAR: SIMULATION PARAMETERS ---
    st.sidebar.header("Scenario Parameters")
    
    # Parameter 1: Economic Demand
    demand = st.sidebar.slider(
        "Market Demand Factor", 
        min_value=0.5, max_value=2.0, value=1.0, step=0.1,
        help="1.0 is Normal. 0.5 is Recession (Half sales). 2.0 is Boom."
    )
    
    # Parameter 2: Inflation
    # I changed the slider to use Integers (0 to 50) so the display looks correct (e.g. 10%)
    inflation_pct = st.sidebar.slider(
        "Price Inflation Shock", 
        min_value=0, max_value=50, value=0, step=5,
        format="%d%%",
        help="Increase base prices by this percentage."
    )
    
    # I convert the integer back to decimal for the calculation (e.g., 10 becomes 0.10)
    inflation_decimal = inflation_pct / 100.0

    # --- ACTION BUTTON ---
    if st.sidebar.button("RUN SIMULATION", type="primary"):
        with st.spinner("Simulating Market Scenarios... Writing to SQL Database..."):
            # I call the ETL function with the decimal value
            count = etl.generate_simulation(demand_factor=demand, price_increase=inflation_decimal)
            st.success(f"Simulation Complete! Generated {count} transactions in 'hardware_store.db'")

    st.markdown("---")

    # --- PREVIEW SECTION ---
    st.subheader("Database Preview (Live SQL View)")
    
    try:
        # I read directly from the SQL database created
        df_trans = database.load_from_sql('transactions')
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Transactions in DB: {len(df_trans)}")
            st.dataframe(df_trans.head(200), use_container_width=True)
            
        with col2:
            st.info("Financial Impact Preview")
            total_sales = df_trans['total_amount'].sum()
            st.metric("Total Revenue Generated", f"${total_sales:,.2f}")
            
    except Exception:
        st.warning("No database found. Please run a simulation first.")

if __name__ == "__main__":
    main()