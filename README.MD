# Bass diffusion analysis: Dreame X50 Ultra

The report covers all seven assignment steps: the chosen invention, historical
comparison, data, Bass parameter estimates, diffusion forecast, geographic scope,
and annual adopter estimates. The forecast uses the United States as its scope.

## Run the calculations

From this project folder, run:

```bash
python -m pip install -r requirements.txt
python build_data.py
python analysis.py
```

`build_data.py` saves the manually collected iRobot shipment figures and the
Fermi market-size assumptions. It reads the supplied `data/sources.json`; it
does not download data. Each historical observation has a source link.

`analysis.py` estimates the Bass model, checks predictions for 2022-2024,
calculates the Dreame forecasts, and generates all three figures. Its main
results are p = 0.000881, q = 0.325893, and M = 59.97 million shipment units.
That M belongs to iRobot's historical series. Dreame's base-case U.S. potential
is separately assumed to be about 2.65 million households.

## Folder contents

| File or folder | Contents |
| --- | --- |
| `build_data.py` | Source observations and market-size assumptions |
| `analysis.py` | Estimation, forecast check, projections, and charts |
| `requirements.txt` | Python dependencies |
| `data/irobot_shipments.csv` | Historical shipment data with row-level links |
| `data/model_results.json` | Unrounded parameter estimates and error measures |
| `data/historical_fit.csv` | Actual and fitted annual shipments |
| `data/holdout_validation.csv` | Three-year forecast check and benchmark |
| `data/dreame_normalized_forecast.csv` | Annual and cumulative percentages |
| `data/us_market_potential.csv` | Low, base, and high Fermi assumptions |
| `data/us_dreame_adopter_forecast.csv` | Annual and cumulative household counts |
| `img/historical_fit.png` | Reported shipments and fitted model |
| `img/normalized_forecast.png` | Cumulative and annual adoption percentages |
| `img/us_adopters.png` | Annual U.S. adopters in three scenarios |
| `report/report.tex` | LaTeX source |
| `report/report_latex_source.txt` | Identical source as plain text |
| `report/report.pdf` | Compiled report |