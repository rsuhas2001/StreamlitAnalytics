import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Retail Insights Dashboard", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Retail Sales Analytics")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload your dataset", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    filename = fl.name
    st.write("Uploaded File:", filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir("/Users/suhasr/Documents/Dashboard_Streamlit")  # Adjust to your path
    df = pd.read_csv("/Users/suhasr/Documents/Dashboard_Streamlit/Sample - Superstore.csv", encoding="ISO-8859-1")

col1, col2 = st.columns(2)
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Filter your data:")
region = st.sidebar.multiselect("Select Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Select State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Select City", df3["City"].unique())

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df3["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df3["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()

with col1:
    st.subheader("Category-wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=["${:,.2f}".format(x) for x in category_df["Sales"]], template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region-wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Time Series Sales Analysis")
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
time_series = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%b"))["Sales"].sum().reset_index()
fig2 = px.line(time_series, x="month_year", y="Sales", labels={"Sales": "Total Sales"}, height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Sales Breakdown by Segment")
fig3 = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Sales vs Profit Analysis")
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", color="Category")
data1.update_layout(title_text="Sales vs Profit Relationship", xaxis_title="Sales", yaxis_title="Profit")
st.plotly_chart(data1, use_container_width=True)

st.download_button("Download Processed Data", data=filtered_df.to_csv(index=False).encode('utf-8'), file_name="Filtered_Data.csv", mime="text/csv")
