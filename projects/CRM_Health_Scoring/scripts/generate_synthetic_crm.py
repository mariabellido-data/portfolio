from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Synthetic CRM dataset generator — HEALTH SERVICES (ethical)
# ---------------------------------------------------------------------

COUNTRIES = [
    "Spain", "France", "Italy", "Germany", "Portugal",
    "Netherlands", "Sweden", "Denmark", "Ireland", "Belgium"
]

HEALTH_SERVICES = [
    "Primary Care Clinic",
    "Telemedicine Provider",
    "Mental Health Services",
    "Diagnostics Lab",
    "Rehabilitation Center",
    "Home Care Provider",
    "Public Health NGO",
]

# Behaviour priors by service line
ENGAGEMENT_MEAN = {
    "Primary Care Clinic": 0.70,
    "Telemedicine Provider": 0.75,
    "Mental Health Services": 0.68,
    "Diagnostics Lab": 0.62,
    "Rehabilitation Center": 0.65,
    "Home Care Provider": 0.66,
    "Public Health NGO": 0.64,
}
RESP_TIME_MEAN = {  # hours
    "Primary Care Clinic": 16,
    "Telemedicine Provider": 8,
    "Mental Health Services": 20,
    "Diagnostics Lab": 14,
    "Rehabilitation Center": 24,
    "Home Care Provider": 18,
    "Public Health NGO": 28,
}
REVENUE_MEAN_EUR = {  # annual scale (euros)
    "Primary Care Clinic": 600_000,
    "Telemedicine Provider": 700_000,
    "Mental Health Services": 500_000,
    "Diagnostics Lab": 800_000,
    "Rehabilitation Center": 450_000,
    "Home Care Provider": 550_000,
    "Public Health NGO": 250_000,
}

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))

def generate_crm(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    countries = rng.choice(COUNTRIES, size=n)
    services = rng.choice(HEALTH_SERVICES, size=n)

    engagement = np.array([
        np.clip(rng.normal(ENGAGEMENT_MEAN[s], 0.07), 0.05, 0.98)
        for s in services
    ])

    # Lognormal response time around service mean
    response_time = np.array([
        np.clip(rng.lognormal(mean=np.log(RESP_TIME_MEAN[s]) - 0.1, sigma=0.30), 2, 72)
        for s in services
    ])

    # New patients/referrals converted ~ Poisson scaled by engagement
    leads_converted = rng.poisson(lam=np.clip(engagement * 14, 1.5, None)).astype(int)

    # Patient satisfaction [1..10]
    satisfaction = np.clip(5.2 + engagement * 3.8 + rng.normal(0, 0.8, size=n), 1, 10)

    # Annual revenue (or operating budget for NGO) — lognormal around scale
    revenue = np.array([
        float(np.clip(rng.lognormal(mean=np.log(REVENUE_MEAN_EUR[s]) - 0.25, sigma=0.40), 80_000, 4_000_000))
        for s in services
    ])

    # Churn/attrition risk (lower with high engagement/satisfaction, higher with slow response)
    z = (
        -1.9
        - 2.1 * engagement
        - 0.22 * (satisfaction - 5)
        + 0.035 * response_time
        - 0.0000025 * revenue
        - 0.03 * leads_converted
    )
    churn_prob = sigmoid(z)
    churn_risk = (rng.uniform(size=n) < churn_prob).astype(int)

    df = pd.DataFrame({
        "Client_ID": [f"C{str(i+1).zfill(4)}" for i in range(n)],
        "Country": countries,
        "Service_Line": services,
        "Engagement_Rate": engagement.round(3),
        "Response_Time_Hours": response_time.round(1),
        "Leads_Converted": leads_converted,
        "Satisfaction_Score": satisfaction.round(1),
        "Revenue_Last_Year_EUR": revenue.round(2),
        "Churn_Risk": churn_risk,
    })
    return df

def main():
    parser = argparse.ArgumentParser(description="Generate a synthetic HEALTH CRM dataset.")
    parser.add_argument("--n", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("projects/CRM_Health_Scoring/data/crm_data_sample.csv"),
    )
    args = parser.parse_args()

    df = generate_crm(n=args.n, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df):,} rows to {args.out.resolve()}")

if __name__ == "__main__":
    main()

