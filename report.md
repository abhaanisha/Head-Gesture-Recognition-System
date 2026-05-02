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

[![Demo Video](https://img.shields.io/badge/▶_Watch_Demo-SharePoint-0078D4?style=for-the-badge&logo=microsoft)](https://indianinstituteofscience-my.sharepoint.com/:v:/g/personal/abhas_iisc_ac_in/IQCmHS_j7puyQ6OWcKqMe5GkAeruAGz5R6FupJL88lnMZLk?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=pOxfAL)

</div>

---

## 📌 Table of Contents

1. Problem Statement, Motivation & Objectives
2. Proposed Solution
3. Hardware & Software Setup
4. Data Collection & Dataset Preparation
5. Model Design, Training & Evaluation
6. Model Compression & Efficiency Metrics
7. Model Deployment & On-Device Performance
8. System Prototype (Pictures / Figures)
9. Conclusions & Limitations
10. Future Work
11. Challenges & Mitigation
12. References
13. Team

---

## 1. Problem Statement, Motivation & Objectives
The loss of verbal and motor communication due to aging or neurological conditions (such as ALS or stroke) creates a profound barrier to independence. While voice assistants and touchscreens are common, they are often inaccessible to individuals with speech impairments or limited limb mobility. This project addresses the need for a hands-free, private, and intuitive communication interface that utilizes the "last mile" of motor control: head gestures.

The motivation behind this system is to provide a reliable "communication bridge" that works in real-time and protects user privacy. By moving the intelligence from the cloud to the **Edge**, we eliminate the risks of data exposure and the critical delays associated with network latency. This ensures that an emergency gesture (like "Head shake") is detected instantly, regardless of internet connectivity.

**Key Project Objectives:**
* Develop a robust data acquisition pipeline using dual IMU sensors to provide 12-axis spatial redundancy.
* **Evaluate and compare multiple machine learning paradigms (Traditional ML vs. Deep Learning) to identify the most efficient model for resource-constrained hardware.**
* Deploy an optimized, lightweight classifier (Decision Tree) that achieves high accuracy with minimal CPU and memory overhead.
* Minimize inference latency to ensure real-time responsiveness on the Arduino Nicla Vision.
* Integrate an end-to-end ecosystem including on-device feedback, a Streamlit monitoring dashboard, and mobile notifications.

---

## 2. Proposed Solution (Overview)
Our solution utilizes a head-mounted wearable that translates head motion into actionable alerts. The system processes data through a multi-stage pipeline:


1.  **Data Acquisition:** Dual Nicla Vision boards (Master-Slave) capture synchronized 12-axis IMU data at 50Hz.
2.  **Pre-processing:** Raw signals are cleaned, scaled using Z-score normalization, and sliced into 1.6-second temporal windows.
3.  **Edge Inference:** A localized model classifies the motion into one of seven activities. While 1D-CNNs were explored for research, a **Decision Tree Classifier** was chosen for deployment due to its superior efficiency-to-accuracy ratio.
4.  **Integrated Output:** Upon detection, the system triggers local feedback (Buzzer/OLED) and transmits results via UDP to a Streamlit dashboard and mobile app.
---
### System Overview

<div align="center">
<img src="doc/Figure/System Flow Diagram.png" alt="System Flow Diagram" width="480"/>
<br><em>End-to-end system flow from head movement to feedback output</em>
</div>

<br>

The system uses **two Arduino Nicla Vision boards** — one on each temple — forming a bilateral dual-IMU configuration:

```
┌─────────────────────────────────────────────────────────────┐
│                    HEAD-MOUNTED WEARABLE                    │
│                                                             │
│  LEFT TEMPLE                         RIGHT TEMPLE           │
│ ┌─────────────────┐   Wi-Fi UDP    ┌─────────────────┐     │
│ │  Nicla Vision   │ ─────────────► │  Nicla Vision   │     │
│ │  (SLAVE)        │   port 6000    │  (MASTER)       │     │
│ │  LSM6DSRX IMU   │                │  LSM6DSRX IMU   │     │
│ │  ax2,ay2,az2    │                │  ax1,ay1,az1    │     │
│ │  gx2,gy2,gz2    │                │  gx1,gy1,gz1    │     │
│ └─────────────────┘                │                 │     │
│                                    │  ┌───────────┐  │     │
│                                    │  │  TinyML   │  │     │
│                                    │  │ Inference │  │     │
│                                    │  └───────────┘  │     │
│                                    │  SSD1306 OLED   │     │
│                                    │  Buzzer (D2)    │     │
│                                    └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Dual IMU (12-axis)** | Single IMU cannot reliably distinguish Tilt Left vs Tilt Right; bilateral sensors provide asymmetry-based discrimination |
| **Wi-Fi UDP** | Low-latency, connectionless — ideal for real-time 50 Hz streaming on MicroPython |
| **TinyML On-Board** | Zero cloud dependency, zero latency, works in hospitals/rural areas without internet |
| **OLED + Buzzer** | Dual feedback (visual + audio) for users with visual or hearing impairments |

---
## 3. Hardware and Software Setup - Parthib will add
---

## 4. Data Collection & Dataset Preparation
*   **Data Source:** A custom dataset was hand-collected from multiple participants to ensure the model learned general motion patterns.
*   **Sample Size:** We recorded approximately 20,000 samples per activity class, resulting in a comprehensive dataset of ~140,000 samples.
*   **Class Distribution:** The data covers 7 activities: *Nod, Head Shake, Tilt Left, Tilt Right, Look Up, Look Down, and Idle.*
*   **Preprocessing Steps:**
    *   **Normalization:** Applied `StandardScaler` (fitted only on training data) to center Accelerometer and Gyroscope readings, making the model "Gravity-Invariant."
    *   **Segmentation:** Implemented a Sliding Window of 80 samples (1.6s) with a 40-sample (50%) overlap to ensure full gesture capture.
    *   **Labeling:** Used regex-based parsing to extract activity codes from filenames for supervised learning.

---

## 5. Model Design, Training & Evaluation
We performed a comparative study between traditional Machine Learning and Deep Learning architectures to find the best fit for the Arduino Nicla Vision.

### 5.1 Deployment Model: Decision Tree Classifier
The Decision Tree was selected as the primary deployment target. It provides a non-linear classification path that is extremely lightweight, consisting of a series of simple `if-else` logical branches that run nearly instantaneously on a microcontroller.
*   **Architecture:**: .
*   **Performance:** Achieved **99.9% - 100% test accuracy**, masterfully handling the 12-axis feature vector with a negligible memory footprint.
The evaluation metrics observed for Decision Tree model are:
### Decision Tree Accuracy: 100.00%

#### Classification Report

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

### 5.2 Research Model: 1D-Convolutional Neural Network (CNN)
As an advanced research path, we developed a 1D-CNN to capture the temporal "shape" of gestures.
### 5.2.1 **Initial Architecture:**  Split-Path CNN Architecture for IMU Gesture Recognition

#### Architectural Flowchart
```text
    A["Input\n(80 timesteps x 12 channels)\n6 Master IMU + 6 Slave IMU"] --> B["GaussianNoise (0.1)\nCorrupts data to prevent memorization"]
    
    B --> C["Conv1D Block 1\n64 filters, kernel=5, ReLU\nL2=0.005"]
    C --> D["BatchNorm"]
    D --> E["MaxPooling1D (pool=2)\nOutput: 38 x 64"]
    E --> F["Dropout (0.4)"]
    
    F --> G["Conv1D Block 2\n128 filters, kernel=5, ReLU\nL2=0.005"]
    G --> H["BatchNorm"]
    H --> I["MaxPooling1D (pool=2)\nOutput: 17 x 128"]
    I --> J["Dropout (0.4)"]
    
    J --> K["Branch A: GlobalAveragePooling1D\nCaptures POSTURE (gravity vector)\nOutput: 128"]
    J --> L["Branch B: Flatten\nCaptures MOTION (full waveform)\nOutput: 17 x 128 = 2176"]
    
    K --> M["Concatenate\nOutput: 128 + 2176 = 2304"]
    L --> M
    
    M --> N["Dense (64, ReLU)\nL2=0.005"]
    N --> O["Dropout (0.4)"]
    O --> P["Dense (7, Softmax)\nFinal Classification"]
    
    P --> Q["Output Classes:\n1. Nod\n2. Head Shake\n3. Tilt Left\n4. Tilt Right\n5. Look Up\n6. Look Down\n7. Idle"]
```


## Data Shape Flow

| Layer | Output Shape | Purpose |
|-------|-------------|---------|
| Input | (80, 12) | 1.6 sec window x 12 IMU channels |
| GaussianNoise | (80, 12) | Anti-overfitting noise injection |
| Conv1D (64) | (76, 64) | Detects local motion patterns |
| MaxPooling1D | (38, 64) | Downsamples, keeps peaks |
| Conv1D (128) | (34, 128) | Detects deeper features |
| MaxPooling1D | (17, 128) | Further downsampling |
| Branch A: GAP | (128) | Averages entire window - Gravity/Posture |
| Branch B: Flatten | (2176) | Preserves full timeline - Motion sequence |
| Concatenate | (2304) | Merges posture + motion |
| Dense (64) | (64) | Final decision logic |
| Dense (7) | (7) | Softmax probabilities |

## Why the Split?

The split into two branches is the core innovation of this architecture.

- *Branch A (GlobalAveragePooling)* answers: "On average, which way is gravity pulling?" This perfectly identifies static postures like Look Down, Look Up, and Idle.
- *Branch B (Flatten)* answers: "What was the exact sequence of movement over 1.6 seconds?" This perfectly identifies dynamic gestures like Nod, Head Shake, and Tilts.

By concatenating both branches, the Dense layer receives the best of both worlds and can make highly informed decisions.

### 5.2.2 **Optimized Architecture:** Sequential CNN Architecture for IMU Gesture Recognition

#### Architectural Flowchart
```text
    A["Input\n(80 timesteps x 12 channels)\n6 Master IMU + 6 Slave IMU"] --> B["GaussianNoise (0.1)\nAdds random noise to prevent memorization"]
    
    B --> C["Conv1D Block 1\n32 filters, kernel=3, ReLU\nScans 3-tick (60ms) patterns"]
    C --> D["Dropout (0.4)\nRandomly disables 40% of neurons"]
    
    D --> E["Conv1D Block 2\n64 filters, kernel=3, ReLU\nExtracts deeper features"]
    E --> F["Dropout (0.4)\nRandomly disables 40% of neurons"]
    
    F --> G["GlobalAveragePooling1D\nAverages entire window into\none value per filter\nOutput: 64"]
    
    G --> H["Dense (32, ReLU)\nFinal decision logic"]
    H --> I["Dense (7, Softmax)\nProbability per gesture class"]
    
    I --> J["Output Classes:\n1. Nod\n2. Head Shake\n3. Tilt Left\n4. Tilt Right\n5. Look Up\n6. Look Down\n7. Idle"]

```
## Data Shape Flow

| Layer | Output Shape | Parameters | Purpose |
|-------|-------------|------------|---------|
| Input | (80, 12) | 0 | 1.6 sec window x 12 IMU channels |
| GaussianNoise | (80, 12) | 0 | Anti-overfitting noise injection |
| Conv1D (32) | (78, 32) | 1,184 | Detects short motion patterns |
| Dropout (0.4) | (78, 32) | 0 | Prevents over-reliance on any filter |
| Conv1D (64) | (76, 64) | 6,208 | Extracts deeper temporal features |
| Dropout (0.4) | (76, 64) | 0 | Prevents over-reliance on any filter |
| GlobalAveragePooling1D | (64) | 0 | Compresses full window into posture summary |
| Dense (32) | (32) | 2,080 | Learns decision boundaries |
| Dense (7) | (7) | 231 | Softmax classification |
| *Total* | | *9,703* | |

## Key Design Decisions

- *No MaxPooling:* Uses GlobalAveragePooling1D instead, which preserves the gravity baseline signal rather than only keeping peak values.
- *No Flatten:* Avoids exploding the parameter count. Flatten would create a (76 x 64 = 4,864) vector feeding into Dense, massively increasing model size and overfitting risk.
- *No BatchNormalization:* Removed to prevent stripping the DC offset (gravity vector) which is critical for distinguishing static postures.
- *Small Filters (32/64):* Deliberately kept small to prevent memorization and to fit within Nicla Vision SRAM constraints.
- *Kernel Size 3:* Scans 3 consecutive timesteps (60ms at 50Hz), capturing rapid micro-movements within gestures.

### Training Setup
*   **Data Split:** Implemented a strict **File-Based Split** (80% Train, 20% Validation) to ensure that windows from the same recording never appeared in both sets, preventing "Data Leakage."
*   **Hyperparameters:** Optimizer: Adam (lr=0.001); Loss: Categorical Crossentropy; Batch Size: 32.
*   **Callbacks:** Used `EarlyStopping` to halt training when validation loss stopped improving, restoring the best weights.

### Evaluation Metrics
The model was evaluated on a 100% "Blind" Test Set of files never seen during training.
*   **Validation Accuracy:** ~85% - 90% (Realistic, non-overfit performance).
*   **Confusion Matrix:** Analyzed to ensure distinct gestures like "Tilt Left" were not confused with "Nods."
*   **Inference Speed:** Profiling confirmed an inference time of ~0.1ms per window, fitting comfortably within the hardware's real-time requirements. (WE NEED TO CHECK THIS)
---
 ## 6. Model Compression & Efficiency Metrics

To ensure the system remains responsive while handling dual-IMU streams and WiFi communication, we evaluated the efficiency of both our primary and research models. Our goal was to find the "Pareto Optimal" point—the best balance between high accuracy and low resource consumption.

### Techniques Used
*   **C++ Transpilation (Decision Tree):** For the deployed model, we converted the trained Decision Tree into a series of static C++ `if-else` branches using mc2gen. This eliminates the need for a heavy runtime engine (like TFLite), making it the most compressed form of logic possible.
*   **Post-Training Quantization (1D-CNN):** We applied **INT8 Quantization** to the CNN. This converted 32-bit floating-point weights into 8-bit integers, shrinking the model math to run on the microcontroller's integer hardware.
*   **Global Average Pooling (GAP):** In the CNN architecture, we used GAP to replace traditional Flattening layers. This reduced total parameters by ~90% before deployment, significantly lowering the RAM requirement.

### Comparative Efficiency Metrics
The following table compares the raw research model (CNN) against the optimized deployment model (Decision Tree):

| Model Approach | Model Size | Inference Latency | Accuracy | Memory Type |
| :--- | :--- | :--- | :--- | :--- |
| **1D-CNN (Float32)** |  153.3 KB | 0.4933 ms | 96.45 % | Needs TFLite RAM |
| **1D-CNN (INT8)** (QAT) |  17 KB | 0.1590 ms |84.10 % | Needs TFLite RAM |
| **1D-CNN (INT8)** (PQT) |  16.6 KB | 0.1072 ms |85.24 % | Needs TFLite RAM |
| **Decision Tree (Deployed)** | **1.52 KB** | **< 0.01 ms** | **100%** | **Static Flash** |

## 6. Model Compression & Efficiency Metrics

A critical phase of this project involved a comparative study between a high-performance "Heavy" CNN and an optimized "Edge-Ready" version. This allowed us to quantify the exact trade-offs required to fit deep learning intelligence onto the Arduino Nicla Vision hardware.

### Optimization Techniques
*   **Post-Training Quantization (PTQ):** We utilized 8-bit integer quantization to shrink the model size and accelerate inference on the microcontroller’s hardware.
*   **Quantization Aware Training (QAT):** We simulated the effects of 8-bit precision loss during the training phase to improve the robustness of the optimized model.
*   **Architectural Selection:** We moved from a heavy baseline architecture to a more serialized, filter-efficient design to minimize the static RAM footprint.

### Efficiency Comparison (CNN Research Path)
The table below tracks the metrics captured during our transition from the high-precision baseline to the deployment-ready quantized version:

| Metric | Heavy CNN Baseline | Optimized Quantized CNN | Improvement |
| :--- | :--- | :--- | :--- |
| **Model Size (KB)** | 2329.94 KB | **153 KB** | **~12x Smaller** |
| **Inference Time** | 0.2640 ms | **0.1072 ms** | **~2.5x Faster** |
| **Test Accuracy** | 95.66% | **85.34%** | -10.32% |

### Analysis and Final Deployment Strategy
Our initial "Heavy" CNN achieved an impressive accuracy of **95.66%**, but its **2.3 MB** size exceeded the 2 MB total Flash limit of the Nicla Vision (especially when considering the space required for OLED and WiFi drivers). While our optimization efforts successfully reduced the model size by over **11x**, with a good accuracy of 94% there were a lot of challenges encountered to deploy it on the Nicla. Some of which are:
* Memory Fragmentation crash: The Nicla crashed completely when trying to load the .tflite file. This happened because the Nicla has less than 500 KB of usable RAM. If we connect to the Wi-fi first, there is a scatter of small memory blocks all over that heap of memory and thus when a large model like CNN which is of around 200 KB tries to load, it cannot find a contagious block of RAM. To overcome this we had to restructure the code to load the model first and then connect to the Wi-fi
* Interpreter Compatibility Crash: By default, TensorFlow applies Per-Channel quantization to Dense layers. OpenMV's lightweight TFLite interpreter does not support this operation. The fix was to force compiler to use older simple math on colab
* WiFi Dropout: Nicla uses a single main processor to do both the CNN math and manage the WiFi connection. Thus while deploying a model like CNN it has do the inference mathematics and also Receive the packet sent. This Created a network bottleneck in the pipeline.

To overcome the problems caused by large model we trained a smaller model, as stated earlier, but we observed that due to our limited custom dataset, the CNN lacked enough diverse samples to maintain high precision after the significant data loss caused by 8-bit quantization. Consequently, we made the strategic decision to back off from deploying the CNN in the final prototype. Instead, we prioritized the **Decision Tree model**, as it maintained **100% accuracy** with an even smaller footprint, ensuring the most stable real-time behavior for the assistive device.

### Performance Visualizations
The following figures provide a visual breakdown of the trade-offs in size, speed, and accuracy across our various experimental architectures.

![Model Metrics:](doc/Figure/CNN_Base.png)
*Figure 3: Initial Architecture, Comparison of Model Size, Accuracy, and Latency between the Heavy Baseline and Quantized TFLite versions.*

![Optimization Strategy:](doc/Figure/CNN_optimized.png)
*Figure 4: Optimized Architecture and Performance impact of Post-Training Quantization (PTQ) and Quantization Aware Training (QAT) on model size and inference speed.*
Decision tree achieved 100% accuracy
![Optimization Strategy:](doc/Figure/Decision_tree_cm.png)
### Resource Utilization (On-Device Profiling)
*   **Memory (RAM):** 
    *   The **Decision Tree** uses negligible RAM as it runs as native code. 
    *   Choosing the Decision Tree allowed us to keep over **90% of the RAM free** for the OLED display buffers and the high-load UDP WiFi stack.
*   **Flash Storage:** Both models fit comfortably within the 2MB Flash, but the Decision Tree is so small it allows for the storage of extensive gesture-to-action lookup tables.

### Observed Trade-offs & Engineering Decision
1.  **Complexity vs. Performance:** While the 1D-CNN is more robust to temporal shifts, the Decision Tree provided **100% accuracy** on our current feature-engineered dataset. 
2.  **Thermal Impact:** The Decision Tree’s near-zero CPU usage was the deciding factor. It helped mitigate the **device heating issues** caused by the WiFi modules, as the processor remains in a low-power state between sampling intervals.
3.  **Final Verdict:** The Decision Tree was selected for final deployment because it provided the highest accuracy with the lowest possible resource footprint, representing the pinnacle of "Efficiency-First" Edge AI design.
---
## 7. Model Deployment & On-Device Performance

Deploying the intelligence onto the head-mounted gear required a precise integration of our data-scaling logic, the synchronized wireless communication, and the final classification model.

### Deployment Steps
1.  **Model Conversion:** The trained **Decision Tree** was converted into a static C++ header file (`model.h`). This approach transpiled the logical branches of the tree into a series of optimized `if-else` statements, allowing it to run as native machine code without the need for a heavy runtime interpreter.
2.  **Wireless Integration:** The Slave Nicla was flashed with a dedicated UDP-sender script that broadcasts its 6-axis readings at 50Hz. The Master Nicla was flashed with a multi-threaded logic that listens for these UDP packets, merges them with its own 6-axis readings, and triggers the inference engine.
3.  **Hardware Interfacing:** The final firmware includes drivers for the **OLED SSD1306** (to display gesture results) and the **Active Buzzer** (to provide audible confirmation for specific alerts like "Help" or "Emergency").

### Performance on Arduino Nicla Vision
*   **Inference Time:** Because the Decision Tree runs as native C++ logic, the inference time is **under 0.01 ms**. This is effectively "instantaneous" relative to the 20ms sampling interval, providing zero-lag feedback to the user.
*   **Resource Utilization:** 
    *   **CPU Load:** Extremely low. The processor spends most of its time waiting for the next sensor sample or managing the WiFi stack.
    *   **Memory Efficiency:** The entire deployment binary uses less than **20% of the available SRAM**, ensuring the device never crashes due to memory overflow.
*   **Real-time Behavior:** The system maintains a consistent **50Hz control loop**. We implemented a "Last-Known-Value" buffer for the Slave sensor data; if a UDP packet is lost due to network jitter, the Master uses the previous sample to maintain a continuous 12-axis feature vector, preventing gaps in the recognition stream.

### Deployment Observations
*   **Wireless Latency:** The UDP-based synchronization achieved a latency of less than **15ms**, which is well within the acceptable limit for real-time human activity recognition.
*   **User Feedback Loop:** Testing confirmed that from the moment a user completes a "Nod" or "Shake," the OLED display updates and the buzzer sounds in under **250ms**, providing a highly responsive experience for the motor-impaired user.
  
## 8. System Prototype - Parthib will add this
---
## 9. Conclusions & Limitations

### Conclusions
The project successfully demonstrates the feasibility of a high-precision, head-mounted Human Activity Recognition (HAR) system using Edge AI. By leveraging the **dual-IMU Master-Slave architecture**, we achieved 12-axis spatial redundancy, which proved critical in distinguishing between intentional head gestures and random motion noise. 

Key outcomes include:
*   **Edge Autonomy:** The system performs 100% of its inference on-device, ensuring zero cloud dependency, low latency (<250ms feedback loop), and maximum user privacy.
*   **Model Optimization:** Our comparative study proved that while 1D-CNNs offer superior temporal pattern recognition, a **Decision Tree Classifier** provided the most efficient balance of 100% accuracy and near-zero CPU/Memory utilization for the target hardware.
*   **Integrated Ecosystem:** Beyond the model, we developed a full assistive environment, integrating real-time local feedback (OLED/Buzzer) with remote caregiver monitoring via Streamlit and mobile notifications.

### Limitations
Despite the successful prototype, several technical and practical limitations were identified:

1.  **Hardware Thermal Constraints:** The decision to use **UDP over WiFi** for data synchronization between the Master and Slave boards caused significant thermal heating. The constant power draw of the WiFi modules on the compact Nicla Vision boards is a limiting factor for long-term wearable comfort.
2.  **Wireless Reliability:** While UDP is fast, it is a "connectionless" protocol. Environmental interference occasionally caused packet jitter or data loss, requiring the firmware to rely on "last-known" sensor values, which could momentarily decrease classification confidence.
3.  **Dataset Diversity:** The current dataset was collected from a limited cohort of five participants. While the model shows high generalization, it may require further calibration to handle individuals with specific neck mobility constraints or different physiological movement speeds.
4.  **Mechanical Sensitivity:** The accuracy of the 12-axis feature vector is highly dependent on the consistent alignment of the headband. Small shifts in the physical placement of the sensors relative to each other can introduce bias into the gravity-based accelerometer readings.
   
---
## 10. Future Work

The current prototype serves as a foundation for a sophisticated assistive communication system. Future development will focus on enhancing the hardware efficiency, model robustness, and user personalization.

### 1. Hardware & Power Optimization
To resolve the identified thermal heating issues, we plan to transition the Master-Slave communication from WiFi/UDP to **Bluetooth Low Energy (BLE)** or a high-speed **hard-wired UART link**. This will significantly reduce the power consumption of the Nicla Vision boards, prolonging battery life and making the device comfortable for continuous daily wear.

### 2. Advanced Model Deployment (CNN Pruning)
While the Decision Tree provided high accuracy for our initial dataset, we intend to deploy our **1D-Convolutional Neural Network (CNN)** for its superior temporal recognition. To make this feasible for the Edge, we will implement **Weight Pruning** and **Sparsification** to remove redundant connections in the network. This will shrink the CNN’s memory footprint, allowing it to provide deep-learning-level robustness with the same efficiency as a simpler model.

### 3. Personalized AI via Transfer Learning
Human motion varies significantly based on age and physical condition. We aim to implement a **User Calibration Mode**. By using **Transfer Learning**, the system could be "fine-tuned" for a specific patient using just 30 seconds of their individual head-movement data. This would allow the system to adapt to users with limited ranges of motion or unique physiological "signatures."

### 4. Expanded Gesture Vocabulary
We plan to expand the recognition library beyond the current seven activities to include more complex commands, such as "Double-Nod" for confirmation or "Head Circle" for specific environmental requests (e.g., controlling a smart-home light or television).

### 5. Multi-Modal Feedback Integration
Future iterations will include haptic (vibration) feedback on the headband itself. This would provide the user with immediate confirmation that their gesture was recognized without them needing to look at an OLED screen, making the interaction loop even more seamless and intuitive.

## 11. Challenges & Mitigation

The development of a dual-sensor wearable on an Edge platform presented several multi-disciplinary hurdles. Below are the primary technical, hardware, and data challenges faced during the project and the strategies implemented to mitigate them.

### 1. Technical Challenge: Model Overfitting and "Data Leakage"
*   **Challenge:** During early model training, we observed a common deep learning "trap" where the model reported near-perfect (100%) validation accuracy but failed completely (under 2% accuracy) on real-world test files. 
*   **Mitigation:** We identified this as **overlap leakage**; because we used a sliding window with 50% overlap, nearly identical data points were appearing in both training and validation sets. We mitigated this by implementing a strict **File-Based Data Split**. By ensuring that 100% of the windows from a single CSV file remained together in either the Training or Validation set, we forced the model to learn general head gestures rather than specific recording noise.

### 2. Hardware Challenge: Failure of Wired UART Communication
*   **Challenge:** Our initial architecture relied on a hard-wired UART link for Master-Slave communication. However, due to the high sensitivity of the Nicla Vision’s surface-mount pads, soldering proved unreliable, leading to intermittent connection failures and hardware instability.
*   **Mitigation:** We performed a technical pivot to a wireless architecture using **UDP over WiFi**. This allowed the two boards to communicate without physical wires. To handle the lack of a "handshake" in UDP, we developed a robust listener script on the Master board that could gracefully handle occasional dropped packets without crashing the inference loop.

### 3. Data Challenge: Wireless Jitter and Signal Synchronization
*   **Challenge:** Unlike a wired connection, UDP over WiFi introduces **network jitter**, where data packets from the Slave board arrive at irregular intervals. This made it difficult to perfectly align the left and right IMU signals into a single 12-axis feature vector.
*   **Mitigation:** We optimized the sampling rate to **50Hz**. This frequency was the "sweet spot"—fast enough to capture the high-frequency motion of a head shake, but slow enough to provide the UDP buffer sufficient time to recover from network delays. We also implemented a **"Last-Known-Value" buffer** to fill temporary gaps in the Slave’s data stream, ensuring the feature vector remained complete.

### 4. Debugging Challenge: Device Thermal Management (Heating)
*   **Challenge:** During long data collection and testing sessions, we observed significant **thermal heating** of the Nicla Vision boards. This was primarily caused by the high power consumption of the WiFi modules combined with continuous CPU-intensive processing.
*   **Mitigation:** To reduce the thermal profile, we chose to deploy the **Decision Tree model** for the final prototype. Because a Decision Tree is a series of simple logical branches (`if-else`), it requires near-zero CPU cycles compared to a CNN. This allowed the processor to remain in a low-power state between samples, successfully mitigating the heating issue while maintaining high accuracy.

### 5. Mechanical Challenge: Sensor Alignment and Gravity Bias
*   **Challenge:** Every participant wears the headband slightly differently, which changes the baseline "gravity vector" on the accelerometer. A model trained on one person's "Idle" position would fail on another person because their resting "zero point" was different.
*   **Mitigation:** We utilized **StandardScaler (Z-score Normalization)** during pre-processing. By centering all 12 axes around a mean of zero and scaling by standard deviation, we made the model **"Gravity-Invariant."** This forced the neural network to focus on the *relative change* in motion rather than the absolute angle of the sensors, allowing the system to generalize across different users.
---
## 12. References -  Parthib/Abha will add

[1] Gouwanda, D., & Senanayake, S. A. (2011). Identifying gait asymmetry using gyroscopes—A cross-correlation and Normalized Symmetry Index approach. *Journal of Biomechanics*, 44(5), 972–978.

[2] Ortega-Anderez, D., Lotfi, A., Langensiepen, C., & Appiah, K. (2019). A multi-level refinement approach towards the classification of quotidian activities using accelerometer data. *Journal of Ambient Intelligence and Humanized Computing*, 10(11), 4319–4330.

-- AI was used for debugging.
<div align="center">

[![Demo Video](https://img.shields.io/badge/▶_Watch_Full_Demo_Video-SharePoint-0078D4?style=for-the-badge&logo=microsoft)](https://indianinstituteofscience-my.sharepoint.com/:v:/g/personal/abhas_iisc_ac_in/IQCmHS_j7puyQ6OWcKqMe5GkAeruAGz5R6FupJL88lnMZLk?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=pOxfAL)

<img src="doc/Figure/demo_image.png" alt="Live Demo" width="680"/>
<br><em>Live gesture recognition — OLED displaying detected gesture in real-time</em>

</div>

---

## 13. Team Members and Roles

| Name | Key Contributions & Responsibilities |
|:---|:---|
| **Parthib Dey** | Hardware System Integration, Master-Slave Data Collection Setup, Model Pipeline Development, and On-Device Deployment. |
| **Abha Singh Sardar** | Primary Data Collection, Data Preprocessing, Feature Engineering, Traditional ML Model Training, and Performance Evaluation. |
| **Tishha Agrawal** | Data Collection, CNN Model Development & Preprocessing, Post-Training Quantization (PTQ) & Pruning, Streamlit Web Application Debugging, CNN model Deployment code(tried but not deployed), and Technical Documentation. |
| **Maitreyi Tiwari** | Data Collection, CNN Data Augmentation & Re-training, Quantization-Aware Training (QAT) & Pruning, Deployment code for CNN (tried but not deployed), `ntfy` Mobile Application debugging, and Technical Documentation. |


> **Course:** CP 330 — Edge AI &nbsp;|&nbsp; **Instructor:** Prof. Pandarasamy Arjunan &nbsp;|&nbsp; Indian Institute of Science (IISc), Bangalore, Semester 2, 2026
---

<div align="center">

**Built with ❤️ at IISc Bangalore**

*Making communication accessible for everyone*

</div>
