import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy_financial import pmt, irr, npv

# ---------------------------
# Page & Title Configuration
# ---------------------------
st.set_page_config(page_title="Combined Solar Dashboard", layout="wide")
st.title("Combined Solar Dashboard")

# ---------------------------
# Sidebar: Shared Input Parameters
# ---------------------------
st.sidebar.header("Input Parameters")

customer_name = st.sidebar.text_input("Customer Name", value="John Doe")
system_size_kw = st.sidebar.number_input("System Size (kW)", value=7.5, step=0.1)
cost_per_watt = st.sidebar.number_input("Cost per Watt ($)", value=5.88, step=0.1)
electric_bill = st.sidebar.number_input("Monthly Electric Bill ($)", value=300, step=1)
roof_cost = st.sidebar.number_input("Roof Cost ($)", value=5000, step=100)
lease_rate = st.sidebar.number_input("Lease Rate (decimal)", value=0.028, step=0.001)
lease_base = st.sidebar.number_input("Lease Base ($)", value=110.0, step=1.0)
battery_cost = st.sidebar.number_input("Battery Add-on Cost ($)", value=0.0, step=1.0)
state = st.sidebar.selectbox("State", ["NY", "NJ"])
lease_eligible = st.sidebar.selectbox("Lease Eligible?", ["yes", "no"])
incentives_toggle = st.sidebar.selectbox("Incentives Applied?", ["yes", "no"])
scope_of_work = st.sidebar.text_area("Scope of Work", "Roof, Panel Upgrade")
include_incentives = st.sidebar.checkbox("Include Incentives in Cash Flow", value=True)

# Add a slider to discount the entire project cost
project_discount_pct = st.sidebar.slider("Project Discount (%)", min_value=0, max_value=100, value=0, step=1)

# ---------------------------
# Sidebar: Customer Loan Program Selection
# ---------------------------
st.sidebar.header("Customer Loan Program")
loan_profiles_list = [
    (25, 4.49, 35.99),
    (25, 4.99, 33.49),
    (25, 5.99, 27.49),
    (25, 6.99, 23.49),
    (25, 7.99, 17.49),
    (25, 8.99, 13.49),
    (25, 9.99, 8.99),
    (25, 10.99, 5.99),
    (25, 11.99, 0.00),
    (20, 4.49, 34.49),
    (20, 4.99, 31.99),
    (20, 5.99, 25.99),
    (20, 6.99, 21.74),
    (20, 7.49, 20.24),
    (20, 7.99, 17.24),
    (20, 8.99, 13.24),
    (20, 9.99, 9.24),
    (20, 10.99, 5.99),
    (20, 11.99, 0.00),
    (15, 4.49, 32.99),
    (15, 4.99, 30.75),
    (12, 4.49, 31.75),
    (10, 4.49, 27.74),
    (10, 4.99, 26.24),
    (10, 5.99, 22.49),
    (10, 6.99, 18.74),
    (10, 7.99, 15.49),
    (7, 4.49, 23.99),
    (7, 4.99, 22.99),
    (7, 5.99, 19.99),
    (7, 6.99, 16.99),
    (7, 7.99, 14.24),
]
loan_profiles = {
    f"{t} Years | APR: {a:.2f}% | Dealer Fee: {f:.2f}%": (t, a, f)
    for (t, a, f) in loan_profiles_list
}
selected_loan_key = st.sidebar.selectbox("Select Customer Loan Program", list(loan_profiles.keys()))
loan_term_cust, loan_apr_cust, dealer_fee_cust = loan_profiles[selected_loan_key]

# ---------------------------
# Create Tabs for Outputs
# ---------------------------
tab_customer, tab_company = st.tabs(["Customer Outputs", "Company Facing Data"])

