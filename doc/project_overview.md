# Head Gesture Recognition System — Project Overview

> **Course:** Edge AI (IISc, Semester 2)  
> **Project Type:** Embedded TinyML — Real-Time Head Gesture Classification  
> **Target Platform:** Arduino Nicla Vision (×2)

---

## 1. Problem Statement & Motivation

Many elderly and differently-abled individuals have severely limited mobility but retain voluntary head movement. This project builds an **assistive communication device** that recognises six distinct head gestures (plus an idle state) and translates them into meaningful messages displayed on an OLED screen, accompanied by audible buzzer alerts — all running in **real-time on constrained edge hardware** without any cloud dependency.

---

## 2. System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          HEAD-MOUNTED WEARABLE                           │
│                                                                          │
│   LEFT TEMPLE                               RIGHT TEMPLE                 │
│ ┌───────────────┐    Wi-Fi UDP (6000)    ┌───────────────┐              │
│ │  Nicla Vision │ ─────────────────────► │  Nicla Vision │              │
│ │  (SLAVE)      │                        │  (MASTER)     │              │
│ │  LSM6DSRX IMU │                        │  LSM6DSRX IMU │              │
│ │  ax2,ay2,az2  │                        │  ax1,ay1,az1  │              │
│ │  gx2,gy2,gz2  │                        │  gx1,gy1,gz1  │              │
│ └───────────────┘                        │               │              │
│                                          │  ┌──────────┐ │              │
│                                          │  │ TinyML   │ │              │
│                                          │  │ (EdgeImp)│ │              │
│                                          │  └──────────┘ │              │
│                                          │  SSD1306 OLED │              │
│                                          │  Buzzer D2    │              │
│                                          └───────────────┘              │
│                                                │ Wi-Fi UDP (5005)       │
│                                                ▼                         │
│                                           PC / Laptop                    │
│                                        (Data_receive.py)                 │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions
| Decision | Rationale |
|---|---|
| **Dual IMU (12-axis)** | Single IMU insufficient for left-tilt vs right-tilt disambiguation; two sensors provide bilateral head motion context |
| **Wi-Fi UDP** | Low-latency, connectionless; suitable for real-time streaming at 50 Hz on MicroPython |
| **Edge Impulse** | Handles spectral feature extraction + Keras model training pipeline; exports Arduino-ready `.zip` library |
| **TinyML on-board** | Zero latency, zero connectivity requirement for end-user deployment |
| **SSD1306 OLED + Buzzer** | Dual feedback (visual + audio) for users who may have visual or hearing impairments |

---

## 3. Hardware Components

| Component | Role | Interface | Qty |
|---|---|---|---|
| **Arduino Nicla Vision** | Microcontroller + Wi-Fi (STM32H747) | — | 2 |
| **LSM6DSRX IMU** | 3-axis Accelerometer + 3-axis Gyroscope | SPI (`SPI(5)`, CS=`PF6`) | 2 (built-in) |
| **SSD1306 OLED (128×64)** | Visual gesture feedback display | I2C | 1 (on Master) |
| **Active Buzzer** | Audio gesture alert | Digital `D2` | 1 (on Master) |
| **Headband** | Mechanical mount at left/right temples | — | 1 |

---

## 4. Gesture Vocabulary

| # | Gesture | OLED Message | Buzzer Pattern | Semantic Meaning |
|---|---|---|---|---|
| 1 | **Nod (Up-Down)** | `I AM OK` | 1 short beep | Affirmation / Yes |
| 2 | **Head Shake (Side-to-Side)** | `NO / HELP` | 2 short beeps | Negation / Assistance call |
| 3 | **Tilt Left** | `NEED WATER` | 1 long beep | Hydration request |
| 4 | **Tilt Right** | `NEED HELP` | 3 short beeps | General distress |
| 5 | **Look Up** | `EMERGENCY` | Continuous beep | Critical / life-safety alert |
| 6 | **Look Down** | `CALL NURSE` | 3 fast beeps | Medical assistance |
| 7 | **Idle** | *(no display)* | Silent | No gesture / resting |

---

## 5. Software Architecture

### 5.1 Firmware — `slave.py` (Left Nicla Vision)
- Connects to Wi-Fi (SSID: `Parthibg60`)
- Reads LSM6DSRX via SPI at **50 Hz** (`TARGET_PERIOD = 20 ms`)
- Packs 6 floats `[ax2, ay2, az2, gx2, gy2, gz2]` into a comma-separated UDP datagram
- Sends to Master IP on **port 6000**

### 5.2 Firmware — `master.py` (Right Nicla Vision)
- Connects to the same Wi-Fi network
- Reads its own IMU at 50 Hz: `[ax1, ay1, az1, gx1, gy1, gz1]`
- Receives slave data from UDP port 6000 (non-blocking; reuses last known value if no packet arrives)
- Constructs a **13-field** datagram: `[timestamp_ms, ax1..gz1, ax2..gz2]`
- Streams to PC on **port 5005** for data collection
- After model deployment: runs **TinyML inference** and drives OLED + Buzzer outputs

