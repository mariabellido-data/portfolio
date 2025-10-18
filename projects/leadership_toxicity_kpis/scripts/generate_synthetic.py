#!/usr/bin/env python3
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def make_data(n: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Categorical features
    teams = np.array(["Ops", "Sales", "Support", "Tech", "Finance"])
    genders = np.array(["F", "M", "Other"])

    team = rng.choice(teams, size=n, replace=True, p=[0.25, 0.2, 0.25, 0.2, 0.1])
    gender = rng.choice(genders, size=n, replace=True, p=[0.48, 0.48, 0.04])

    # Supervisor toxicity score: 0–10
    tox = np.clip(rng.gamma(shape=1.8, scale=2.2, size=n), 0, 10)

    # Boundary violations (discrete)
    boundary_viol = rng.poisson(lam=np.clip(0.2 + 0.35 * (tox/10) * 5, 0.2, 3.0), size=n)

    # Motivation 0–100 (negatively correlated with toxicity, plus noise)
    motivation = np.clip(80 - 6.5*tox + rng.normal(0, 8, n), 0, 100)

    # Absenteeism days/quarter
    base_abs = 1.5 + 0.9*tox + 0.03*(100 - motivation) + 0.4*boundary_viol
    absenteeism = np.clip(rng.normal(base_abs, 1.2, n), 0, None)

    # Performance 0–100
    perf = np.clip(78 - 4.8*tox - 0.8*absenteeism + rng.normal(0, 7, n), 0, 100)

    # Leadership boundary-blurring proxy (0/1)
    boundary_blur = (rng.uniform(0, 1, n) < np.clip(0.05 + 0.07*tox, 0, 0.6)).astype(int)

    df = pd.DataFrame({
        "employee_id": np.arange(1, n+1),
        "team": team,
        "gender": gender,
        "supervisor_toxicity": tox.round(2),
        "boundary_violations": boundary_viol,
        "boundary_blur_flag": boundary_blur,
        "motivation": motivation.round(1),
        "absenteeism_days": absenteeism.round(1),
        "performance_score": perf.round(1),
    })
    return df

def save_charts(df: pd.DataFrame, charts_dir: Path):
    charts_dir.mkdir(parents=True, exist_ok=True)

    # 1) Toxicity distribution
    plt.figure()
    plt.hist(df["supervisor_toxicity"], bins=20)
    plt.title("Supervisor Toxicity — Distribution")
    plt.xlabel("Toxicity (0–10)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(charts_dir / "toxicity_distribution.png", dpi=150)
    plt.close()

    # 2) Toxicity vs Absenteeism (scatter)
    plt.figure()
    plt.scatter(df["supervisor_toxicity"], df["absenteeism_days"], alpha=0.5)
    plt.title("Toxicity vs Absenteeism")
    plt.xlabel("Supervisor Toxicity (0–10)")
    plt.ylabel("Absenteeism (days/quarter)")
    plt.tight_layout()
    plt.savefig(charts_dir / "toxicity_vs_absenteeism.png", dpi=150)
    plt.close()

    # 3) Absenteeism by Team (boxplot)
    groups = [g["absenteeism_days"].values for _, g in df.groupby("team")]
    labels = list(df.groupby("team").groups.keys())
    plt.figure()
    plt.boxplot(groups, labels=labels, showmeans=True)
    plt.title("Absenteeism by Team")
    plt.xlabel("Team")
    plt.ylabel("Absenteeism (days/quarter)")
    plt.tight_layout()
    plt.savefig(charts_dir / "absenteeism_by_team.png", dpi=150)
    plt.close()

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic dataset for leadership toxicity & KPIs with charts."
    )
    parser.add_argument("-n", "--n_rows", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data/leadership_toxicity_kpis.csv"))
    parser.add_argument("--charts-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()

    df = make_data(n=args.n_rows, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    save_charts(df, args.charts_dir)

    # Console KPI summary
    corr = df[["supervisor_toxicity","absenteeism_days","performance_score","motivation"]].corr()
    print(f"Wrote {len(df):,} rows to {args.out}")
    print("\nCorrelation matrix (Pearson):")
    print(corr.round(2))

if __name__ == "__main__":
    main()
