import numpy as np
import pandas as pd
from datetime import datetime, timedelta

print("Generating FinTech transaction stream...")
np.random.seed(42)
n_records = 50000

# 1,000 unique user IDs
user_ids = [f"USR_{i:04d}" for i in range(1, 1001)]
start_date = datetime(2026, 1, 1)

# Baseline user transactions
data = {
    "transaction_id": [f"TXN_{i:07d}" for i in range(n_records)],
    "user_id": np.random.choice(user_ids, n_records),
    "timestamp": [
        start_date + timedelta(minutes=int(x)) 
        for x in np.random.exponential(scale=45, size=n_records).cumsum() % (60 * 24 * 60)
    ],
    "amount": np.round(np.random.lognormal(mean=5.8, sigma=0.9, size=n_records), 2),
    "payment_mode": np.random.choice(
        ["UPI_P2M", "UPI_P2P", "DEBIT_CARD", "NET_BANKING"], 
        n_records, 
        p=[0.58, 0.30, 0.08, 0.04]
    ),
    "device_risk_score": np.random.beta(a=1.5, b=8.0, size=n_records)  # Range 0.0 to 1.0
}

df = pd.DataFrame(data).sort_values(by=["user_id", "timestamp"]).reset_index(drop=True)

# Inject 1% realistic anomaly attack patterns (ticket bursts + velocity spikes)
fraud_count = int(n_records * 0.01)
fraud_indices = np.random.choice(df.index, size=fraud_count, replace=False)

df.loc[fraud_indices, "amount"] = df.loc[fraud_indices, "amount"] * np.random.uniform(12, 28)
df.loc[fraud_indices, "device_risk_score"] = np.random.uniform(0.75, 0.98, size=fraud_count)
df["is_fraud"] = 0
df.loc[fraud_indices, "is_fraud"] = 1

df.to_csv("transactions.csv", index=False)
print(f"Generated 50,000 transactions with {df['is_fraud'].sum()} labeled anomalies in 'transactions.csv'!")