# Leadership Toxicity KPIs

This project generates **synthetic workplace data** to analyse the relationship between toxic supervision, motivation, and absenteeism.  
It is part of a broader portfolio on **ethical auditing of workplace performance and leadership accountability**.

## Structure
- **data/** — synthetic datasets  
- **scripts/** — Python code to generate and analyse data  
- **notebooks/** — exploratory analysis with visualisations  
- **reports/** — exported charts and metrics summaries  

## Objective
To model how **toxic leadership behaviours** (micromanagement, boundary violations, emotional volatility) can correlate with:
- absenteeism rates  
- performance drop  
- employee disengagement  

## Next steps
1. Generate synthetic dataset (Python, Pandas, NumPy)
2. Compute correlation metrics and KPI summaries
3. Visualise distributions (Matplotlib)
4. Export final report for ethical audit case study

![Toxicity distribution](reports/toxicity_distribution.png)
![Toxicity vs Absenteeism](reports/toxicity_vs_absenteeism.png)
![Absenteeism by Team](reports/absenteeism_by_team.png)


## Dashboard

- Notebook: `notebooks/02_dashboard.ipynb`
- KPI Summary (PNG): `reports/kpi_summary.png`
- Correlations Heatmap (PNG): `reports/correlations_heatmap.png`

### Quick preview
![KPI Summary](reports/kpi_summary.png)
![Correlations Heatmap](reports/correlations_heatmap.png)
