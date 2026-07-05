# HydroVigil
### AI-Powered Cyber Attack Detection for Smart Water Infrastructure

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=flat-square&logo=pytorch)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688?style=flat-square&logo=fastapi)
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
- [Results & Metrics](#-results--metrics)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [How to Use](#-how-to-use)
- [Dataset](#-dataset)
- [Fault Tolerance & Memory](#-fault-tolerance--memory)
- [Business Model](#-business-model)
- [Team](#-team)

---

## 🔍 Overview

**HydroVigil** is an AI-powered security monitoring system that detects cyber-attacks in real-time by analyzing time-series sensor data from water pipeline infrastructure. It integrates deep learning model inference (Transformer + LSTM Autoencoders) with a dynamic SCADA Digital Twin UI, providing operational visibility and automated fault containment for Smart Water Grids.

Unlike traditional static threshold-based systems, HydroVigil learns the **normal behavioral baseline** of the pipeline, computes dynamic statistical deviations, and engages local SQLite-backed countermeasure memories to neutralize threats.

---

## 🚨 Problem Statement

Water pipelines are critical national infrastructure. Modern SCADA/IoT deployments have expanded the attack surface:
- **Sophisticated Cyber-Attacks:** Malicious actors manipulate sensor inputs (like flow rate or pressure) to trigger overflows or bursts while keeping parameters just inside "normal" static thresholds.
- **Explainability Gap:** Security operators see alarms but lack statistical context regarding which sensors are affected, how anomalies propagate, or what remediation actions to take.
- **Response Latency:** Manual audit logging and mitigation lookups cause critical delays during active grid infiltration.

---

## 🏗️ Solution Architecture

```
                               ┌────────────────────────┐
                               │ Real-Time SWaT Stream  │
                               └───────────┬────────────┘
                                           │
                                           ▼ (WS Telemetry)
                               ┌────────────────────────┐
                               │  FastAPI Backend Core  │
                               └───────────┬────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼ (Transformer Anomaly Pipeline)              ▼ (Explainability Engine)
         ┌─────────────────────┐                       ┌─────────────────────────────┐
         │ Positional Encoding │                       │ Reconstruction Z-Score (zR) │
         └──────────┬──────────┘                       ├─────────────────────────────┤
                    │                                  │ Temporal Discrepancy (zA)   │
                    ▼                                  ├─────────────────────────────┤
         ┌─────────────────────┐                       │ Row Entropy Variance (zE)   │
         └──────────┬──────────┘                       ├─────────────────────────────┤
                    │                                  │ Max Anomaly Channel Mapping │
                    ▼                                  └──────────────┬──────────────┘
         ┌─────────────────────┐                                      │
         │ Multi-Head Attention│                                      │
         └──────────┬──────────┘                                      │
                    │                                                 │
                    ▼                                                 │
         ┌─────────────────────┐                                      │
         │ Mahalanobis Score   ├──────────────────────────────────────┘
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐         Yes (zA > 3.0 or zE > 2.0)
         │  Fallback Check?    ├──────────────────────────────────────┐
         └──────────┬──────────┘                                      │
                    │ No                                              ▼ (Engage fallback)
                    ▼                                      ┌─────────────────────┐
         ┌─────────────────────┐                           │    LSTM Encoder     │
         │  Transformer Output │                           └──────────┬──────────┘
         └──────────┬──────────┘                                      │
                    │                                                 ▼
                    │                                      ┌─────────────────────┐
                    │                                      │    LSTM Decoder     │
                    │                                      └──────────┬──────────┘
                    │                                                 │
                    └──────────────────────┬──────────────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │  Fault Similarity DB   │ <───> [ database/faults.db ]
                               └───────────┬────────────┘
                                           │
                                           ▼ (JSON Socket Frame)
                               ┌────────────────────────┐
                               │  React Digital Twin    │
                               └────────────────────────┘
```

---

## 🤖 ML Model Details

HydroVigil utilizes a hybrid, confidence-based **Dual-Model Anomaly Core**:

### 1. Primary Model: Transformer Autoencoder
- **Architecture:** Linear spatial embedding mapper, Positional Encoding, and a 2-layer Multi-Head Attention encoder-decoder.
- **Scoring:** Calculates reconstruction loss and maps temporal correlation matrices to measure deviations in sequential dependencies.
- **Inputs:** Shape of `(1, 100, 44)` representing a 100-step time sliding window across 44 standardized SWaT sensor features.

### 2. Fallback Model: LSTM Autoencoder
- **Architecture:** 2-layer stacked LSTM encoder (hidden dimension `64`) and decoder.
- **Engagement Trigger:** Dynamically activated if the Transformer attention z-score ($z_A > 3.0$) or attention row entropy z-score ($z_E > 2.0$) drifts out of normal parameters. This ensures robust continuous monitoring even during temporal shift phases.

### 3. Anomaly Decision Logic (Mahalanobis Distance)
The reconstruction error vector is projected into a Mahalanobis space using the covariance inverse matrix:
$$D_M(x) = \sqrt{(x - \mu)^T \Sigma^{-1} (x - \mu)}$$
- **Decision:** Flags `ATTACK` if $D_M$ exceeds threshold $T_2$ (18.5), and `SUSPICIOUS` if it exceeds $T_1$ (9.2).

---

## 📊 Results & Metrics

| Metric | Score | Description |
|--------|-------|-------------|
| **Overall Accuracy** | **98.2%** | Overall window-level classification accuracy |
| **Normal F1-Score** | **0.99** | Detection accuracy for normal grid states |
| **Attack F1-Score** | **0.73** | Detection accuracy for coordinated attacks |
| **Attack Precision** | **0.75** | Positive predictive value for active threats |
| **Attack Recall** | **0.70** | Sensitivity to cyber-physical anomalies |

---

## 🛠️ Tech Stack

- **Backend Language:** Python 3.8+
- **Deep Learning Framework:** PyTorch
- **API Server & Routing:** FastAPI & Uvicorn (WebSockets)
- **Database:** SQLite (SQLAlchemy)
- **Frontend Framework:** React (Vite, Javascript)
- **UI & Animations:** Vanilla CSS, Tailwind CSS, Framer Motion
- **Icons System:** FontAwesome (react-icons/fa)

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Chindhana06/Hydro_Vigil.git
cd Hydro_Vigil
```

### 2. Set Up Python Virtual Environment
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install websockets
```

### 4. Install Frontend Packages
```bash
cd frontend
npm install
```

---

## 🚀 How to Use

To run the application locally, you must launch both the backend FastAPI server and the frontend Vite server:

### 1. Start the Backend API
Navigate to the root or backend directory and launch Uvicorn:
```bash
cd backend
python -m uvicorn app:app --reload --port 8000
```
*The backend API will run on `http://localhost:8000`. The WebSocket telemetry stream is exposed at `ws://localhost:8000/ws/telemetry`.*

### 2. Start the Frontend Dev Server
In a new terminal window, navigate to the frontend directory:
```bash
cd frontend
npm run dev
```
*Open `http://localhost:5173` in your browser.*

### 3. Operational Walkthrough
1. **Clearance Selection:** On the landing screen, select your command clearance level (Operator or SOC Admin).
2. **Real-time SCADA digital twin:** Observe the active fluid pipelines. The inlet pump spins, the pre-treatment tank level shifts dynamically, and telemetry readouts stream every 900ms.
3. **Simulate Attack:** Click **"Simulate Coordinated Attack"** on the control console. You will see:
   - Anomaly lines plotted in real time.
   - The SCADA digital twin blinking red around the targeted node.
   - The AI Briefing displaying Reconstruction, Temporal, and Entropy Z-Scores along with the identified sensor ID.
4. **Audit Logging (Admin Only):** Click **"Download SOC Audit Report"** to export a structured text file containing all logged threat mitigation logs.

---

## 🌐 Production Deployment

For production deployments, the system is designed to host the backend and frontend separately to support persistent socket communication:

### 1. Backend Deployment (Render)
The FastAPI backend runs on **Render** as a Python Web Service:
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **CORS Settings:** Automatically configured to accept client WebSocket connections from Vercel hosting origins.

### 2. Frontend Deployment (Vercel)
The React dashboard runs on **Vercel** as a Vite Web Application:
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`
- **Environment Variables:**
  - **Key:** `VITE_WS_URL`
  - **Value:** `wss://<your-render-service-name>.onrender.com/ws/telemetry` *(ensure secure `wss://` protocol is used)*
- **Crucial Build Hint:** Remember to trigger a **Redeploy** in the Vercel dashboard after adding or updating variables, so Vite can inject the values during the build phase.

---

## 📂 Dataset

HydroVigil is evaluated on the **Secure Water Treatment (SWaT) Dataset** — an industry-standard benchmark simulating a multi-stage water treatment facility.
- **Features:** 51 sensors (level LIT, flow FIT, pressure PIT) and actuators (valves, pumps).
- **Processing Window:** 100 timesteps of historical features mapping 44 attributes.
- > ⚠️ *Note: The SWaT raw dataset requires a formal access request to SUTD and is not distributed directly in this repository.*

---

## 🛡️ Fault Tolerance & Memory

HydroVigil implements a built-in **Resilience and Mitigation Database**:
- **SQLite Anomaly Log (`database/faults.db`):** When the backend detects a threat, it generates an anomaly signature based on the reconstruction statistics and checks the database.
- **Adaptive Reuse:** If a similar signature is found within threshold limits, it reuses the pre-authorized mitigation response (`"Reused from database"`).
- **Auto-Learning:** New anomaly signatures are stored dynamically (`"Stored for future reuse"`) to ensure immediate containment lookup on future iterations.

---

## 💼 Business Model

Designed for real-world deployment across municipal and industrial smart utilities:
- 🏘️ **Small Municipal Utilities:** SaaS cloud-managed telemetry monitoring.
- 🏭 **Industrial Production Plants:** On-premise private deployment licensing.
- 🏛️ **Smart Cities / Enterprise Contracts:** Multi-site grid integrations and 24/7 security service SLA contracts.

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
