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

# Debug: show shared input values (these should update when you change them)
st.sidebar.write("### Debug: Shared Inputs")
st.sidebar.write("Customer Name:", customer_name)
st.sidebar.write("System Size (kW):", system_size_kw)
st.sidebar.write("Cost per Watt ($):", cost_per_watt)
st.sidebar.write("Monthly Electric Bill ($):", electric_bill)
st.sidebar.write("Roof Cost ($):", roof_cost)
st.sidebar.write("Lease Rate:", lease_rate)
st.sidebar.write("Lease Base ($):", lease_base)
st.sidebar.write("Battery Add-on Cost ($):", battery_cost)
st.sidebar.write("State:", state)
st.sidebar.write("Lease Eligible:", lease_eligible)
st.sidebar.write("Incentives Applied:", incentives_toggle)
st.sidebar.write("Include Incentives:", include_incentives)

# ---------------------------
# Section 1: Solar Financial Scenarios
# ---------------------------
st.markdown("## Solar Financial Scenarios")

# Calculate common values (from the original dashboard logic)
base_price = system_size_kw * 1000 * cost_per_watt
nys_incentive = system_size_kw * 1000 * 0.2

# Fixed loan scenarios for display (hardcoded examples)
loan_scenarios = [
    {'Term': 25, 'APR': 0.0499, 'Monthly Factor': 0.00669},
    {'Term': 15, 'APR': 0.0399, 'Monthly Factor': 0.00769},
    {'Term': 10, 'APR': 0.0299, 'Monthly Factor': 0.00923}
]
for scenario in loan_scenarios:
    scenario['Loan Amount'] = base_price + roof_cost
    scenario['Monthly Payment'] = round(scenario['Loan Amount'] * scenario['Monthly Factor'], 2)

cash = {
    'Total Cost': base_price + roof_cost - nys_incentive,
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
    'Cash Total': f"${cash['Total Cost']:.2f}",
    'Lease Y1': f"${lease['Year 1 Payment']} /mo",
    'Lease Y2': f"${lease['Year 2 Payment']} /mo",
    'Lease Y3': f"${lease['Year 3 Payment']} /mo"
}
for loan in loan_scenarios:
    output_summary[f"Loan {loan['Term']}yr APR"] = f"{loan['APR']*100:.2f}%"
    output_summary[f"Loan {loan['Term']}yr Payment"] = f"${loan['Monthly Payment']} /mo"

st.subheader("Customer Inputs")
st.json({
    "Customer Name": customer_name,
    "System Size (kW)": system_size_kw,
    "Cost per Watt ($)": cost_per_watt,
    "Monthly Electric Bill ($)": electric_bill,
    "Roof Cost ($)": roof_cost,
    "Lease Rate": lease_rate,
    "Lease Base": lease_base
})

st.subheader("Loan Scenarios")
st.dataframe(pd.DataFrame(loan_scenarios))

st.subheader("Cash Purchase")
st.json(cash)

st.subheader("Lease Option")
st.json(lease)

st.subheader("Output Summary")
st.dataframe(pd.DataFrame([output_summary]).T, use_container_width=True)

st.subheader("Monthly Payment Comparison")
labels = [f"Loan {l['Term']}yr" for l in loan_scenarios] + ["Lease Y1", "Cash"]
values = [l['Monthly Payment'] for l in loan_scenarios] + [lease['Year 1 Payment'], 0]
fig1, ax1 = plt.subplots(figsize=(8, 4))
ax1.bar(labels, values)
ax1.set_ylabel("USD / month")
ax1.set_title("Monthly Payment Comparison")
st.pyplot(fig1)

# ---------------------------
# Section 2: Solar Finance Dashboard
# ---------------------------
st.markdown("---")
st.markdown("## Solar Finance Dashboard")

# Loan Program selection appears only in this section.
loan_profiles_list = [
    # 25-Year options
    (25, 4.49, 35.99),
    (25, 4.99, 33.49),
    (25, 5.99, 27.49),
    (25, 6.99, 23.49),
    (25, 7.99, 17.49),
    (25, 8.99, 13.49),
    (25, 9.99, 8.99),
    (25, 10.99, 5.99),
    (25, 11.99, 0.00),
    # 20-Year options
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
    # 15-Year options
    (15, 4.49, 32.99),
    (15, 4.99, 30.75),
    # 12-Year option
    (12, 4.49, 31.75),
    # 10-Year options
    (10, 4.49, 27.74),
    (10, 4.99, 26.24),
    (10, 5.99, 22.49),
    (10, 6.99, 18.74),
    (10, 7.99, 15.49),
    # 7-Year options
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
selected_loan_key = st.selectbox("Select Loan Program", list(loan_profiles.keys()))
loan_term_sfd, loan_apr_sfd, dealer_fee_sfd = loan_profiles[selected_loan_key]

# Perform Solar Finance calculations using the selected loan program.
# Note: The dealer fee is provided as a percentage so we convert it to a decimal.
base_cost = cost_per_watt * 1000 * system_size_kw - battery_cost
gross_cost = base_cost / (1 - (dealer_fee_sfd / 100))

if lease_eligible == "no":
    capped_size = min(system_size_kw, 8)
    federal_tax_credit = (((cost_per_watt * 1000 * capped_size) - 0) / (1 - (dealer_fee_sfd / 100))) * 0.3
else:
    federal_tax_credit = 0

battery_credit = ((gross_cost + battery_cost) * 0.3) * (0 if incentives_toggle == "yes" else 1)
ny_solar_credit = (min(5000, (gross_cost + battery_cost) * 0.25) if state == "NY" else 0) * (0 if incentives_toggle == "yes" else 1)

loan_rate_val = loan_apr_sfd / 100
loan_amount = gross_cost
loan_base_val = abs(pmt(loan_rate_val / 11.15, loan_term_sfd * 12, loan_amount))
loan_adj_val = abs(pmt(loan_rate_val / 11, loan_term_sfd * 12, loan_amount - (battery_credit + ny_solar_credit)))

base_bill = electric_bill * 1.15
lease_discount_7 = base_bill * (1 - 0.07)
lease_discount_15 = base_bill * (1 - 0.15)

years = loan_term_sfd
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

col1, col2, col3 = st.columns(3)
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
