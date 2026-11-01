from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

out=Path('outputs'); out.mkdir(exist_ok=True)
NAVY='17365D'; BLUE='2F75B5'; PALE='EAF1F8'
def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def border_table(t):
    t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for row in t.rows:
      for c in row.cells: c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def setup(d):
    sec=d.sections[0]; sec.top_margin=Inches(.68); sec.bottom_margin=Inches(.68); sec.left_margin=Inches(.78); sec.right_margin=Inches(.78)
    styles=d.styles; styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(10.5); styles['Normal'].font.color.rgb=RGBColor(38,48,60)
    for st,size in [('Title',25),('Heading 1',16),('Heading 2',12)]:
      styles[st].font.name='Aptos Display'; styles[st].font.size=Pt(size); styles[st].font.color.rgb=RGBColor.from_string(NAVY)
    h=sec.header.paragraphs[0]; h.text='MANUFACTURING PROCESS HEALTH  |  ANALYTICAL BASELINE'; h.style='Caption'
    f=sec.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.RIGHT; f.add_run('Thales Group dataset review  •  1 November 2026')
def title(d,txt,sub):
    p=d.add_paragraph(style='Title'); p.add_run(txt)
    p=d.add_paragraph(); r=p.add_run(sub); r.italic=True; r.font.color.rgb=RGBColor(90,105,120)
def heading(d,txt,l=1):d.add_heading(txt,level=l)
def para(d,txt):d.add_paragraph(txt)
def bullets(d,arr):
    for x in arr:d.add_paragraph(x,style='List Bullet')
def table(d,headers,rows,widths=None):
    t=d.add_table(rows=1,cols=len(headers)); border_table(t)
    for i,h in enumerate(headers):
      c=t.rows[0].cells[i];c.text=h;shade(c,NAVY)
      for r in c.paragraphs[0].runs:r.font.bold=True;r.font.color.rgb=RGBColor(255,255,255);r.font.size=Pt(9)
    for n,row in enumerate(rows):
      cells=t.add_row().cells
      for i,x in enumerate(row):
        cells[i].text=str(x)
        if n%2:shade(cells[i],PALE)
        for p in cells[i].paragraphs:
          for r in p.runs:r.font.size=Pt(9)
    return t

# Report
D=Document();setup(D);title(D,'Manufacturing Process Health and Operational Efficiency','Diagnostic baseline for a 6G enabled smart factory | Dataset analysis, 1 January–10 March 2025')
para(D,'Executive finding. The supplied file is useful for demonstrating a monitoring workflow, but it does not establish actionable machine health patterns. Sensor and quality measures are almost uncorrelated in this sample; the efficiency label is principally reflected in error rate and production speed. Treat results as a data quality baseline, not as evidence of real plant performance or 6G impact.')
heading(D,'1. Scope and approach')
para(D,'We analyzed the supplied Thales_Group_Manufacturing CSV as provided. It contains 100,000 observations across 50 machine identifiers and three operation modes. The file uses Timestamp rather than the brief’s Time field. Date and Timestamp were combined for temporal checks. Descriptive statistics, missingness, duplicates, label and mode distributions, machine summaries, and Pearson correlations were reviewed. This is observational analysis; no causal claims or predictive model validation are made.')
heading(D,'2. Data validation and readiness')
table(D,['Check','Finding','Interpretation'],[
('Rows / columns','100,000 / 14','Large enough for descriptive exploration.'),('Coverage','1 Jan–10 Mar 2025','69 days; timestamps are minute-level.'),('Missing values','0 across all columns','No imputation required for this snapshot.'),('Exact duplicate rows','0','No exact row duplicates.'),('Repeated date-time keys','1,440','Multiple machine observations share minute stamps; expected in a fleet, but machine-time uniqueness should be checked.'),('Ordering','One backward one-minute step in file order','Sort by parsed datetime before time-series work.'),('Ranges','Temperature 30–90 °C; vibration 0.1–5 Hz; power 1.5–10 kW; latency 1–50 ms','Values appear bounded and unusually uniform; validate against sensor specifications and plant control limits.'),('Identifier / mode','50 machine IDs; Active 70.1%, Idle 20.1%, Maintenance 9.9%','Labels are consistent in this extract.')])
para(D,'The measured values are highly regular and largely independent of machine, mode, and one another. This pattern is consistent with synthetic or randomized data, though provenance cannot be established from the CSV alone. Before operational use, obtain data lineage, sensor calibration ranges, shift schedules, production context, and confirmed definitions for the predictive maintenance score and efficiency label.')
heading(D,'3. KPI baseline')
table(D,['Indicator','Observed baseline','How to read it'],[
('Efficiency distribution','High 2.99% (2,986); Medium 19.19% (19,189); Low 77.83% (77,825)','Strong Low class imbalance. Not a fleet benchmark without a verified label definition.'),('Production speed','Mean 275.9 units/hour; machine means 270.0–284.9','Small between-machine spread (SD of machine means 3.4). Not adjusted for product mix or scheduled state.'),('Defect rate','Mean 5.01%','No meaningful linear relationship with sensor readings or speed in this file.'),('Error rate','Mean 7.50%','Varies with efficiency class; class averages are 1.01% High, 2.73% Medium, 8.93% Low.'),('Machine health index','Not calculated as a single score','No engineering thresholds, weights, or directionality were supplied. A composite would imply unsupported standards.')])
heading(D,'4. Operational diagnostics')
heading(D,'Efficiency labels and operation modes',2)
para(D,'Mode distributions are nearly indistinguishable: the High share is about 3.0% in Active, 2.8% in Idle, and 3.0% in Maintenance; Low is about 77.7%, 78.3%, and 77.8%, respectively. These figures do not support a mode-specific efficiency intervention. Confirm whether Idle and Maintenance records should be included in an efficiency denominator.')
heading(D,'Sensors, output, defects, and errors',2)
para(D,'Across the numeric fields, temperature, vibration, power, network latency, packet loss, defect rate, and maintenance score show correlations close to zero with production speed and defect rate (absolute Pearson r below 0.01 in this extract). Vibration also has essentially no linear association with error rate. This does not rule out nonlinear or lagged effects, but the present data provides no useful evidence for them.')
para(D,'The efficiency label aligns much more strongly with error rate and speed: Low rows average 254.9 units/hour and 8.93% error, while High rows average 450.8 units/hour and 1.01% error. This may be because these variables define or inform the label; the label-generation logic is undocumented. Do not treat this association as independent validation or model performance.')
heading(D,'Machine comparisons',2)
para(D,'The proportion of High labels by machine ranges only from 2.3% to 3.7%, and machine-average speed ranges from 270.0 to 284.9 units/hour. Given the narrow spreads and likely randomized structure, ranking machines would create false precision. The dashboard therefore supports inspection and filtering but should not be used to declare a machine unhealthy.')
heading(D,'5. Recommendations')
bullets(D,[
'Confirm source provenance and whether rows are simulated, randomized, or derived from production systems. Preserve an explicit data dictionary and label-generation rules.',
'Add engineering limits per machine and product: warning/alarm temperature, vibration spectra and units, power envelopes, and acceptable network latency and packet loss.',
'Add product/part identifiers, good and total units, planned production time, downtime reason, shift, maintenance events, and operating state. Define whether speed is instantaneous or period-normalized.',
'Validate timestamp semantics, timezone, machine-time key uniqueness, clock synchronization, and missing intervals. Sort before any trend analysis.',
'Define the Predictive_Maintenance_Score scale and direction. Validate it against maintenance outcomes and lead time before using it for decisions.',
'For a pilot, baseline each machine by product and operating mode; use robust control charts and alert thresholds reviewed by process engineers. Track false alarms and missed events.',
'Assess 6G contribution separately with network-side measurements and controlled comparisons. This file alone cannot attribute efficiency or quality outcomes to 6G.'
])
heading(D,'6. Limitations')
para(D,'The extract has no documented sampling method, production context, sensor limits, label definition, or confirmed 6G network provenance. Correlations are descriptive and linear; they do not establish causation. Averages conceal short-lived excursions. No inferential tests, forecasting, or predictive maintenance model was validated. The reported defect percentage is not a defect count normalized by produced units, so the requested defect density KPI cannot be computed reliably.')
heading(D,'Appendix: reproducible definitions')
bullets(D,['Average production speed = arithmetic mean of Production_Speed_units_per_hr; also summarized by machine.','Efficiency distribution = row share for each Efficiency_Status category.','Defect density was not derived; the defect-rate field is retained as reported because production denominator semantics are unknown.','No Machine Health Index was fabricated. Introduce one only after engineering-approved thresholds and weights exist.'])
D.save(out/'Manufacturing_Process_Health_Research_Report.docx')

