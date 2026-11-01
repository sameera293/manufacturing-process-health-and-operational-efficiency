Smart Factory Process Health dashboard

The dataset is bundled beside app.py and loads automatically. Keep Thales_Group_Manufacturing.csv in this folder.

Run from this folder:
  python -m pip install -r requirements.txt
  python -m streamlit run app.py

The dashboard filters by machine, operation mode, and date range. It reports descriptive indicators only. No engineering limits or label logic were supplied, so it does not calculate a health index or issue condition alerts.
