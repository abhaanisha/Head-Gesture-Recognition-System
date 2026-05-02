<div align="center">

# 🧠 Head Gesture Recognition System
### TinyML-Based Assistive Communication for Elderly & Disabled Individuals

[![IISc](https://img.shields.io/badge/IISc-Edge_AI_Course-blue?style=for-the-badge)](https://iisc.ac.in)
[![Course](https://img.shields.io/badge/CP_330-Edge_AI-purple?style=for-the-badge)](https://www.samy101.com/edge-ai-25/projects/18-blind-assistance/)
[![Platform](https://img.shields.io/badge/Platform-Arduino_Nicla_Vision-teal?style=for-the-badge)](https://store.arduino.cc/products/nicla-vision)
[![TensorFlow Lite](https://img.shields.io/badge/TensorFlow-Lite_INT8-orange?style=for-the-badge&logo=tensorflow)](https://www.tensorflow.org/lite)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Course:** CP 330 — Edge AI &nbsp;|&nbsp; **Instructor:** Prof. Pandarasamy Arjunan &nbsp;|&nbsp; Indian Institute of Science, Bangalore

*A real-time, cloud-free gesture recognition system that translates head movements into meaningful messages — running entirely on a wearable microcontroller.*

[![Presentation Video](https://img.shields.io/badge/Google%20Drive-Watch%20Presentation-4285F4?style=for-the-badge&logo=google-drive&logoColor=white)](https://drive.google.com/file/d/1__JJ69PBDf3QR5xZBZMHhklWdVlq01Ug/view?usp=drivesdk)
[![Demo Video](https://img.shields.io/badge/▶_Watch_Demo-SharePoint-0078D4?style=for-the-badge&logo=microsoft)](https://indianinstituteofscience-my.sharepoint.com/:v:/g/personal/abhas_iisc_ac_in/IQCmHS_j7puyQ6OWcKqMe5GkAeruAGz5R6FupJL88lnMZLk?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=pOxfAL)


</div>


## 1. Problem Statement

Many elderly and differently-abled individuals have severely limited hand mobility but retain **voluntary head movement**. This project builds a wearable assistive communication device that:

- Recognises **6 distinct head gestures** (+ an idle state)
- Translates them into messages displayed on an **OLED screen**
- Triggers **audible buzzer alerts** for each gesture type
- Runs entirely **on-device** — no cloud, no smartphone required

> **Why head gestures?** Conditions like ALS, post-stroke paralysis, and spinal cord injuries frequently spare cranial nerve-controlled neck muscles while eliminating hand mobility. Head movement is thus a reliable, low-fatigue communication channel available to this population.

---

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Dual IMU (12-axis)** | Single IMU cannot reliably distinguish Tilt Left vs Tilt Right; bilateral sensors provide asymmetry-based discrimination |
| **Wi-Fi UDP** | Low-latency, connectionless — ideal for real-time 50 Hz streaming on MicroPython |
| **TinyML On-Board** | Zero cloud dependency, zero latency |
| **OLED + Buzzer** | Dual feedback (visual + audio) to Alert the caregiver in case of an emergency |

---

### System Overview

<div align="center">
<img src="doc/Figure/System_flow_diagram.png" alt="System Flow Diagram" width="480"/>
<br><em>End-to-end system flow from head movement to feedback output</em>
</div>

## 2. Hardware Setup

<div align="center">
<img src="doc/Figure/Head Sensor Placement Diagram.png" alt="Sensor Placement" width="480"/>
<br><em>Dual Nicla Vision boards mounted at left and right temples</em>
</div>

### Physical Setup

<table>
<tr>
<td align="center"><img src="doc/Figure/Setup_image_1.jpeg" alt="Setup Photo 1" width="360"/><br><em>Physical hardware setup — side view</em></td>
<td align="center"><img src="doc/Figure/Setup_image_2.jpeg" alt="Setup Photo 2" width="360"/><br><em>Wearable headband with both Nicla Vision boards mounted</em></td>
</tr>
</table>

<br>

### Bill of Materials

| Component | Role | Interface | Qty |
|---|---|---|---|
| *Arduino Nicla Vision* | MCU (STM32H747) + Wi-Fi + IMU | — | 2 |
| *LSM6DSRX IMU* | 3-axis Accel + 3-axis Gyro (built-in on Nicla) | SPI | 2 (built-in) |
| *Arduino UNO R4 WiFi* | Output controller — OLED + Buzzer | Wi-Fi UDP | 1 |
| *SSD1306 OLED (128×64)* | Visual gesture feedback | I2C (0x3C) | 1 |
| *Active Buzzer* | Audio gesture alert | Digital pin 9 | 1 |
| *Wearable Cap* | Temple mounting frame for Nicla boards | — | 1 |

### Pin Connections — Arduino UNO R4 WiFi

| Component | Signal | UNO R4 Pin |
|---|---|---|
| SSD1306 OLED | SDA | A4 |
| SSD1306 OLED | SCL | A5 |
| SSD1306 OLED | VCC | 3.3V |
| SSD1306 OLED | GND | GND |
| Active Buzzer | Signal | Digital 9 |
| Active Buzzer | GND | GND |

---

## 3. Gesture Vocabulary

The system recognises 7 states (6 gestures + idle):

| # | Gesture | OLED Display | Buzzer | Description |
|---|---|---|---|---|
| 1 | *Nod* | Class: 1 · Nod | 1 beep (150 ms) | Affirmation / Yes |
| 2 | *Head Shake* | Class: 2 · Head_Shake | 1 beep (150 ms) | Negation / No |
| 3 | *Tilt Left* | Class: 3 · Tilt_Left | 1 beep (150 ms) | Left tilt detected |
| 4 | *Tilt Right* | Class: 4 · Tilt_Right | 1 beep (150 ms) | Right tilt detected |
| 5 | *Look Up* | Class: 5 · Look_Up | 1 beep (150 ms) | Upward head motion |
| 6 | *Look Down* | Class: 6 · Look_Down | 1 beep (150 ms) | Downward head motion |
| 7 | *Idle* | Waiting for Gesture... | Silent | No gesture / resting |

---

## 4. Software Architecture

### 4.1 Data Collection Pipeline
- **Slave Nicla (`slave_datacollection.py`)**: Streams 6-axis IMU data to the Master via UDP (port 6000) at 50 Hz.
- **Master Nicla (`master_datacollection.py`)**: Merges its own 6-axis IMU data with the Slave's data and streams a combined 13-value packet to the PC via UDP (port 5005).
- **PC (`Data_receive.py`)**: Records the UDP stream and saves it into timestamped CSV files for model training.

### 4.2 Inference Pipeline
- **Slave Nicla (`slave.py`)**: Connects to Wi-Fi and continuously streams 6-axis IMU data to the Master via UDP at 50 Hz.
- **Master Nicla (`master.py`)**:
  - Maintains a 20-sample sliding window to extract 113 features (stats & cross-IMU).
  - Runs a native Python `m2cgen` Decision Tree for real-time 7-class gesture recognition.
  - Applies a 5-sample majority vote smoothing to filter out noise.
  - Broadcasts recognised gestures to the PC (port 5005) and Arduino UNO R4 (port 5006) via UDP.

### 4.3 Output & Monitoring
- **Arduino UNO R4 WiFi (`arduino_uno.ino`)**: Listens on port 5006. Updates an I2C OLED display and triggers an active buzzer only when the gesture changes.
- **PC Monitor (`streamlit_app.py`)**: Listens on port 5005. Applies a stricter 50-sample (95% threshold) majority vote smoothing. It triggers voice feedback (Windows TTS) and sends push notifications to caregivers via `ntfy.sh` with a 15-second cooldown.

---

## 5. Dataset

### Collection Summary
- **Total Samples:** Over 20k samples per class, totaling ~140,000 samples
- **Sampling Rate:** 50 Hz (20 ms period)
- **Session Duration:** ~250 seconds per recording
- **Multi-subject diversity:** multiple collectors with different gesture amplitudes and head sizes
- `test_*.csv` files are calibration recordings — excluded from training


---

## 6. ML Pipeline & Feature Engineering

<div align="center">
<img src="doc/Figure/Machine Leaning Pipeline Diagram.png" alt="ML Pipeline" width="700"/>
<br><em>5-stage ML pipeline from data collection to Arduino deployment</em>
</div>

<br>

<div align="center">
<img src="doc/Dual-IMU_Feature_Engineering.png" alt="Feature Engineering Pipeline" width="780"/>
<br><em>Dual-IMU feature engineering: 148-dimensional feature vector from a 1-second window</em>
</div>

### Feature Engineering

The feature pipeline operates on **1-second sliding windows** (50 samples @ 50 Hz) with **50% overlap**:

#### Group 1 — Per-Channel Statistical Features (132 features)
11 statistics × 12 IMU channels (ax1, ay1, az1, gx1, gy1, gz1, ax2, ay2, az2, gx2, gy2, gz2):

| Feature | Description |
|---|---|
| `mean` | Average value (DC offset, bias direction) |
| `std` | Standard deviation (motion spread) |
| `min` / `max` | Peak excursion |
| `var` | Variance (energy of fluctuation) |
| `rms` | Root mean square (total motion magnitude) |
| `energy` | Sum of squares (total signal power) |
| `iqr` | Interquartile range (robust spread) |
| `median` | Robust central value |
| `skewness` | Asymmetry of motion profile |
| `kurtosis` | Peakedness (impulse-like vs. smooth) |

#### Group 2 — Spectral Features (12 features)
2 FFT features × 6 gyroscope channels (gx1, gy1, gz1, gx2, gy2, gz2):

| Feature | Description |
|---|---|
| `dominant_frequency` | Frequency bin with highest FFT magnitude (gesture tempo) |
| `spectral_entropy` | Distribution of spectral energy (periodic vs. irregular) |

#### Group 3 — Cross-IMU Symmetry Features (4 features)
> 🔑 **The key innovation** — designed specifically to discriminate Tilt Left vs Tilt Right, which appear identical to a single IMU.

| Feature | Formula | Physical Meaning |
|---|---|---|
| `cross_gx_mean_diff` | `mean(gx1) - mean(gx2)` | Roll asymmetry: sign flips between Tilt L and Tilt R |
| `cross_gx_rms_diff` | `rms(gx1) - rms(gx2)` | Energy-weighted roll asymmetry |
| `cross_gz_mean_diff` | `mean(gz1) - mean(gz2)` | Yaw asymmetry during tilts |
| `cross_gz_corr` | `Pearson(gz1, gz2)` | Bilateral synchrony: +1 = same direction, -1 = opposite |

During **Tilt Left**: `cross_gx_mean_diff < 0` (left temple dominant).  
During **Tilt Right**: `cross_gx_mean_diff > 0` (right temple dominant).

### Models Trained

| Model | Purpose |
|---|---|
| **Decision Tree** | Baseline + interpretable decision rules |
| **Random Forest** | Robust ensemble baseline |
| **Keras Dense MLP** | Primary model for TFLite deployment |

**Keras Architecture:**
```
Input (148) → Dense(128) + BN + Dropout(0.3)
            → Dense(64)  + BN + Dropout(0.3)
            → Dense(32)  + Dropout(0.2)
            → Dense(7, Softmax)

Total Parameters: 30,663  |  INT8 Size: ~33.6 KB
```

**Training Setup:**
- Split: 80% train / 20% test (stratified)
- Optimizer: Adam (lr=1e-3), Loss: Categorical Crossentropy
- Callbacks: EarlyStopping (patience=15), ReduceLROnPlateau, ModelCheckpoint

---

## 7. Model Results

<div align="center">

| Model | Test Accuracy |
|---|---|
| Decision Tree | **100.00%** |
| Random Forest | **100.00%** |
| **Keras TinyMLP** | **100.00%** |
| INT8 TFLite | **100.00%** |

</div>

**Dataset Summary:**
```
Raw samples loaded        : 141,751
Windows (50 samples, 50%) :   5,661
Feature dimensionality    :     150
```

<br>

The Decision Tree achieved **99.9%–100% test accuracy**, masterfully handling the 12-axis feature vector with a negligible memory footprint.

#### Classification Report — Decision Tree (Accuracy: 100.00%)

```text
Classification Report:
                  precision    recall  f1-score   support

         Nod       1.00      1.00      1.00       129
  Head_Shake       1.00      1.00      1.00       154
   Tilt_Left       1.00      1.00      1.00       169
  Tilt_Right       1.00      1.00      1.00       162
     Look_Up       1.00      1.00      1.00       163
   Look_Down       1.00      1.00      1.00       177
        Idle       1.00      1.00      1.00       179

    accuracy                           1.00      1133
   macro avg       1.00      1.00      1.00      1133
weighted avg       1.00      1.00      1.00      1133
```

![Confusion Matrix — Decision Tree](doc/Figure/Decision_tree_cm.png)

---



### Real-Time Inference Flow (on Master board)
```
Every 20ms:
  1. Read Master IMU  → [ax1, ay1, az1, gx1, gy1, gz1]
  2. Receive Slave UDP → [ax2, ay2, az2, gx2, gy2, gz2]
  3. Append 12-value sample to circular window buffer (50 samples)
  4. When window full:
       a. Extract 148 features (stats + spectral + cross-IMU)
       b. Apply StandardScaler normalisation
       c. Run TFLite INT8 inference  (~15–40 ms)
       d. argmax(softmax) → predicted gesture class
       e. Update OLED display
       f. Trigger Buzzer pattern
  5. Slide window by 25 samples (50% overlap), repeat
```

**Target inference latency:** 15–40 ms on STM32H747 Cortex-M7 @ 480 MHz

---

## 8. Repository Structure

```
Head-Gesture-Recognition-System/
│
├── README.md                          ← This file
├── report.md
├── model_development.ipynb            ← Full ML pipeline notebook for the deployed model
├── CNN_Code_Files/
│   ├── CNN_Model_Development.ipynb        ← CNN development code[end-to-end-pipeline](also contains pruning, PQT and QAT)
|   ├──CNN_master_deployment.py
│   └── CNN_slave_deployment.py    
├── Model_deployment_Final/
│   ├── master.py                      ← MicroPython: Master Nicla Vision (Right)
│   └── slave.py                       ← MicroPython: Slave Nicla Vision (Left)
|   └── streamlit_PC_Side.py
|   └── Arduino_Uno_R4_wifi/
|      └──Arduino_Uno_R4_wifi.ino
|
├── data_collection/       ← Data collection script and the collected data
│   └── master.py               
|   └── slave.py
|   └── imu_data/          ← Collected data
│    └── imu_data/                      ← Raw CSV recordings (7 gesture classes)
│       ├── 1_Nod_*.csv
│       ├── 2_Head_Shake_*.csv
│       ├── 3_Tilt_Left_*.csv
│       ├── 4_Tilt_Right_*.csv
│       ├── 5_Look_Up_*.csv
│       ├── 6_Look_Down_*.csv
│       └── 7_Idle_*.csv
|
├── feature_order.json                 ← Feature vector ordering for inference
│
├── model_output/
|   ├── eda_overview.png               ← EDA visualisation
│   ├── cm_*.png                       ← Confusion matrices
│   ├── training_curves.png            ← Accuracy/loss curves
|   ├── learning_curves.png            ← Accuracy/loss curves
│   ├── tsne_features.png              ← Feature space t-SNE
│   └── feature_importance_rf.png      ← Feature importance
│
└── doc/
    ├── Figure/ ← Figures used in the report
```

---

## 9. Getting Started

### Prerequisites

```bash
# Python environment (tf_env or dl_env)
conda create -n tf_env python=3.9
conda activate tf_env
pip install tensorflow==2.10.1 scikit-learn pandas numpy scipy matplotlib seaborn joblib
```

### Step 1: Data Collection

1. Flash `firmware/slave.py` to the **Left** Nicla Vision
2. Flash `firmware/master.py` to the **Right** Nicla Vision (set to data collection mode)
3. Update Wi-Fi credentials and IP addresses in both scripts
4. Run the collection script on your PC:

```bash
python data_collection/Data_receive.py
```

### Step 2: Train the Model

Open and run the notebook:
```bash
jupyter notebook model_development.ipynb
```

Or run the standalone script:
```bash
conda run -n tf_env python train_model.py
```

Outputs will be saved to `model_output/`.

### Step 3: Deploy on Hardware

1. Copy `model_output/head_gesture_int8_model.h` to your Arduino firmware directory
2. Update `firmware/master.py` to inference mode (load TFLite model)
3. Flash updated `master.py` to the Master Nicla Vision
4. Wear the device and test live gesture recognition

> **Course:** CP 330 — Edge AI &nbsp;|&nbsp; **Instructor:** Prof. Pandarasamy Arjunan &nbsp;|&nbsp; Indian Institute of Science (IISc), Bangalore, Semester 2, 2026

---

## 10. References

[1] Gouwanda, D., & Senanayake, S. A. (2011). Identifying gait asymmetry using gyroscopes—A cross-correlation and Normalized Symmetry Index approach. *Journal of Biomechanics*, 44(5), 972–978.

[2] Ortega-Anderez, D., Lotfi, A., Langensiepen, C., & Appiah, K. (2019). A multi-level refinement approach towards the classification of quotidian activities using accelerometer data. *Journal of Ambient Intelligence and Humanized Computing*, 10(11), 4319–4330.

---

<div align="center">

**Built with ❤️ at IISc Bangalore**

*Making communication accessible for everyone*

</div>
