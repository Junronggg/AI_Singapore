# 💧 Multi-Agent AI System for Anomaly Detection & Predictive Maintenance

## 📌 Overview

This project implements a **multi-agent AI system** for real-time monitoring of industrial water systems.  
It processes sensor data, detects anomalies, diagnoses root causes, predicts failure risks, and generates actionable recommendations.

> 🚀 Our goal is to move from **reactive monitoring → proactive and intelligent decision-making**.

---

## 🎯 Key Features

- 📡 Real-time data simulation using SWaT dataset  
- 🤖 Multi-agent intelligence pipeline (5 agents)  
- 🔍 Anomaly detection using Isolation Forest  
- 🧠 Root cause diagnosis via feature analysis  
- 📈 Predictive risk scoring  
- 🛠️ Decision support recommendations  
- 🌐 FastAPI backend for real-time APIs  
- 📊 Streamlit dashboard for visualization  

---

## 🧱 System Architecture
Data → Processing → Agents → Backend → Dashboard
### Multi-Agent Pipeline
Monitoring → Anomaly Detection → Diagnosis → Prediction → Decision

Each agent performs a specific task and passes structured outputs to the next stage.

---

## 🧠 Agents

### 1. Monitoring Agent
- Validates incoming data
- Detects missing or inconsistent values
- Uses rule-based checks and rolling statistics

---

### 2. Anomaly Detection Agent
- Model: **Isolation Forest**
- Trained on normal system behavior
- Outputs anomaly score for each data point

---

### 3. Root Cause Diagnosis Agent
- Identifies most abnormal features
- Ranks contributing sensor signals
- Infers likely causes (e.g., pressure drop, flow issues)

---

### 4. Predictive Maintenance Agent
- Converts anomaly signals into **risk scores**
- Estimates failure likelihood
- Enables proactive maintenance planning

---

### 5. Decision Support Agent
- Maps system state → recommended actions
- Generates operational suggestions:
  - inspection
  - maintenance
  - system isolation

---

## ⚙️ Data Pipeline

### Dataset
- SWaT (Secure Water Treatment) dataset
- 51 sensors, time-series data
- Includes normal + attack scenarios

### Processing Steps
- Data cleaning (missing values, duplicates)
- Normalization (z-score scaling)
- Feature engineering:
  - rolling statistics
  - rate of change
- Real-time simulation via data replay

---

## 🔗 Backend API (FastAPI)

### Endpoints

| Endpoint | Description |
|--------|------------|
| `/health` | Check system status |
| `/dashboard/latest` | Get latest system state |
| `/dashboard/history` | Get historical data |
| `/demo/start` | Start simulation |
| `/demo/stop` | Stop simulation |

---

## 📊 Frontend Dashboard (Streamlit)

- Real-time anomaly score chart  
- Risk score visualization  
- Incident summary  
- Root cause insights  
- Recommended actions  
- System status monitoring  

---

## 🚀 How to Run

### 1. Clone repository
```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start backend
```bash
uvicorn app:app --reload
```

### 4. Start frontend
```bash
streamlit run dashboard.py
```
