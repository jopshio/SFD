
# Solar Finance Dashboard
# Exported full working Streamlit app

# Placeholder - actual dashboard code should be pasted here before use.
import streamlit as st
import numpy as np
import pandas as pd
from numpy_financial import pmt, irr, npv
import matplotlib.pyplot as plt

st.set_page_config(page_title="Solar Finance Dashboard", layout="wide")

loan_profiles_list = [
    (25, 4.49, 35.99), (25, 4.99, 33.49), (25, 5.99, 27.49), (25, 6.99, 23.49), (25, 7.99, 17.49),
    (25, 8.99, 13.49), (25, 9.99, 8.99), (25, 10.99, 5.99), (25, 11.99, 0.00),
    (20, 4.49, 34.49), (20, 4.99, 31.99), (20, 5.99, 25.99), (20, 6.99, 21.74), (20, 7.49, 20.24),
    (20, 7.99, 17.24), (20, 8.99, 13.24), (20, 9.99, 9.24), (20, 10.99, 5.99), (20, 11.99, 0.00),
    (15, 4.49, 32.99), (15, 4.99, 30.75), (12, 4.49, 31.75),
    (10, 4.49, 27.74), (10, 4.99, 26.24), (10, 5.99, 22.49), (10, 6.99, 18.74), (10, 7.99, 15.49),
    (7, 4.49, 23.99), (7, 4.99, 22.99), (7, 5.99, 19.99), (7, 6.99, 16.99), (7, 7.99, 14.24)
]
loan_profiles = {f"{t} Yr @ {a:.2f}% | Fee: {f:.2f}%": (t, a, f) for (t, a, f) in loan_profiles_list}

st.title("☀️ Solar Finance Dashboard")

system_size_kw = st.number_input("System Size (kW)", value=5.2)
cost_per_watt = st.number_input("Cost per Watt ($)", value=10.0)
battery_cost = st.number_input("Battery Add-on Cost ($)", value=0.0)
monthly_bill = st.number_input("Monthly Electric Bill ($)", value=500)
state = st.selectbox("State", ["NY", "NJ"])
lease_eligible = st.selectbox("Lease Eligible?", ["yes", "no"])
incentives_toggle = st.selectbox("Incentives Applied?", ["yes", "no"])
profile_key = st.selectbox("Loan Program", list(loan_profiles.keys()))
loan_term, loan_apr, dealer_fee_pct = loan_profiles[profile_key]
scope_of_work = st.text_area("Scope of Work", "Roof, Panel Upgrade")
include_incentives = st.checkbox("Include Incentives in Cash Flow", value=True)

base_cost = cost_per_watt * 1000 * system_size_kw - battery_cost
dealer_fee = dealer_fee_pct / 100
gross_cost = base_cost / (1 - dealer_fee)

if lease_eligible == "no":
    capped_size = min(system_size_kw, 8)
    federal_tax_credit = (((cost_per_watt * 1000 * capped_size) - 0) / (1 - dealer_fee)) * 0.3
else:
    federal_tax_credit = 0

battery_credit = ((gross_cost + battery_cost) * 0.3) * (0 if incentives_toggle == "yes" else 1)
ny_solar_credit = (min(5000, (gross_cost + battery_cost) * 0.25) if state == "NY" else 0) * (0 if incentives_toggle == "yes" else 1)

loan_rate = loan_apr / 100
loan_amount = gross_cost
loan_base = abs(pmt(loan_rate/11.15, loan_term*12, loan_amount))
loan_adj = abs(pmt(loan_rate/11, loan_term*12, loan_amount - (battery_credit + ny_solar_credit)))

base_bill = monthly_bill * 1.15
lease_discount_7 = base_bill * (1 - 0.07)
lease_discount_15 = base_bill * (1 - 0.15)

years = loan_term
annual_savings = monthly_bill * 12
monthly_savings = monthly_bill
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
    st.metric("Base Loan", f"${loan_base:,.0f}/mo")
    st.metric("Adjusted Loan", f"${loan_adj:,.0f}/mo")
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
fig, ax = plt.subplots()
ax.plot(range(0, years + 1), np.cumsum(cash_flows), marker="o", label="Annual")
ax.set_title("Cumulative Annual Cash Flow")
ax.set_xlabel("Year")
ax.set_ylabel("$ Cumulative Savings")
ax.grid(True)
st.pyplot(fig)

st.subheader("Monthly Cash Flow")
fig2, ax2 = plt.subplots()
ax2.plot(range(0, len(monthly_cash_flows)), np.cumsum(monthly_cash_flows), linewidth=1)
ax2.set_title("Cumulative Monthly Cash Flow")
ax2.set_xlabel("Month")
ax2.set_ylabel("$ Cumulative Savings")
ax2.grid(True)
st.pyplot(fig2)

st.subheader("Cash Flow Waterfall")
waterfall_df = pd.DataFrame({
    "Label": ["Upfront Cost"] + [f"Year {i+1}" for i in range(years)],
    "Value": [-adjusted_system_cost] + [annual_savings] * years
})
fig3, ax3 = plt.subplots()
cumulative = 0
for i, row in waterfall_df.iterrows():
    color = 'green' if row['Value'] > 0 else 'red'
    ax3.bar(i, row['Value'], bottom=cumulative if row['Value'] < 0 else 0, color=color)
    cumulative += row['Value']
ax3.set_title("Waterfall: Cash Flow Components")
ax3.set_xticks(range(len(waterfall_df)))
ax3.set_xticklabels(waterfall_df['Label'], rotation=45, ha='right')
ax3.axhline(0, color='black', linewidth=0.8)
st.pyplot(fig3)

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
