from pathlib import Path
p=Path('outputs/app.py')
s=p.read_text(encoding='utf-8')
s=s.replace('import plotly.express as px\nimport streamlit as st', 'import plotly.express as px\nimport streamlit as st\nfrom pathlib import Path')
s=s.replace('@st.cache_data\ndef read_data(file):\n    d=pd.read_csv(file)', '@st.cache_data\ndef read_data(file_path):\n    d=pd.read_csv(file_path)')
old='''up=st.sidebar.file_uploader("Upload manufacturing CSV", type="csv")
if up is None:
    st.info("Upload the supplied CSV to begin. The dashboard expects Date, Timestamp, Machine_ID, Operation_Mode, sensor, production, quality, and Efficiency_Status columns.")
    st.stop()
df=read_data(up)'''
new='''DATA_PATH = Path(__file__).parent / "Thales_Group_Manufacturing.csv"
if not DATA_PATH.exists():
    st.error(f"Bundled dataset not found: {DATA_PATH.name}. Keep the CSV in the same folder as app.py.")
    st.stop()
df=read_data(str(DATA_PATH))'''
if old not in s: raise SystemExit('upload block not found')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
Path('outputs/README.txt').write_text('Smart Factory Process Health dashboard\n\nThe dataset is bundled beside app.py and loads automatically. Keep Thales_Group_Manufacturing.csv in this folder.\n\nRun from this folder:\n  python -m pip install -r requirements.txt\n  python -m streamlit run app.py\n\nThe dashboard filters by machine, operation mode, and date range. It reports descriptive indicators only. No engineering limits or label logic were supplied, so it does not calculate a health index or issue condition alerts.\n',encoding='utf-8')