# Executive summary
E=Document();setup(E);title(E,'Smart Factory Process Health Executive Brief','Evidence, limits, and actions for public sector and industrial stakeholders')
para(E,'The supplied 100,000-row dataset does not yet provide a dependable basis for machine health decisions. It can support a monitoring prototype and a data readiness exercise, but field teams should not use its labels to prioritize maintenance or claim 6G-enabled productivity gains.')
heading(E,'What the data says')
bullets(E,['Coverage: 50 machines, 1 January–10 March 2025, with no missing cells or exact duplicate rows.','Efficiency labels: 77.8% Low, 19.2% Medium, and 3.0% High. Mode-level shares are almost identical.','Average reported speed is 275.9 units/hour; average defect rate is 5.01% and average error rate is 7.50%.','Sensor metrics have near-zero linear relationships with production speed and defects. Low labels coincide with higher error and lower speed, but the label logic is unknown.'])
heading(E,'Why caution is needed')
para(E,'Values appear bounded and unusually uniform, and most sensor fields do not vary meaningfully with outcomes. The CSV does not document sensor limits, label rules, product mix, shifts, machine state semantics, or whether records came from operational systems. These gaps prevent reliable health scoring, machine rankings, or causal claims about 6G.')
heading(E,'Recommended next steps')
table(E,['Priority','Action','Decision enabled'],[
('1','Verify data provenance, label logic, sensor units, and operational limits with plant owners.','Establish whether the current sample represents factory operations.'),('2','Join production counts, product/part, shift, downtime and maintenance work orders.','Measure quality and efficiency on comparable operating conditions.'),('3','Pilot per-machine dashboards with reviewed thresholds and alert feedback.','Find actionable excursions and measure false alarms.'),('4','Evaluate network performance and production outcomes in a controlled 6G pilot.','Attribute any observed gains to network changes with credible evidence.')])
heading(E,'Suggested governance position')
para(E,'Fund a staged diagnostic pilot focused first on data validation and operator review. Require documented KPI definitions, engineering-approved limits, and a baseline before scaling. Report observed associations separately from causal evidence, and do not present the current Low label share as a verified national or industry benchmark.')
para(E,'Dataset reviewed: Thales_Group_Manufacturing (1).csv. Analysis period inferred from supplied dates: 1 January–10 March 2025. Prepared 1 November 2026.')
E.save(out/'Smart_Factory_Executive_Summary.docx')
