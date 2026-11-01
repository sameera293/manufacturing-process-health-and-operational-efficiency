import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Smart Factory Process Health", page_icon="🏭", layout="wide")
st.title("Manufacturing Process Health")
st.caption("Diagnostic view • Use verified operating limits before interpreting a machine as unhealthy.")

@st.cache_data
def read_data(file_path):
    d=pd.read_csv(file_path)
    d["DateTime"]=pd.to_datetime(d["Date"].astype(str)+" "+d["Timestamp"].astype(str), dayfirst=True, errors="coerce")
    d["Machine_ID"]=d["Machine_ID"].astype(str)
    return d.dropna(subset=["DateTime"])

DATA_PATH = Path(__file__).parent / "Thales_Group_Manufacturing.csv"
if not DATA_PATH.exists():
    st.error(f"Bundled dataset not found: {DATA_PATH.name}. Keep the CSV in the same folder as app.py.")
    st.stop()
df=read_data(str(DATA_PATH))
required={"Machine_ID","Operation_Mode","Efficiency_Status","DateTime"}
if not required.issubset(df.columns): st.error("Required columns are missing."); st.stop()
st.sidebar.header("Filters")
machines=sorted(df.Machine_ID.unique())
selected=st.sidebar.multiselect("Machines",machines,default=machines)
modes=sorted(df.Operation_Mode.dropna().unique())
sel_modes=st.sidebar.multiselect("Operation modes",modes,default=modes)
lo,hi=df.DateTime.min().date(),df.DateTime.max().date()
dates=st.sidebar.date_input("Date range",(lo,hi),min_value=lo,max_value=hi)
if isinstance(dates,tuple) and len(dates)==2:
    a,b=dates
else:a,b=lo,hi
x=df[df.Machine_ID.isin(selected)&df.Operation_Mode.isin(sel_modes)&df.DateTime.dt.date.between(a,b)].copy()
if x.empty:st.warning("No records match these filters.");st.stop()
cols=st.columns(4)
cols[0].metric("Observations",f"{len(x):,}")
cols[1].metric("Average speed",f"{x.Production_Speed_units_per_hr.mean():,.1f} units/hr")
cols[2].metric("Average defect rate",f"{x['Quality_Control_Defect_Rate_%'].mean():.2f}%")
cols[3].metric("Average error rate",f"{x['Error_Rate_%'].mean():.2f}%")
st.warning("Data readiness caveat: this sample has no documented engineering thresholds or efficiency label logic. The composite Machine Health Index is intentionally not calculated.")

tabs=st.tabs(["Factory overview","Machine health","Production & quality","Efficiency diagnostics","Data checks"])
with tabs[0]:
    c1,c2=st.columns(2)
    with c1:
        counts=x.Efficiency_Status.value_counts().rename_axis("Efficiency status").reset_index(name="Rows")
        st.plotly_chart(px.bar(counts,x="Efficiency status",y="Rows",color="Efficiency status",title="Efficiency label distribution"),use_container_width=True)
    with c2:
        fields=["Temperature_C","Vibration_Hz","Power_Consumption_kW","Network_Latency_ms","Packet_Loss_%"]
        opts=[z for z in fields if z in x]
        metric=st.selectbox("Sensor metric",opts)
        st.plotly_chart(px.line(x.sort_values("DateTime"),x="DateTime",y=metric,color="Operation_Mode",title=f"{metric} over time"),use_container_width=True)
    st.dataframe(x.groupby("Operation_Mode").agg(Records=("Machine_ID","size"),Speed=("Production_Speed_units_per_hr","mean"),Defect=("Quality_Control_Defect_Rate_%","mean"),Error=("Error_Rate_%","mean")).round(2),use_container_width=True)
with tabs[1]:
    sensor=st.selectbox("Trend metric",[c for c in ["Temperature_C","Vibration_Hz","Power_Consumption_kW","Network_Latency_ms","Packet_Loss_%"] if c in x],key="sensor")
    st.plotly_chart(px.line(x.sort_values("DateTime"),x="DateTime",y=sensor,color="Machine_ID",title=f"{sensor} by machine"),use_container_width=True)
    agg=x.groupby("Machine_ID").agg(Mean_Temperature=("Temperature_C","mean"),Mean_Vibration=("Vibration_Hz","mean"),Mean_Power=("Power_Consumption_kW","mean"),Mean_Speed=("Production_Speed_units_per_hr","mean"),Low_Label_Share=("Efficiency_Status",lambda s:(s=="Low").mean())).reset_index()
    st.dataframe(agg.round(3),use_container_width=True)
with tabs[2]:
    c1,c2=st.columns(2)
    with c1:st.plotly_chart(px.scatter(x,x="Production_Speed_units_per_hr",y="Quality_Control_Defect_Rate_%",color="Efficiency_Status",hover_data=["Machine_ID","Operation_Mode"],title="Production speed vs defect rate"),use_container_width=True)
    with c2:st.plotly_chart(px.box(x,x="Machine_ID",y="Error_Rate_%",color="Operation_Mode",title="Error rate by machine and mode"),use_container_width=True)
    st.caption("Defect density cannot be computed reliably without good-unit and total-unit counts.")
with tabs[3]:
    c1,c2=st.columns(2)
    with c1:st.plotly_chart(px.histogram(x,x="Efficiency_Status",color="Operation_Mode",barmode="group",title="Efficiency labels by mode"),use_container_width=True)
    with c2:st.plotly_chart(px.box(x,x="Production_Speed_units_per_hr",y="Efficiency_Status",color="Operation_Mode",title="Speed by efficiency label"),use_container_width=True)
    st.dataframe(pd.crosstab(x.Operation_Mode,x.Efficiency_Status,normalize="index").mul(100).round(2).astype(str)+"%",use_container_width=True)
with tabs[4]:
    st.write("Selected data quality checks")
    st.metric("Missing cells",f"{int(x.isna().sum().sum()):,}")
    st.metric("Exact duplicate rows",f"{int(x.drop(columns=['DateTime']).duplicated().sum()):,}")
    st.metric("Repeated date-time keys",f"{int(x.duplicated(['Date','Timestamp']).sum()):,}")
    st.write("Coverage",f"{x.DateTime.min()} to {x.DateTime.max()}")
    st.write("Efficiency status counts",x.Efficiency_Status.value_counts().to_frame("Rows"))
    st.caption("Repeated timestamps can be expected across machines. For operational time-series checks, test uniqueness on Machine_ID plus parsed timestamp and confirm clock synchronization.")
