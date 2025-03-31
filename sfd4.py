import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy_financial import pmt, irr, npv
import datetime

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

# Add a checkbox for 3-month payment deferral option
deferral_option = st.sidebar.checkbox("3-Month Payment Deferral", value=True)

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
    discounted_project_cost = (base_price + roof_cost) * (1 - project_discount_pct / 100)
    nys_incentive = system_size_kw * 1000 * 0.2

    # Use the discounted project cost for financing and cash purchase calculations
    loan_amount_customer = discounted_project_cost
    monthly_payment_selected = abs(pmt(loan_apr_cust / 100 / 12, loan_term_cust * 12, loan_amount_customer))

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
        'Year 3 Payment': round(lease_base * (1 + lease_rate) ** 2, 2)
    }
    output_summary = {
        'Prepared For': f"Investment Overview prepared for {customer_name}",
        'Selected Loan Program': f"{loan_term_cust} Years | APR: {loan_apr_cust:.2f}% | Dealer Fee: {dealer_fee_cust:.2f}%",
        'Monthly Payment': f"${monthly_payment_selected:,.2f}",
        'Cash Total': f"${cash['Total Cost']:.2f}",
        'Project Discount': f"{project_discount_pct}%"
    }

    # ---------------------------
    # Calculate Payment Schedules Based on Inputs
    # ---------------------------
    current_date_str = datetime.date.today().strftime("%b %d, %Y")
    system_cost = base_price  # System cost (before discount)
    spring_discount = roof_cost  # Using roof_cost as the "Spring Discount"
    itc_val = system_cost * 0.30  # 30% Federal Tax Credit (ITC)
    nys_credit_val = 5000         # Could be dynamic
    nyc_abatement_val = 34356     # Could be dynamic

    # Calculate loan amounts for each scenario:
    loan_amount_no_incentives = loan_amount_customer
    loan_amount_itc = loan_amount_customer - itc_val
    loan_amount_incentives = loan_amount_customer - (itc_val + nys_credit_val + nyc_abatement_val)

    # Loan parameters
    r = loan_apr_cust / 100 / 12  # Monthly interest rate
    n = loan_term_cust * 12       # Total number of months

    # Compute monthly payments using the pmt function
    monthly_payment_no_incentives = abs(pmt(r, n, loan_amount_no_incentives))
    monthly_payment_itc = abs(pmt(r, n, loan_amount_itc))
    monthly_payment_incentives = abs(pmt(r, n, loan_amount_incentives))

    # Apply 3-month deferral if selected (first 3 months are 0)
    no_incentives_1_3 = 0 if deferral_option else monthly_payment_no_incentives
    no_incentives_4_18 = monthly_payment_no_incentives
    no_incentives_y2 = monthly_payment_no_incentives
    no_incentives_y3 = monthly_payment_no_incentives
    no_incentives_y4 = monthly_payment_no_incentives
    no_incentives_y5plus = monthly_payment_no_incentives

    itc_1_3 = 0 if deferral_option else monthly_payment_itc
    itc_4_18 = monthly_payment_itc
    itc_y2 = monthly_payment_itc
    itc_y3 = monthly_payment_itc
    itc_y4 = monthly_payment_itc
    itc_y5plus = monthly_payment_itc

    itc_nys_nyc_1_3 = 0 if deferral_option else monthly_payment_incentives
    itc_nys_nyc_4_18 = monthly_payment_incentives
    itc_nys_nyc_y2 = monthly_payment_incentives
    itc_nys_nyc_y3 = monthly_payment_incentives
    itc_nys_nyc_y4 = monthly_payment_incentives
    itc_nys_nyc_y5plus = monthly_payment_incentives

    total_tax_incentives_val = itc_val + nys_credit_val + nyc_abatement_val
    net_investment_val = loan_amount_customer - total_tax_incentives_val

    annual_savings = electric_bill * 12  # Annual savings based on monthly electric bill

    # Calculate the Total 25-Year Net Savings dynamically.
    # Here we use: Total Savings = (Annual Savings * 25) - Adjusted System Cost.
    # For adjusted system cost, we use the full loan amount (discounted project cost) as a proxy.
    total_25yr_net_savings = annual_savings * 25 - loan_amount_customer

    loan_term_years = 25  # For header display
    loan_apr_val = loan_apr_cust  # Using customer-selected APR

    # ---------------------------
    # Render the PDF-like Lease/Loan Output Layout
    # ---------------------------
    st.markdown("<div style='color: red;'>Hello World</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; font-family: Arial, sans-serif; color: #333;">

      <!-- Header Section -->
      <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <!-- Left side: Company name & investment overview -->
        <div>
          <h2 style="margin: 0;">MpowerSOLAR</h2>
          <p style="margin: 0; font-size: 14px;">
            Investment Overview prepared for <strong>{customer_name}</strong> on {current_date_str}
          </p>
        </div>

        <!-- Right side: Loan info -->
        <div style="text-align: right;">
          <p style="margin: 0;">Loan Term {loan_term_years} Years</p>
          <p style="margin: 0;">AUTOPAY</p>
          <p style="margin: 0;">APR {loan_apr_val:.2f}%</p>
        </div>
      </div>

      <div style="display: flex; justify-content: space-between;">
        <!-- Left Column: Investment Details -->
        <div style="width: 48%;">
          <h3>Investment Details</h3>
          
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td colspan="2" style="padding: 4px 0;"><strong>BASIC LOAN INFORMATION</strong></td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">System Cost</td>
              <td style="padding: 4px 0; text-align: right;">${system_cost:,.0f}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">Spring Discount</td>
              <td style="padding: 4px 0; text-align: right;">${spring_discount:,.0f}</td>
            </tr>

            <tr>
              <td colspan="2" style="padding: 8px 0;"><strong>INCENTIVES</strong></td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">30% Federal Tax Credit (ITC)</td>
              <td style="padding: 4px 0; text-align: right;">${itc_val:,.0f}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">State Tax Credit (NYS)</td>
              <td style="padding: 4px 0; text-align: right;">${nys_credit_val:,.0f}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">Property Tax Abatement (NYC)</td>
              <td style="padding: 4px 0; text-align: right;">${nyc_abatement_val:,.0f}</td>
            </tr>

            <tr>
              <td colspan="2" style="padding: 8px 0;"><strong>TOTAL INVESTMENT</strong></td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">Total Loan Amount</td>
              <td style="padding: 4px 0; text-align: right;">${loan_amount_customer:,.0f}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">Total Tax Incentives</td>
              <td style="padding: 4px 0; text-align: right;">${total_tax_incentives_val:,.0f}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">Net Investment</td>
              <td style="padding: 4px 0; text-align: right;">${net_investment_val:,.0f}</td>
            </tr>
          </table>

          <br/>
          <h4 style="margin-bottom: 8px;">Added Benefits</h4>
          <ul style="margin-top: 0; font-size: 14px;">
            <li>No up-front fees</li>
            <li>No payment for first 3 months</li>
            <li>Referral Bonus: $1,000</li>
            <li>Roof repairs, minor electric work &amp; construction included</li>
          </ul>
        </div>

        <!-- Right Column: Savings Overview -->
        <div style="width: 48%;">
          <h3>Savings Overview</h3>
          
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td style="padding: 4px 0;">Utility w/o Mpower Solar</td>
              <td style="padding: 4px 0; text-align: right;">${electric_bill}/mo</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">Utility w/ Mpower Solar</td>
              <td style="padding: 4px 0; text-align: right;">$41 per meter</td>
            </tr>
            <tr>
              <td style="padding: 4px 0;">All Incentives Applied After 5 Years</td>
              <td style="padding: 4px 0; text-align: right;">$250/mo</td>
            </tr>
          </table>

          <br/>
          <p style="font-weight: bold; margin-bottom: 4px;">Est. Monthly Payment with Incentive Paydown</p>
          <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
            <thead>
              <tr style="background-color: #f0f0f0;">
                <th></th>
                <th>Months<br/>1-3</th>
                <th>Months<br/>4-18</th>
                <th>Year<br/>2</th>
                <th>Year<br/>3</th>
                <th>Year<br/>4</th>
                <th>Year<br/>5+</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>No Incentives</td>
                <td>${no_incentives_1_3:,.0f}</td>
                <td>${no_incentives_4_18:,.0f}</td>
                <td>${no_incentives_y2:,.0f}</td>
                <td>${no_incentives_y3:,.0f}</td>
                <td>${no_incentives_y4:,.0f}</td>
                <td>${no_incentives_y5plus:,.0f}</td>
              </tr>
              <tr>
                <td>ITC</td>
                <td>${itc_1_3:,.0f}</td>
                <td>${itc_4_18:,.0f}</td>
                <td>${itc_y2:,.0f}</td>
                <td>${itc_y3:,.0f}</td>
                <td>${itc_y4:,.0f}</td>
                <td>${itc_y5plus:,.0f}</td>
              </tr>
              <tr>
                <td>ITC + NYS + NYC</td>
                <td>${itc_nys_nyc_1_3:,.0f}</td>
                <td>${itc_nys_nyc_4_18:,.0f}</td>
                <td>${itc_nys_nyc_y2:,.0f}</td>
                <td>${itc_nys_nyc_y3:,.0f}</td>
                <td>${itc_nys_nyc_y4:,.0f}</td>
                <td>${itc_nys_nyc_y5plus:,.0f}</td>
              </tr>
            </tbody>
          </table>

          <br/>
          <h4 style="margin-bottom: 4px;">TOTAL 25-YEAR NET SAVINGS</h4>
          <h2 style="margin-top: 0;">${total_25yr_net_savings:,.0f}</h2>
          <p style="font-size: 12px;">
            This proposal expires 15 days from the date generated unless otherwise stipulated by Mpower Solar
          </p>
        </div>
      </div>

      <br/>
      <p style="font-size: 12px; line-height: 1.4;">
        1 Not everyone is qualified for credits, incentives, or rebates. Please consult your tax professional or legal professional for further information.
        <br/>
        2 The timing for receipt of the NYC Tax Credit may vary. While we assist with submissions, we cannot guarantee specific timelines; consult your tax advisor for details.
        <br/>
        3 The above payment is based on receipt of your timely Incentive Payments and successful enrollment in Autopay/ACH payments as stated in the loan agreement.
        <br/>
        4 A minimum of Two Thousand Five Hundred Dollars ($2,500) is required for loan re-amortization or principal pay-down after month 18.
        <br/>
        5 The projected total 25-year net savings assumes a 4% annual utility escalator.
      </p>

    </div>
    """, unsafe_allow_html=True)

    # Other outputs: Customer Inputs, Output Summary, Cash Purchase, Lease Option, etc.
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
    discounted_base_cost = base_cost * (1 - project_discount_pct / 100)
    gross_cost = base_cost / (1 - (dealer_fee_comp / 100))
    discounted_gross_cost = gross_cost * (1 - project_discount_pct / 100)
    
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