### 5.3 Data Collection — `Data_receive.py` (PC/Laptop)
- Listens on UDP port 5005 (`0.0.0.0:5005`)
- Prompts user for an activity label (e.g., `1_Nod`)
- Records for `DURATION_SECONDS = 250` seconds (can be stopped early with Ctrl+C)
- Saves timestamped CSV: `<activity>_<YYYYMMDD_HHMMSS>.csv`
- **CSV Schema:** `timestamp, ax1, ay1, az1, gx1, gy1, gz1, ax2, ay2, az2, gx2, gy2, gz2, activity`

---

## 6. Dataset

### 6.1 Data Collection Summary

Dataset location: `dataset/imu_data/`

| Gesture Class | Files Collected | Collectors | Approx. Total Rows |
|---|---|---|---|
| `1_Nod` | 3 main files | Abha, Adarsh, Parthib | ~21,000+ |
| `2_Head_Shake` | 4 files | Abha, Adarsh, Parthib, Maitreyi | ~23,000+ |
| `3_Tilt_Left` | 4 files | Abha, Adarsh, Parthib, Maitreyi | ~25,000+ |
| `4_Tilt_Right` | 4 files | Abha, Adarsh, Parthib, Maitreyi | ~25,000+ |
| `5_Look_Up` | 4 files | Abha, Adarsh, Parthib, Maitreyi | ~24,000+ |
| `6_Look_Down` | 4 files | Abha, Adarsh, Parthib, Maitreyi | ~26,000+ |
| `7_Idle` | 4 files | Abha, Adarsh, Parthib, Maitreyi | ~24,000+ |

> **Note:** Several `test_*.csv` files are also present — these are calibration/sanity-check recordings and should be excluded from model training.

### 6.2 CSV File Naming Convention

```
<class_index>_<GestureName>_<CollectorName>_<YYYYMMDD>_<HHMMSS>.csv
```

**Example:** `1_Nod_Abha_20260410_163845.csv`

### 6.3 Data Schema

```
timestamp  : int   — Board millisecond tick (from time.ticks_ms())
ax1, ay1, az1 : float — Master board accel (g), axes X/Y/Z
gx1, gy1, gz1 : float — Master board gyro (°/s), axes X/Y/Z
ax2, ay2, az2 : float — Slave board accel (g), axes X/Y/Z
gx2, gy2, gz2 : float — Slave board gyro (°/s), axes X/Y/Z
activity   : str   — Class label (e.g., "1_Nod_Abha")
```

### 6.4 Sampling Rate & Data Density
- **Target rate:** 50 Hz (20 ms period per sample)
- A 250-second recording yields ~**12,500 rows** per session
- Larger files (~849 KB, ~6,245 rows — e.g., `1_Nod_Abha`) represent edited/trimmed sessions
- Multiple collectors (Abha, Adarsh, Parthib, Maitreyi) ensure **subject diversity** for generalisation

---

## 7. ML Pipeline — Edge Impulse

