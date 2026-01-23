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
    
    # 1. Data Loading
    df_trans, df_products, df_b2b = logic.load_data()

    if df_trans is None:
        st.error("Error: Could not load data. Please run 'src/etl.py' first.")
        return

    # --- SIDEBAR FILTERS (INTERACTIVITY) ---
    st.sidebar.header("Dashboard Filters")
    st.sidebar.write("Customize your view here:")

    # Filter 1: Year Selection
    # I extract unique years from the data to populate the filter
    available_years = sorted(df_trans['date'].dt.year.unique())
    selected_year = st.sidebar.selectbox("Select Year", available_years, index=len(available_years)-1)

    # Filter 2: Category Selection
    # I get all unique categories from the products table
    available_cats = df_products['category'].unique().tolist()
    selected_cats = st.sidebar.multiselect("Select Categories", available_cats, default=available_cats)

    st.sidebar.markdown("---")
    st.sidebar.caption("Filters apply to KPIs and Charts only.")

    # --- FILTERING LOGIC ---
    # I filter the transactions based on the user's selection
    # 1. Filter by Year
    df_filtered = df_trans[df_trans['date'].dt.year == selected_year].copy()
    
    # 2. Filter by Product Category
    # First I need to know which products belong to the selected categories
    valid_products = df_products[df_products['category'].isin(selected_cats)]['product_id']
    df_filtered = df_filtered[df_filtered['product_id'].isin(valid_products)]

    # If the filter leaves no data, I show a warning
    if df_filtered.empty:
        st.warning("No data available for the current filters.")
        return

    st.markdown("---")

    # 2. Metric Calculation (KPIs)
    # I calculate KPIs based on the FILTERED data, not the full dataset
    kpis = logic.calculate_kpis(df_filtered, df_products)
    
    # Note: Churn analysis usually requires full history, so I pass the full dataframe for that one,
    # or I could decide to filter it too. For now, I keep Churn global.
    churn_data = logic.analyze_b2b_churn(df_trans, df_b2b)

    # 3. KPI Visualization (Top Row)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label=f"Revenue ({selected_year})", value=f"${kpis['total_sales']:,.2f}")
    
    with col2:
        st.metric(label="Net Margin (%)", value=f"{kpis['margin_percent']:.1f}%")
    
    with col3:
        st.metric(label="Avg. Ticket", value=f"${kpis['avg_ticket']:.2f}")

    with col4:
        # I display the count of at-risk clients
        risk_count = len(churn_data)
        st.metric(label="Global Clients at Risk", value=risk_count)

    st.markdown("---")

    # 4. Main Section (Charts and Tables)
    col_left, col_right = st.columns([2, 1]) 

    with col_left:
        st.subheader(f"Sales Trend ({selected_year})")
        st.write("Weekly revenue evolution for selected filters.")
        
        # I get the forecast/trend from logic.py using the FILTERED data
        forecast_df = logic.forecast_sales(df_filtered)
        
        # I plot the data
        st.line_chart(forecast_df.set_index('Date'))

    with col_right:
        st.subheader("At-Risk Contractors")
        st.write(f"Clients with >90 days inactivity (Global).")
        
        if not churn_data.empty:
            display_cols = ['name', 'days_inactive', 'email']
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