# =============================================================================
# Tab 1: Customer Outputs
# =============================================================================
with tab_customer:
    st.markdown("### Customer Outputs")
    # Calculate base project cost and apply project discount
    base_price = system_size_kw * 1000 * cost_per_watt
    discounted_project_cost = (base_price + roof_cost) * (1 - project_discount_pct/100)
    nys_incentive = system_size_kw * 1000 * 0.2

    # Use the discounted project cost for financing and cash purchase calculations
    loan_amount_customer = discounted_project_cost
    monthly_payment_selected = abs(pmt(loan_apr_cust/100/12, loan_term_cust*12, loan_amount_customer))

    # Calculate cash purchase using the discounted project cost
    cash = {
        'Total Cost': discounted_project_cost - nys_incentive,
        'Monthly Savings': round(electric_bill, 2),
        'Payback Years': round((base_price - nys_incentive) / (electric_bill * 12), 1)
    }
    lease = {
        'Year 1 Payment': lease_base,
        'Escalation Rate': lease_rate,
        'Year 2 Payment': round(lease_base * (1 + lease_rate), 2),
        'Year 3 Payment': round(lease_base * (1 + lease_rate)**2, 2)
    }
    output_summary = {
        'Prepared For': f"Investment Overview prepared for {customer_name}",
        'Selected Loan Program': f"{loan_term_cust} Years | APR: {loan_apr_cust:.2f}% | Dealer Fee: {dealer_fee_cust:.2f}%",
        'Monthly Payment': f"${monthly_payment_selected:,.2f}",
        'Cash Total': f"${cash['Total Cost']:.2f}",
        'Project Discount': f"{project_discount_pct}%"
    }
    # New Loan Option section
    # Header similar to your PDF
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="margin: 0; font-family: Arial, sans-serif;">MpowerSOLAR</h1>
        <p style="margin: 0; font-size: 14px; font-family: Arial, sans-serif;">
            Investment Overview prepared for <strong>{customer_name}</strong> on Mar 31, 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Styled Loan Information similar to the PDF layout
    st.markdown(f"""
    <div style="border: 2px solid #000; padding: 20px; margin: 20px 0; font-family: Arial, sans-serif;">
    <h2 style="margin-bottom: 10px;">BASIC LOAN INFORMATION</h2>
    <table style="width: 100%; border-collapse: collapse; font-size: 16px;">
        <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Loan Amount</td>
        <td style="padding: 8px; border: 1px solid #ddd;">${loan_amount_customer:,.0f}</td>
        </tr>
        <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">APR</td>
        <td style="padding: 8px; border: 1px solid #ddd;">{loan_apr_cust:.2f}%</td>
        </tr>
        <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Loan Term</td>
        <td style="padding: 8px; border: 1px solid #ddd;">{loan_term_cust} Years</td>
        </tr>
        <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Monthly Payment</td>
        <td style="padding: 8px; border: 1px solid #ddd;">${monthly_payment_selected:,.2f}</td>
        </tr>
        <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Dealer Fee</td>
        <td style="padding: 8px; border: 1px solid #ddd;">{dealer_fee_cust:.2f}%</td>
        </tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

    
    
    
    
    
    
    #st.subheader("Loan Option")
    #loan_data = {
     #   "Loan Amount": loan_amount_customer,
      #  "Monthly Payment": monthly_payment_selected,
       # "Loan Term (years)": loan_term_cust,
        #"APR": loan_apr_cust,
       # "Dealer Fee": dealer_fee_cust,
    #}
    #st.json(loan_data)

    st.subheader("Customer Inputs")
    st.json({
        "Customer Name": customer_name,
        "System Size (kW)": system_size_kw,
        "Cost per Watt ($)": cost_per_watt,
        "Monthly Electric Bill ($)": electric_bill,
        "Roof Cost ($)": roof_cost,
        "Lease Rate": lease_rate,
        "Lease Base": lease_base,
        "Project Discount (%)": project_discount_pct
    })

    st.subheader("Output Summary")
    st.dataframe(pd.DataFrame([output_summary]).T, use_container_width=True)

    st.subheader("Cash Purchase")
    st.json(cash)

    st.subheader("Lease Option")
    st.json(lease)

    st.subheader("Monthly Payment Comparison")
    labels = ["Selected Loan Payment", "Lease Y1", "Cash"]
    values = [monthly_payment_selected, lease['Year 1 Payment'], 0]
    fig_cust, ax_cust = plt.subplots(figsize=(8, 4))
    ax_cust.bar(labels, values)
    ax_cust.set_ylabel("USD / month")
    ax_cust.set_title("Monthly Payment Comparison")
    st.pyplot(fig_cust)

    st.markdown("### Export Data")
    csv_output_summary = pd.DataFrame([output_summary]).T.to_csv(index=True)
    st.download_button("📥 Download Output Summary CSV", data=csv_output_summary, file_name="output_summary.csv")
    csv_cash = pd.DataFrame([cash]).to_csv(index=False)
    st.download_button("📥 Download Cash Purchase CSV", data=csv_cash, file_name="cash_purchase.csv")
    csv_lease = pd.DataFrame([lease]).to_csv(index=False)
    st.download_button("📥 Download Lease Option CSV", data=csv_lease, file_name="lease_option.csv")

# =============================================================================
# Tab 2: Company Facing Data
# =============================================================================
with tab_company:
    st.markdown("### Company Facing Data")
    # Company-facing loan program selection (independent from customer selection)
    loan_profiles_list_comp = [
        (25, 4.49, 35.99),
        (25, 4.99, 33.49),
        (25, 5.99, 27.49),
        (25, 6.99, 23.49),
        (25, 7.99, 17.49),
        (25, 8.99, 13.49),
        (25, 9.99, 8.99),
        (25, 10.99, 5.99),
        (25, 11.99, 0.00),
        (20, 4.49, 34.49),
        (20, 4.99, 31.99),
        (20, 5.99, 25.99),
        (20, 6.99, 21.74),
        (20, 7.49, 20.24),
        (20, 7.99, 17.24),
        (20, 8.99, 13.24),
        (20, 9.99, 9.24),
        (20, 10.99, 5.99),
        (20, 11.99, 0.00),
        (15, 4.49, 32.99),
        (15, 4.99, 30.75),
        (12, 4.49, 31.75),
        (10, 4.49, 27.74),
        (10, 4.99, 26.24),
        (10, 5.99, 22.49),
        (10, 6.99, 18.74),
        (10, 7.99, 15.49),
        (7, 4.49, 23.99),
        (7, 4.99, 22.99),
        (7, 5.99, 19.99),
        (7, 6.99, 16.99),
        (7, 7.99, 14.24),
    ]
    loan_profiles_comp = {
        f"{t} Years | APR: {a:.2f}% | Dealer Fee: {f:.2f}%": (t, a, f)
        for (t, a, f) in loan_profiles_list_comp
    }
    selected_loan_key_comp = st.selectbox("Select Company Loan Program", list(loan_profiles_comp.keys()))
    loan_term_comp, loan_apr_comp, dealer_fee_comp = loan_profiles_comp[selected_loan_key_comp]
    
    # Calculate base cost (without discount) then apply discount to both base and gross costs
    base_cost = cost_per_watt * 1000 * system_size_kw - battery_cost
    discounted_base_cost = base_cost * (1 - project_discount_pct/100)
    gross_cost = base_cost / (1 - (dealer_fee_comp / 100))
    discounted_gross_cost = gross_cost * (1 - project_discount_pct/100)
    
    # Company revenue defined as margin on the project
    company_revenue = discounted_gross_cost - discounted_base_cost

    if lease_eligible == "no":
        capped_size = min(system_size_kw, 8)
        federal_tax_credit = (((cost_per_watt * 1000 * capped_size) - 0) / (1 - (dealer_fee_comp / 100))) * 0.3
    else:
        federal_tax_credit = 0

    battery_credit = ((gross_cost + battery_cost) * 0.3) * (1 if incentives_toggle == "yes" else 0)
    ny_solar_credit = (min(5000, (gross_cost + battery_cost) * 0.25) if state == "NY" else 0) * (1 if incentives_toggle == "yes" else 0)
    
    loan_rate_val = loan_apr_comp / 100
    loan_amount = gross_cost
    loan_base_val = abs(pmt(loan_rate_val / 11.15, loan_term_comp * 12, loan_amount))
    loan_adj_val = abs(pmt(loan_rate_val / 11, loan_term_comp * 12, loan_amount - (battery_credit + ny_solar_credit)))
    
    base_bill = electric_bill * 1.15
    lease_discount_7 = base_bill * (1 - 0.07)
    lease_discount_15 = base_bill * (1 - 0.15)
    
    years = loan_term_comp
    annual_savings = electric_bill * 12
    monthly_savings = electric_bill
    adjusted_system_cost = gross_cost - (federal_tax_credit + battery_credit + ny_solar_credit if include_incentives else 0)
    cash_flows = [-adjusted_system_cost] + [annual_savings] * years
    monthly_cash_flows = [-adjusted_system_cost] + [monthly_savings] * (years * 12)
    npv_value = npv(0.05, cash_flows)
    roi = (sum(cash_flows[1:]) - adjusted_system_cost) / adjusted_system_cost
    irr_val = irr(cash_flows)
    
    def get_payback(cf):
        cum = np.cumsum(cf)
        for i, v in enumerate(cum):
            if v >= 0:
                return i
        return f">{years}"
    payback_year = get_payback(cash_flows)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gross System Cost", f"${gross_cost:,.0f}")
        st.metric("Battery Add-on", f"${battery_cost:,.0f}")
        st.metric("State", state)
    with col2:
        st.metric("Base Loan", f"${loan_base_val:,.0f}/mo")
        st.metric("Adjusted Loan", f"${loan_adj_val:,.0f}/mo")
        st.metric("Incentive Applied", f"${battery_credit + ny_solar_credit:,.0f}")
    with col3:
        st.metric("Base Monthly Bill", f"${base_bill:,.0f}")
        st.metric("7% Discounted", f"${lease_discount_7:,.0f}")
        st.metric("15% Discounted", f"${lease_discount_15:,.0f}")
    with col4:
        st.metric("Revenue", f"${company_revenue:,.0f}")
    
    st.markdown(f"**Scope of Work:** {scope_of_work}")
    st.metric("ROI", f"{roi:.2%}")
    st.metric("NPV (5% rate)", f"${npv_value:,.0f}")
    st.metric("IRR", f"{irr_val:.2%}")
    st.metric("Payback Period", f"{payback_year} years")
    
    st.subheader("Cash Flow Over Time")
    fig2, ax2 = plt.subplots()
    ax2.plot(range(0, years + 1), np.cumsum(cash_flows), marker="o")
    ax2.set_title("Cumulative Annual Cash Flow")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("$ Cumulative Savings")
    ax2.grid(True)
    st.pyplot(fig2)
    
    st.subheader("Monthly Cash Flow")
    fig3, ax3 = plt.subplots()
    ax3.plot(range(0, len(monthly_cash_flows)), np.cumsum(monthly_cash_flows), linewidth=1)
    ax3.set_title("Cumulative Monthly Cash Flow")
    ax3.set_xlabel("Month")
    ax3.set_ylabel("$ Cumulative Savings")
    ax3.grid(True)
    st.pyplot(fig3)
    
    st.subheader("Cash Flow Waterfall")
    waterfall_df = pd.DataFrame({
        "Label": ["Upfront Cost"] + [f"Year {i+1}" for i in range(years)],
        "Value": [-adjusted_system_cost] + [annual_savings] * years
    })
    fig4, ax4 = plt.subplots()
    cumulative = 0
    for i, row in waterfall_df.iterrows():
        color = 'green' if row['Value'] > 0 else 'red'
        ax4.bar(i, row['Value'], bottom=cumulative if row['Value'] < 0 else 0, color=color)
        cumulative += row['Value']
    ax4.set_title("Waterfall: Cash Flow Components")
    ax4.set_xticks(range(len(waterfall_df)))
    ax4.set_xticklabels(waterfall_df['Label'], rotation=45, ha='right')
    ax4.axhline(0, color='black', linewidth=0.8)
    st.pyplot(fig4)
    
    st.subheader("Monthly Cash Flow Table")
    monthly_df = pd.DataFrame({
        "Month": list(range(len(monthly_cash_flows))),
        "Monthly Cash Flow": monthly_cash_flows,
        "Cumulative": np.cumsum(monthly_cash_flows)
    })
    st.dataframe(monthly_df, use_container_width=True)
    st.download_button("📥 Download Monthly CSV", data=monthly_df.to_csv(index=False), file_name="monthly_cash_flow.csv")
    
    annual_df = pd.DataFrame({
        "Year": list(range(years + 1)),
        "Annual Cash Flow": cash_flows,
        "Cumulative": np.cumsum(cash_flows)
    })
    st.subheader("Annual Cash Flow Table")
    st.dataframe(annual_df, use_container_width=True)
    st.download_button("📥 Download Annual CSV", data=annual_df.to_csv(index=False), file_name="annual_cash_flow.csv")