### 7.1 Data Upload
- CSV files are uploaded to [Edge Impulse Studio](https://studio.edgeimpulse.com/)
- Each column is mapped: `ax1..gz2` → input features, `activity` → label

### 7.2 Impulse Design
| Parameter | Value |
|---|---|
| **Window Size** | 2000 ms (100 samples @ 50 Hz) |
| **Window Increase** | 200 ms |
| **Processing Block** | Spectral Analysis (FFT-based) |
| **Learning Block** | Keras (Dense classifier) / TFLite |

### 7.3 Spectral Analysis Block
- Computes **FFT magnitude + spectral power** per axis for each 2-second window
- Input to classifier: flattened spectral features from all 12 axes

### 7.4 Classifier Architecture (Keras)
- Dense layers with ReLU activations → Softmax output over 7 classes
- Optimised for deployment on STM32H747 (FPU available)

### 7.5 Deployment
- Model exported as **Arduino library** (`.zip`)
- Library added to Arduino IDE / MicroPython environment on the Master board
- Inference time target: **15–40 ms** (achievable on STM32H747)
- Accuracy target: **≥ 88%**

---

## 8. Project Phases (Workflow)

```
Phase 1: Hardware Setup
  └── Mount Nicla Vision boards on headband (left/right temples)
  └── Wire OLED to Master via I2C
  └── Wire Buzzer to Master D2

Phase 2: Data Collection
  └── Flash slave.py → Slave board
  └── Flash master.py → Master board (streaming mode)
  └── Run Data_receive.py on PC
  └── Collect 250s sessions per gesture, per person

Phase 3: Model Training (Edge Impulse)
  └── Upload CSVs → Create Impulse
  └── Spectral Analysis → Keras model
  └── Train & evaluate (target ≥88% accuracy)
  └── Export as Arduino library (.zip)

Phase 4: Deployment
  └── Install exported library on Master
  └── Update master.py to run inference loop
  └── Drive OLED & Buzzer based on prediction

Phase 5: Testing & Validation
  └── Live gesture testing
  └── Measure inference latency (target 15–40 ms)
  └── Edge-case & robustness testing
```

---

## 9. Real-Time Inference Flow (Deployed)

```
Every 20ms (Master Board):
  1. Read own IMU → [ax1, ay1, az1, gx1, gy1, gz1]
  2. Receive UDP from Slave → [ax2, ay2, az2, gx2, gy2, gz2]
  3. Append 12-value sample to sliding window buffer (2000ms = 100 samples)
  4. When window is full:
       a. Run Spectral Analysis (FFT)
       b. Run Keras/TFLite inference
       c. Get predicted class label
       d. Update OLED display with message
       e. Trigger Buzzer with appropriate pattern
  5. Slide window by 200ms, repeat
```

---

## 10. Communication Protocol Details

### Wi-Fi Network
- **SSID:** `Parthibg60`
- **Authentication:** WPA2 (`Parthib123`)
- Boards communicate over LAN; no internet required

### UDP Packet Format

| Direction | Source | Destination | Port | Payload Format |
|---|---|---|---|---|
| Slave → Master | Slave IP | Master IP (`10.91.132.16`) | 6000 | `ax2,ay2,az2,gx2,gy2,gz2` (6 floats, comma-sep.) |
| Master → PC | Master IP | PC IP (`10.91.132.79`) | 5005 | `ts,ax1,ay1,az1,gx1,gy1,gz1,ax2,ay2,az2,gx2,gy2,gz2` (13 values) |

---

## 11. Output Feedback Details

### OLED Display (SSD1306, I2C)
- 128×64 pixels
- Displays large text corresponding to the detected gesture
- Cleared automatically upon detecting a new gesture

### Buzzer Patterns (Active Buzzer on D2)
| Gesture | Pattern |
|---|---|
| Nod | 1 short beep (100ms) |
| Head Shake | 2 × short beep (100ms ON, 100ms OFF) |
| Tilt Left | 1 long beep (500ms) |
| Tilt Right | 3 × short beep (100ms ON, 100ms OFF) |
| Look Up | Continuous beep (until next gesture) |
| Look Down | 3 × fast beep (50ms ON, 50ms OFF) |
| Idle | Silent |

---

## 12. Known Issues & Troubleshooting Notes

| Issue | Likely Cause | Fix |
|---|---|---|
| Model confused between Tilt Left and Tilt Right | Single-axis dominance in single-IMU system | Dual-IMU design mitigates this; collect more diverse data |
| Slave data lag / stale readings | UDP packet loss on Wi-Fi | Master reuses `last_slave` values; acceptable at 50 Hz |
| OLED not updating | I2C address mismatch or wiring | Verify address (0x3C or 0x3D) with I2C scanner |
| Low accuracy (<88%) | Insufficient data diversity | Collect from more subjects and gesture styles |
| High inference latency (>40ms) | Model too large | Reduce dense layer size; apply quantisation (INT8) |

---

## 13. Future Enhancements (Suggested)

- **Bluetooth / Wi-Fi remote alerts:** Notify caregivers on a mobile app when EMERGENCY or CALL NURSE gestures are detected
- **Speech Synthesis Module:** Add a small speaker to vocally announce the detected command (e.g., "NEED WATER")
- **Personalised re-training:** Allow per-user fine-tuning directly on-device using continual learning
- **Battery & form factor:** Integrate a Li-Po battery and custom 3D-printed headband for standalone wearable use
- **Expand gesture vocabulary:** Add chin-drop, forward-nod, rotational gestures for richer communication
- **On-device confidence display:** Show prediction confidence % on OLED to help users calibrate their gestures

---

## 14. Directory Structure

```
edgeAI_project/
├── head_gesture_system.pdf       ← Project specification document (17 pages)
├── doc/
│   └── project_overview.md       ← This file
├── EDGE AI Project/
│   ├── CODE FILES/
│   │   ├── master.py             ← MicroPython firmware for Master (Right) Nicla Vision
│   │   └── slave.py              ← MicroPython firmware for Slave (Left) Nicla Vision
│   ├── Data_receive.py           ← PC-side UDP data collection script
│   ├── datacheck.ipynb           ← Jupyter notebook for dataset inspection/verification
│   ├── test.py                   ← Quick connectivity/sanity test script
│   └── test1.py                  ← Extended test script
└── dataset/
    └── imu_data/                 ← Collected gesture CSV files (34 files, 7 classes × ~4 subjects)
        ├── 1_Nod_*.csv           ← Class 1: Nod gesture recordings
        ├── 2_Head_Shake_*.csv    ← Class 2: Head shake recordings
        ├── 3_Tilt_Left_*.csv     ← Class 3: Tilt left recordings
        ├── 4_Tilt_Right_*.csv    ← Class 4: Tilt right recordings
        ├── 5_Look_Up_*.csv       ← Class 5: Look up recordings
        ├── 6_Look_Down_*.csv     ← Class 6: Look down recordings
        ├── 7_Idle_*.csv          ← Class 7: Idle (no gesture) recordings
        └── test_*.csv            ← Calibration/test files (exclude from training)
```

---

## 15. Team Members (Inferred from Dataset)

| Name | Role |
|---|---|
| **Abha** | Data collection, project lead |
| **Adarsh** | Data collection |
| **Parthib** | Data collection |
| **Maitreyi** | Data collection |

---
