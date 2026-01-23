import streamlit as st
import pandas as pd
import logic  # I import my internal logic module

# I configure the page settings with a professional title and wide layout
st.set_page_config(
    page_title="Hardware Analytics Suite",
    layout="wide"
)

def main():
    # --- Project Header ---
    st.title("Hardware Store Analytics Suite")
    st.markdown("**Business Intelligence Solution** | Developed by Nicolás Aravena")
    st.markdown("---")

    # 1. Data Loading
    # I call the function I created in logic.py to fetch the dataframes
    df_trans, df_products, df_b2b = logic.load_data()

    if df_trans is None:
        st.error("Error: Could not load data. Please run 'src/etl.py' first.")
        return

    # 2. Metric Calculation (KPIs)
    # I calculate the financial KPIs and the Churn list using my logic module
    kpis = logic.calculate_kpis(df_trans, df_products)
    churn_data = logic.analyze_b2b_churn(df_trans, df_b2b)

    # 3. KPI Visualization (Top Row)
    # I use 4 columns to display the metrics like a control panel
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Revenue (USD)", value=f"${kpis['total_sales']:,.2f}")
    
    with col2:
        st.metric(label="Net Margin (%)", value=f"{kpis['margin_percent']:.1f}%")
    
    with col3:
        st.metric(label="Avg. Ticket", value=f"${kpis['avg_ticket']:.2f}")

    with col4:
        # I display the count of at-risk clients
        risk_count = len(churn_data)
        st.metric(label="B2B Clients at Risk (Churn)", value=risk_count)

    st.markdown("---")

    # 4. Main Section (Charts and Tables)
    # I define an asymmetric layout (2:1 ratio) for the main content
    col_left, col_right = st.columns([2, 1]) 

    with col_left:
        st.subheader("Sales Forecast (Next 4 Weeks)")
        st.write("Projected revenue based on 8-week moving average.")
        
        # I get the forecast dataframe from logic.py
        forecast_df = logic.forecast_sales(df_trans)
        
        # I plot the data using the native Streamlit line chart
        st.line_chart(forecast_df.set_index('Date'))

    with col_right:
        st.subheader("At-Risk Contractors")
        st.write(f"Clients with >90 days inactivity.")
        
        if not churn_data.empty:
            # I select only the relevant columns for the report
            display_cols = ['name', 'days_inactive', 'email']
            
            # I display the dataframe without the index for a cleaner look
            st.dataframe(
                churn_data[display_cols].sort_values('days_inactive', ascending=False),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.success("No clients at risk currently.")

    # 5. Footer
    st.markdown("---")
    st.caption("System Status: Operational | Data Source: Local CSV Simulation")

if __name__ == "__main__":
    main()