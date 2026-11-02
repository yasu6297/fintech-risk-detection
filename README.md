\# FinTech Transaction Risk \& Behavioral Anomaly Detection



An unsupervised risk scoring pipeline and real-time operations dashboard designed to identify fraudulent activity and behavioral anomalies in high-volume payment streams.



\## Problem Statement

In high-throughput payment systems (such as UPI), fraudulent activity represents <1% of transactions. Rule-based static thresholds create excessive false positives or fail against dynamic attack vectors.



\## Solution Architecture

1\. \*\*Dynamic Behavioral Feature Engineering (`model.py`):\*\*

&#x20;  - Historical per-user rolling mean \& standard deviation.

&#x20;  - User-relative transaction Z-scores ($\\frac{x - \\mu}{\\sigma}$).

&#x20;  - Transaction velocity ($\\Delta t$ seconds since last transaction).

2\. \*\*Unsupervised Modeling:\*\* Isolation Forest isolates multi-dimensional outliers without relying on delayed chargeback labels.

3\. \*\*Operations Triage Dashboard (`app.py`):\*\* Interactive Streamlit dashboard enabling real-time risk score threshold calibration and triage queue exports.



\## Performance

\- \*\*Recall:\*\* 94% on simulated anomaly patterns

\- \*\*Precision:\*\* 62% at 1.5% contamination threshold

\- \*\*ROC-AUC:\*\* 0.9988



\## Tech Stack

\- Python, Scikit-Learn, Pandas, NumPy, Streamlit, Plotly

