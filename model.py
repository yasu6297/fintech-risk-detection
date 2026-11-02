import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score

print("Loading transactions and engineering behavioral features...")
df = pd.read_csv("transactions.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# 1. Feature Engineering: User Historical Baseline Spending
user_baselines = df.groupby("user_id")["amount"].agg(["mean", "std"]).reset_index()
user_baselines.columns = ["user_id", "user_avg_amount", "user_std_amount"]
user_baselines["user_std_amount"] = user_baselines["user_std_amount"].fillna(1.0)

df = df.merge(user_baselines, on="user_id", how="left")

# Amount Z-score: Standard deviations away from user's historical spend
df["amount_zscore"] = (df["amount"] - df["user_avg_amount"]) / df["user_std_amount"]

# Transaction Velocity: Seconds elapsed since previous transaction by same user
df["prev_timestamp"] = df.groupby("user_id")["timestamp"].shift(1)
df["seconds_since_prev_txn"] = (df["timestamp"] - df["prev_timestamp"]).dt.total_seconds().fillna(86400)

# 2. Prepare Features for Unsupervised Isolation Forest
feature_cols = ["amount", "amount_zscore", "seconds_since_prev_txn", "device_risk_score"]
X = df[feature_cols].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. Model Training: Isolation Forest (Contamination = expected rare event rate ~1.5%)
print("Training Isolation Forest anomaly detector...")
iso = IsolationForest(n_estimators=120, contamination=0.015, random_state=42)
preds = iso.fit_predict(X_scaled)

# Isolation Forest tags -1 for anomalies, 1 for normal
df["anomaly_flag"] = np.where(preds == -1, 1, 0)
df["anomaly_score"] = iso.decision_function(X_scaled) * -1  # Higher score = higher anomaly risk

# 4. Model Evaluation Telemetry
print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(df["is_fraud"], df["anomaly_flag"], target_names=["Normal", "Anomaly/Fraud"]))
print(f"ROC-AUC Score: {roc_auc_score(df['is_fraud'], df['anomaly_score']):.4f}")

# Save scored dataset for the dashboard
df.to_csv("scored_transactions.csv", index=False)
print("Saved final telemetry to 'scored_transactions.csv'!")
