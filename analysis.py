"""Fit the Bass model, forecast adoption, and draw the report's three figures."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

folder = Path(__file__).resolve().parent
data_folder = folder / "data"
image_folder = folder / "img"
image_folder.mkdir(exist_ok=True)


def bass_F(t, p, q):
    """Cumulative fraction of the potential market that has adopted."""
    e = np.exp(-(p + q) * np.asarray(t))
    return (1 - e) / (1 + (q / p) * e)


def annual_sales(t, p, q, M):
    return M * (bass_F(t, p, q) - bass_F(t - 1, p, q))


def fit_bass(t, sales):
    # M is in millions. Broad bounds keep all three parameters positive.
    parameters, _ = curve_fit(
        annual_sales, t, sales, p0=[0.001, 0.3, 60],
        bounds=([1e-8, 1e-8, 1], [1, 3, 10000]),
        x_scale="jac", max_nfev=10000,
        ftol=1e-10, xtol=1e-10, gtol=1e-10
    )
    return parameters


def rmse(actual, predicted):
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


# Roomba launched in 2002. FY2005 is therefore model year 4.
data = pd.read_csv(data_folder / "irobot_shipments.csv")
years = data.fiscal_year.to_numpy()
t = years - 2001
sales = data.units_thousands.to_numpy() / 1000
p, q, M = fit_bass(t, sales)
fitted = annual_sales(t, p, q, M)
r_squared = 1 - np.sum((sales - fitted) ** 2) / np.sum((sales - sales.mean()) ** 2)

pd.DataFrame({
    "fiscal_year": years, "observed_million": sales,
    "fitted_million": fitted, "residual_million": sales - fitted
}).to_csv(data_folder / "historical_fit.csv", index=False)

# Check a forecast made using only data through 2021.
train = years <= 2021
early_parameters = fit_bass(t[train], sales[train])
test_prediction = annual_sales(t[~train], *early_parameters)
benchmark = np.repeat(sales[train][-1], sum(~train))
pd.DataFrame({
    "fiscal_year": years[~train], "observed_million": sales[~train],
    "bass_forecast_million": test_prediction, "last_value_million": benchmark
}).to_csv(data_folder / "holdout_validation.csv", index=False)

results = {
    "p": float(p), "q": float(q), "M_million": float(M),
    "r_squared": float(r_squared), "rmse_million": rmse(sales, fitted),
    "peak_time_years": float(np.log(q / p) / (p + q)),
    "half_adoption_years": float(np.log(2 + q / p) / (p + q)),
    "holdout_p": float(early_parameters[0]),
    "holdout_q": float(early_parameters[1]),
    "holdout_M_million": float(early_parameters[2]),
    "holdout_rmse_million": rmse(sales[~train], test_prediction),
    "benchmark_rmse_million": rmse(sales[~train], benchmark)
}
(data_folder / "model_results.json").write_text(json.dumps(results, indent=2))

# Transfer p and q to Dreame. The forecast starts at zero product adoption.
forecast_years = np.arange(1, 31)
cumulative = bass_F(np.arange(31), p, q)
annual = np.diff(cumulative)
pd.DataFrame({
    "year_after_launch": forecast_years,
    "annual_pct": 100 * annual, "cumulative_pct": 100 * cumulative[1:]
}).to_csv(data_folder / "dreame_normalized_forecast.csv", index=False)

# Use a separate household market size for each U.S. scenario.
market = pd.read_csv(data_folder / "us_market_potential.csv")
forecasts = []
for row in market.itertuples():
    forecasts.append(pd.DataFrame({
        "scenario": row.scenario, "year_after_launch": forecast_years,
        "market_potential_households": row.market_potential_households,
        "annual_adopters": np.rint(row.market_potential_households * annual).astype(int),
        "cumulative_adopters": np.rint(row.market_potential_households * cumulative[1:]).astype(int)
    }))
adopters = pd.concat(forecasts, ignore_index=True)
adopters.to_csv(data_folder / "us_dreame_adopter_forecast.csv", index=False)

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

# Figure 1: historical shipments and fitted annual volumes.
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(years, sales, color="lightsteelblue", label="Reported shipments")
ax.plot(years, fitted, color="navy", label="Bass fit")
ax.set(xlabel="Fiscal year", ylabel="Million robots shipped")
ax.set_xticks(np.arange(2005, 2025, 3))
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(image_folder / "historical_fit.png", dpi=200)
plt.close(fig)

# Figure 2: cumulative and annual shares of Dreame's potential market.
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
axes[0].plot(np.arange(31), 100 * cumulative, color="navy")
axes[0].set(title="Cumulative adoption", ylabel="% of potential households", ylim=(0, 100))
axes[1].bar(forecast_years, 100 * annual, color="teal")
axes[1].set(title="Adoption during each year", ylabel="% of potential households")
for ax in axes:
    ax.set_xlabel("Years after launch")
fig.tight_layout()
fig.savefig(image_folder / "normalized_forecast.png", dpi=200)
plt.close(fig)

# Figure 3: changing M changes the scale, not the timing of adoption.
fig, ax = plt.subplots(figsize=(8, 3.5))
for scenario in ["Low", "Base", "High"]:
    subset = adopters[adopters.scenario == scenario]
    ax.plot(subset.year_after_launch, subset.annual_adopters / 1000, label=scenario)
ax.set(xlabel="Year after launch", ylabel="New adopting households (thousands)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(image_folder / "us_adopters.png", dpi=200)
plt.close(fig)

print(f"p = {p:.6f}, q = {q:.6f}, M = {M:.2f} million")
print(f"R-squared = {r_squared:.3f}; RMSE = {results['rmse_million']:.3f} million")
print(f"Holdout RMSE = {results['holdout_rmse_million']:.3f} million")
