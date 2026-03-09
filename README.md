# HydroVigil
### AI-Powered Cyber Attack Detection for Smart Water Infrastructure

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=flat-square&logo=pytorch)
![Accuracy](https://img.shields.io/badge/Accuracy-97--98%25-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Dataset](https://img.shields.io/badge/Dataset-SWaT-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

> **Detect. Alert. Protect.** — Real-time time-series anomaly detection for cyber threat identification in water pipeline infrastructure.

---

## 📸 Demo & Screenshots

SCREENSHOTS
<!-- Add your dashboard screenshot here -->
> <img width="930" height="428" alt="image" src="https://github.com/user-attachments/assets/f5e7479f-f161-406c-909e-2356d320779f" />
> <img width="934" height="440" alt="image" src="https://github.com/user-attachments/assets/cf82b4f1-b4d7-4d42-9e97-66a5adb7ead8" />
> <img width="968" height="433" alt="image" src="https://github.com/user-attachments/assets/bb5f364d-a057-408b-b787-9d98d058a830" />
> <img width="900" height="456" alt="image" src="https://github.com/user-attachments/assets/63e62a35-354b-4ad9-9ca3-3cd1e37a5e8b" />
> <img width="985" height="512" alt="image" src="https://github.com/user-attachments/assets/df327fbb-06f3-4c49-8abe-d2057cfe7b3a" />
> <img width="975" height="488" alt="image" src="https://github.com/user-attachments/assets/0c3c33a6-e6c4-42bb-b4f5-d4d4d09a16a2" />
> <img width="979" height="551" alt="image" src="https://github.com/user-attachments/assets/2c1b2b25-4cc5-44b9-a1bb-54ac859f5f3e" />

<!-- Add your demo GIF or video link here -->
DEMO VIDEO
> Drive link : https://drive.google.com/file/d/1laPnz7cy6maIVQA9Y5gJi7PJEJu9kZLG/view?usp=sharing

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Solution Architecture](#-solution-architecture)
- [ML Model Details](#-ml-model-details)
- [Results](#-results)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [How to Use](#-how-to-use)
- [Dataset](#-dataset)
- [Fault Tolerance](#-fault-tolerance)
- [Business Model](#-business-model)
- [Team](#-team)

---

## 🔍 Overview

**HydroVigil** is an AI-powered monitoring system that detects cyber-attacks in real-time by analyzing time-series sensor data from water pipeline infrastructure. It uses a dual-model architecture (Transformer + LSTM) to identify abnormal behavioral patterns caused by malicious manipulation of SCADA/IoT sensor data.

Unlike traditional static threshold-based systems, HydroVigil learns the **normal behavioral baseline** of the pipeline and flags deviations that match known cyber-attack signatures — all without requiring labeled attack data upfront.

---

## 🚨 Problem Statement

Water pipelines are critical national infrastructure. With the rise of IoT and SCADA systems, the attack surface has expanded dramatically:

- Cyber-attacks mimic normal fluctuations and go **undetected for hours**
- Manual monitoring **cannot scale** with real-time sensor data volumes
- Real-world attacks (Oldsmar 2021, Pennsylvania 2023, Bengaluru 2025) have proven the threat is **active and growing**

**Traditional monitoring is not sufficient for cyber-aware detection.**

---

## 🏗️ Solution Architecture

```
DATA INPUT
├── Real-Time Sensor Streams
└── Historical Pipeline Data
        │
        ▼
DATA ACQUISITION LAYER
        │
        ▼
PREPROCESSING & FEATURE ENGINEERING
├── Missing Value Handling
├── Normalization
├── Time-Series Feature Extraction
│   ├── Temporal Patterns
│   └── Trend & Seasonality
        │
        ▼
MODELING & DETECTION
└── Baseline Behavior Modeling
        │
        ▼
SECURITY ANALYSIS & RESPONSE
├── Cyber-Attack Classification Layer
├── Identify Attack-Like Behavior
├── Alert & Visualization Layer
├── Dashboard Display
└── Human Analyst / Operator
        │
        ▼ (Analyst Feedback Loop)
```

---

## 🤖 ML Model Details

HydroVigil uses a **confidence-based dual-model architecture**:

### Primary Model — Transformer
- Captures long-range temporal dependencies in sensor data
- Dominant decision-maker in the pipeline
- Outputs a confidence score per window

### Fallback Model — LSTM
- Fault-tolerant fallback activated only when Transformer confidence is low (~3% of scenarios)
- Ensures continuous detection even during model uncertainty

### Decision Logic
```
if transformer_confidence >= threshold:
    use transformer_prediction
else:
    use lstm_prediction  # fallback activated
```

### Window-Based Processing
Instead of processing every single data point, the system uses **sliding windows**:
- Window size: **100 seconds**
- Stride: **10**
- Drastically reduces computational load while maintaining detection accuracy

```python
window_size = 100
stride = 10
X_train_windows = create_windows(X_train_std, window_size, stride)
# Train windows shape: (138700, 100, 44)
```

---

## 📊 Results

| Metric | Score |
|--------|-------|
| Overall Accuracy | **97–98%** |
| Normal Detection F1-Score | **0.99** |
| Attack Detection F1-Score | **0.72–0.73** |
| Macro F1-Score | **0.83–0.86** |
| Weighted F1-Score | **0.97–0.98** |

### Dual Model Redundancy
| Metric | Score |
|--------|-------|
| Accuracy | 0.98 |
| Macro F1 | 0.86 |
| Weighted F1 | 0.98 |
| Attack F1 | 0.73 |
| Attack Recall | 0.70 |
| Attack Precision | 0.75 |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| Deep Learning | PyTorch |
| Primary Model | Transformer (Attention-based) |
| Fallback Model | LSTM |
| Data Processing | Pandas, NumPy, Scikit-learn |
| Visualization / Dashboard | React.js / HTML+JS |
| Dataset | SWaT (Secure Water Treatment) |
| Deployment (planned) | Docker, Kubernetes, Apache Kafka, Apache Flink, Redis |

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/Chindhana06/Hydro_Vigil.git
cd Hydro_Vigil

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### requirements.txt (key dependencies)
```
torch>=2.0.0
numpy
pandas
scikit-learn
matplotlib
seaborn
```

---

## 🚀 How to Use

### 1. Prepare Your Data
Place your sensor data CSV file in the `data/` directory. The system expects time-series data with sensor readings (pressure, flow rate, water level, etc.).

```
data/
└── your_sensor_data.csv
```

### 2. Preprocess & Train
```bash
python train.py --data data/your_sensor_data.csv --window 100 --stride 10
```

### 3. Run Anomaly Detection
```bash
python detect.py --data data/your_sensor_data.csv --model saved_models/transformer.pt
```

### 4. Launch Dashboard
```bash
# Navigate to the dashboard directory
cd dashboard
# Open index.html in your browser
# OR serve it locally
python -m http.server 8000
```

### 5. Simulate a Cyber Attack (for testing)
On the dashboard, click **"Simulate Coordinated Attack"** to run a progressive anomaly lifecycle simulation and observe the detection pipeline in action.

---

## 📂 Dataset

HydroVigil is trained and evaluated on the **SWaT (Secure Water Treatment) Dataset** — an industry-standard benchmark for water infrastructure cybersecurity research.

- **Source:** iTrust, Singapore University of Technology and Design (SUTD)
- **Access:** [Request here](https://itrust.sutd.edu.sg/itrust-labs_datasets/dataset_info/)
- **Features:** 51 sensors and actuators across 6 stages of water treatment
- **Train windows shape:** `(138700, 100, 44)`
- **Test windows shape:** `(144162, 100, 44)`

> ⚠️ The SWaT dataset requires a formal request to SUTD. It is not included in this repository.

---

## 🛡️ Fault Tolerance

HydroVigil includes a built-in **Adaptive Resilience Layer**:

| Metric | Value |
|--------|-------|
| False Prediction Rate | 16.7% |
| Recovery Success Rate | 66.7% |
| Countermeasure Reuse Hit | 100% |
| Fallback Activations | ~3% of scenarios |
| Mean Mitigation Time | 38s |

### How it works:
- False alarms are logged with timestamp, sensor ID, anomaly score, threshold, and model version
- Root cause and resolution are recorded in an **error database** for audit tracking
- Logged countermeasures are **reused automatically** in future similar scenarios
- Cases are fed back into retraining and threshold tuning for continuous improvement

---

## 💼 Business Model

HydroVigil is designed for real-world deployment across three tiers:

- 🏘️ **Small Utilities** (Panchayats, small towns) — SaaS subscription at ₹5,000–₹15,000/month
- 🏭 **Industrial Plants** (Food, pharma, manufacturing) — On-premise license at ₹2L–₹10L one-time
- 🏛️ **Government / Municipal** (Water boards, smart cities) — Enterprise contract + maintenance at ₹25L–₹1Cr/year

### Scalability Roadmap
| Phase | Timeline | Goal |
|-------|----------|------|
| Phase 1 | Now | Pilot with 1–2 water utilities |
| Phase 2 | 6 months | SaaS MVP, 10+ utilities, ₹10L–₹20L ARR |
| Phase 3 | 1 year | Government contracts, Smart City integrations, ₹1Cr+ ARR |

---

## 👩‍💻 Team — SHE CORE

| Name | Branch | College |
|------|--------|---------|
| Chindhana K | B.E. EEE, 3rd Year | SSN College of Engineering |
| Harshini Ganga TS | B.E. ECE, 3rd Year | SSN College of Engineering |
| Vijaya Lakshmi M | B.Tech IT, 3rd Year | SSN College of Engineering |

---


<p align="center">
  Made with 💧 by Team SHE CORE · SSN College of Engineering
</p>

