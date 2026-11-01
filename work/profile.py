import pandas as pd
p=r'C:\Users\samee\Downloads\Thales_Group_Manufacturing (1).csv'
d=pd.read_csv(p)
print(d['Predictive_Maintenance_Score'].corr(d['Error_Rate_%']))
print(d.groupby('Efficiency_Status')['Error_Rate_%'].mean())
print(d.groupby('Efficiency_Status')['Production_Speed_units_per_hr'].mean())
print(d.groupby('Efficiency_Status').size()/len(d))
print(d['Machine_ID'].nunique(),d['Operation_Mode'].value_counts())
print('repeated timestamps',d.duplicated(['Date','Timestamp']).sum())
