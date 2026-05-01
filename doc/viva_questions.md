# Viva Questions — Head Gesture Recognition System
**IISc Edge AI Course | April–May 2026**

> Questions are grouped by topic, progressing from intuitive basics a professor would probe first, to deep technical and design-reasoning questions.

---

## SECTION 1 — Problem & Motivation

---

**Q1. Why does this project exist? Couldn't a patient just use a smartphone or button panel?**

**A:** Many patients in the target group (severely paralysed elderly or accident survivors) have lost fine motor control in their hands — they cannot reliably press buttons or hold a phone. However, they often retain **voluntary head movement** because the neck muscles are controlled by a different neural pathway (cranial nerves, brainstem) that is frequently spared in conditions like ALS, spinal cord injury, or post-stroke paralysis. The project exploits this retained capability as a communication channel.

A smartphone also requires a caregiver to be in proximity and involves cloud dependency. This device is self-contained on the patient's body.

---

**Q2. Why not use eye-tracking or voice recognition instead of head gestures?**

**A:**
- **Eye-tracking** requires a front-facing camera, calibration per session, controlled lighting, and the patient's eyes to be open and focused. It fails in low-light, and the patient cannot close their eyes to rest.
- **Voice recognition** fails for patients with dysarthria (speech impairment), which commonly accompanies motor neuron diseases. Many target users cannot produce clear speech.
- **Head gestures** are coarse, robust, and intuitive. The system works in the dark, doesn't require any visual attention from the patient, and the 6 chosen gestures map naturally to universal communication primitives (yes/no, water, help, emergency).

---

**Q3. Why limit to exactly 6 gestures + Idle? Why not 20 gestures?**

**A:** Several engineering constraints:
1. **Classification difficulty increases exponentially** as classes are added, especially with noisy IMU data and limited training data.
2. **User cognitive load** — a severely fatigued or unwell patient cannot reliably recall and reproduce 20 distinct gestures.
3. **Hardware limitation** — the OLED is 128×64 pixels; displaying more than one short phrase is impractical.
4. **Biomechanical limits** — the human head has limited degrees of freedom (pitch, roll, yaw). Beyond 6 distinct gestures, movements become ambiguous or physically tiring.

The 6 chosen gestures cover the most critical communication needs: affirmation, negation, three specific requests, and an emergency signal.

---

## SECTION 2 — Hardware Architecture

---

**Q4. You use two Arduino Nicla Vision boards. What is inside each one?**

**A:** Each Nicla Vision contains:
- **MCU:** STM32H747XI — a dual-core (Cortex-M7 @ 480 MHz + Cortex-M4 @ 240 MHz) microcontroller
- **IMU:** LSM6DSRX — a 6-axis MEMS sensor (3-axis accelerometer + 3-axis gyroscope) connected via SPI
- **Wi-Fi / Bluetooth:** Murata LBEE5KL1DX module (used for Wi-Fi UDP communication here)
- **Camera:** 2 MP CMOS image sensor (unused in this project)
- **FPU (Floating Point Unit):** available on Cortex-M7, enables efficient TFLite inference

---

**Q5. One board is the "Master" and one is the "Slave." Who decided this and why?**

**A:** This is a deliberate design choice driven by resource allocation:
- The **Master** (right temple) aggregates data, runs TinyML inference, drives the OLED and buzzer. It is the "brain."
- The **Slave** (left temple) has a single job: read its IMU and send data. It offloads all computation to the Master.

This asymmetric design is called a **star topology**. An alternative would be peer-to-peer (both boards run inference), but that doubles cost and complexity. The Master-Slave model is simpler, uses less power on the Slave side, and avoids synchronisation problems if both boards independently computed predictions.

---

**Q6. Why is the Master on the right temple specifically?**

**A:** No strict technical requirement — either temple would work electrically. However, the right temple was chosen because:
1. Most people are right-side dominant — mounting the primary computing unit on the dominant side reduces cable routing complexity.
2. The OLED and buzzer wires run downward from the Master; routing them from the right side toward a caregiver's view is more natural.
3. Symmetry: in the dataset, `ax1/gx1` always refers to the right temple, which kept the feature space consistent across all data collectors.

---

**Q7. The IMU is the LSM6DSRX. What does MEMS mean? How does it actually measure acceleration?**

**A:** MEMS = **Micro-Electro-Mechanical System**. The accelerometer inside is a microscopic mechanical structure — a tiny proof mass suspended by silicon springs, etched onto a chip. When the device accelerates, the proof mass deflects against the springs. This deflection changes the capacitance between the proof mass and fixed plates. The electronics measure this capacitance change and convert it to an acceleration value.

The gyroscope uses the **Coriolis effect**: a vibrating MEMS mass experiences a force perpendicular to its vibration when the device rotates. This perpendicular force is measured capacitively as angular velocity.

---

**Q8. What is SPI and why is it used to communicate with the IMU instead of I2C?**

**A:**
- **SPI (Serial Peripheral Interface):** 4-wire synchronous protocol — MOSI, MISO, SCK, CS. Full-duplex, clock speeds up to 50+ MHz.
- **I2C:** 2-wire open-drain bus. Half-duplex, typically 100 kHz–1 MHz.

**Why SPI for IMU:** The LSM6DSRX can output at up to 6.66 kHz data rate. At 50 Hz (our sampling rate), the bottleneck isn't data rate, but SPI is still preferred because:
1. It is **point-to-point** (dedicated CS pin) — no address conflicts
2. It is **lower latency** than I2C
3. The Nicla Vision firmware library (`lsm6dsox`) is implemented over SPI

The OLED uses I2C because it is a slower display device where 100 kHz is perfectly adequate, and it saves GPIO pins.

---

**Q9. Your system has two IMUs sampling at 50 Hz each over Wi-Fi. Is the data actually synchronised?**

**A:** Not perfectly — this is a known limitation. The Slave transmits its IMU reading over UDP at ~50 Hz independently of the Master. The Master reads its own IMU at exactly 50 Hz and picks up the **most recent** Slave UDP packet received at that moment. So there can be a desynchronisation of 0 to 20 ms between the two IMU readings in any given sample.

At 50 Hz, 20 ms is one full sample period — meaning in the worst case, the Master's current reading is paired with the Slave's previous reading. This is an inherent limitation of the software-timed, UDP-based architecture.

**Why it still works:** Head gestures evolve over 500ms–1000ms. A 0–20 ms desynchronisation is small relative to gesture duration. The statistical features extracted over a 1-second window average out the jitter effect. A hardware-synchronised system (using a hardware trigger line) would be ideal but is impractical without custom PCB design.

---

## SECTION 3 — Communication Protocol

---

**Q10. Why UDP? What is the difference between UDP and TCP?**

**A:**

| Property | UDP | TCP |
|---|---|---|
| Connection | Connectionless | Connection-oriented (handshake) |
| Delivery | No guarantee | Guaranteed, ordered |
| Overhead | ~8 bytes header | ~20 bytes header + ACK overhead |
| Latency | Very low | Higher (retransmissions, ACKs) |
| Use case | Real-time streaming | File transfer, web |

**For 50 Hz IMU streaming:** A missed packet at 50 Hz means ~20 ms of missing data. This is acceptable because:
1. The Master reuses the last known Slave value — a brief gap is better than stalling to wait for a retransmission.
2. TCP's retransmission mechanism would introduce unbounded latency spikes whenever a packet is lost — far worse than a stale value.

UDP is the standard choice for real-time sensor streaming (same reason video calls use UDP not TCP).

---

**Q11. The Slave sends to IP `10.91.132.16` (the Master's IP) hardcoded. What happens if the Master's IP changes?**

**A:** It breaks — the Slave cannot find the Master. This is a known hardcoding issue documented in the project. In deployment, the fix would be:
1. **Static IP assignment** in the Wi-Fi router's DHCP table (by MAC address) — the Master always gets the same IP.
2. **mDNS (Bonjour/Avahi):** The Master advertises itself as `master-nicla.local` and the Slave resolves this hostname dynamically.
3. **Broadcast discovery:** Slave broadcasts on `255.255.255.255` and Master responds with its IP.

For the lab demo, static assignment via router DHCP reservation is the simplest fix.

---

**Q12. The Master sends data to port 5005 on the PC during data collection. During inference deployment, does it still send to the PC?**

**A:** No. During deployed inference mode, `master.py` runs the TinyML model locally and does **not** stream to the PC. The data collection and inference modes are mutually exclusive:
- **Collection mode:** Master acts as a forwarder — collects, merges IMU data, sends 13-value CSV row to PC.
- **Inference mode:** Master runs the Edge Impulse library locally — fills a circular buffer, runs FFT → classifier → OLED/Buzzer output. No PC involved.

This is the key advantage of TinyML: the PC is only needed during development, not during patient use.

---

## SECTION 4 — Data Collection & Dataset

---

**Q13. You sampled at 50 Hz. How did you choose this rate? What is the Nyquist criterion telling you?**

**A:** By the **Nyquist-Shannon sampling theorem**, to faithfully reconstruct a signal of maximum frequency `f_max`, you must sample at at least `2 × f_max`.

Head gestures are voluntary, slow biological movements. The biomechanically useful frequency content of head gestures is below **5 Hz** — a nod or head shake completes at most 2 cycles per second. Even including higher harmonics, there is negligible gesture-relevant energy above 10 Hz.

So Nyquist requires: `f_sample ≥ 2 × 10 = 20 Hz` minimum.

**Why 50 Hz:** Chosen to give 2.5× margin over the Nyquist requirement. Also, 50 Hz = 20 ms period, which is:
- Easily achievable on MicroPython with `time.ticks_ms()` timing
- A standard IMU data rate for wearable applications
- Produces 50 samples in 1 second → clean window size

Sampling faster (e.g., 200 Hz) would add noise, consume more memory, and complicate MicroPython timing without benefiting gesture recognition.

---

**Q14. Why collect data from 4 different people (Abha, Adarsh, Parthib, Maitreyi)? Why not just one expert performer?**

**A:** This is about **generalisation** vs **overfitting to a specific person's style**. If a model is trained on only one person's gestures:
- It learns that person's specific head motion amplitude, speed, and posture
- It will fail on other users whose gestures differ in scale or style

By collecting from 4 people with different:
- Head sizes (affecting IMU lever arm)
- Gesture amplitudes (some people nod 20°, others 5°)
- Movement speeds
- Body postures (sitting upright vs reclining)

The model is forced to learn the *invariant structural signature* of each gesture rather than a person-specific pattern. This is called **cross-subject generalisation** and is essential for any assistive technology that must work out-of-the-box for new patients.

---

**Q15. A session is 250 seconds. Is that enough data?**

**A:** At 50 Hz, 250 seconds = **12,500 raw rows** per session. With 50% overlapping 1-second windows, that yields approximately **498 windows** per session. With ~4 sessions per class, that is ~2,000 windows per class, and ~14,000 total training windows across 7 classes.

Is this enough? It depends:
- **For a simple Dense MLP on 148 features:** Yes, this is comfortably sufficient. The model has ~30,000 parameters but features are highly informative.
- **For a CNN on raw sequences:** Likely insufficient — CNNs need 10,000+ samples per class.
- **For generalisation to new users:** Borderline. 4 subjects is a minimal diversity set. 10+ subjects would be ideal for a clinical deployment.

The target accuracy of ≥88% was achieved, validating that the dataset is adequate for the current scope.

---

**Q16. You excluded `test_*.csv` files from training. Why? What were they used for?**

**A:** The `test_*.csv` files are **calibration recordings** made at the start of sessions to verify the hardware was working correctly — confirming Wi-Fi connection, sensor readings, and correct CSV format. They are not labeled with specific gesture classes and may contain:
- Mixed/ambiguous motion (person moving around while checking setup)
- Sensor warmup artifacts
- Incomplete or garbage data

Including them would introduce **unlabeled noise** into the training set, corrupting the class boundaries the model tries to learn. They are excluded by checking if the filename starts with `test` before loading.

---

## SECTION 5 — Machine Learning Pipeline

---

**Q17. Why a 1-second window? What happens if you use 500ms or 2 seconds?**

**A:** The window size is a **gesture duration tradeoff**:

| Window | Implication |
|---|---|
| **500 ms** | May capture an incomplete gesture (a nod takes ~800ms). Statistical features represent a partial signal — reduced accuracy. But lower latency. |
| **1 second** | Captures one complete gesture cycle for most gestures. Good balance. |
| **2 seconds** (Edge Impulse default) | May capture 1–2 complete cycles. Better for periodic gestures (Head Shake). But: doubles latency, captures more "non-gesture" signal at edges, and is computationally heavier. |

The Edge Impulse pipeline uses 2 seconds (100 samples); our custom pipeline uses 1 second (50 samples). The 1-second choice was made to reduce inference latency and because most gestures complete within 1 second for the 4 data collectors.

---

**Q18. What is StandardScaler doing mathematically? Why is it fitted only on training data?**

**A:** `StandardScaler` transforms each feature `x` as:

```
x_scaled = (x - mean_train) / std_train
```

This centres each feature to zero mean and scales to unit variance across the training set.

**Why train-only fitting:** If we compute `mean` and `std` on the entire dataset (train + test), we are using information from the test set to normalise the training data. This is **data leakage** — the model effectively "sees" test set statistics during training, which artificially inflates evaluation accuracy. The test set must remain completely unseen until final evaluation.

In deployment, the **same scaler** (with the training set's `mean` and `std`) is applied to live sensor data. This is why `scaler.pkl` is saved — so the exact same transformation is applied at inference time.

---

**Q19. You chose a Dense MLP (fully-connected network) over CNN or LSTM. Can you defend this?**

**A:** Yes, because the features are already **hand-engineered to be permutation-invariant** — the 148 features are a flat vector where spatial/temporal order does not carry meaning. CNN and LSTM exploit spatial locality and temporal order respectively.

- **CNN** expects local correlations in adjacent input dimensions. Our feature vector has no meaningful spatial adjacency (feature 3 and feature 4 are not inherently related the way adjacent pixels in an image are).
- **LSTM** expects temporal dependencies across timesteps. Our feature extraction already compresses the time dimension — the window's temporal information is summarised in statistics.

A Dense MLP is the correct architecture for a flat, order-independent feature vector. It also meets TinyML constraints: 30,663 parameters at ~33 KB INT8, with sub-5 ms inference on the Cortex-M7.

---

**Q20. You use Batch Normalisation inside the network. What does it do and why is it important for this project?**

**A:** Batch Normalisation (BN) normalises the activations at each layer across the current mini-batch to zero mean and unit variance, then applies a learnable scale and shift:

```
y = γ × (x - μ_batch) / σ_batch + β
```

**Why it matters here:**
1. **Training stability:** IMU features span very different ranges even after StandardScaler (cross-IMU correlation is [-1, 1], energy is in thousands). BN prevents internal covariate shift — the distribution change in layer inputs as weights update.
2. **Faster convergence:** BN allows higher learning rates.
3. **Implicit regularisation:** BN adds slight noise from batch statistics, reducing overfitting on a relatively small dataset (~14,000 windows).

**Important at deployment:** During inference, BN uses the **running mean/variance** accumulated during training (not mini-batch stats), so it is deterministic.

---

**Q21. Your model outputs probabilities from Softmax. What is the inference decision rule?**

**A:** The model outputs a vector of 7 probabilities that sum to 1.0. The predicted class is:

```
class = argmax(softmax_output)
```

However, a simple argmax can be overconfident. In production, a **confidence threshold** should be applied:
- If `max(softmax_output) < threshold` (e.g., 0.6), classify as **Idle** or "uncertain" and do not trigger any output.

This prevents triggering "EMERGENCY" when the model is only 52% confident. The current implementation does not yet implement thresholding — this is noted as a future enhancement.

---

**Q22. What is INT8 quantisation? What does it trade off?**

**A:** Neural network weights are normally stored as 32-bit floating point (float32). **INT8 quantisation** converts them to 8-bit signed integers:

```
x_int8 = round(x_float32 / scale) + zero_point
```

Where `scale` and `zero_point` are calibrated using the representative dataset.

**Tradeoffs:**

| | Float32 | INT8 |
|---|---|---|
| Weight precision | 32 bits | 8 bits |
| Model size | 120 KB | **33.6 KB** (3.6× smaller) |
| Inference speed | Baseline | 2–4× faster (integer arithmetic) |
| RAM usage | High | **4× lower** |
| Accuracy | Baseline | Minor drop (~1–2%) |

For the Nicla Vision with 1 MB RAM and no GPU, INT8 is not just preferred — it may be **required** to fit the model in memory and meet the 15–40 ms latency target.

---

## SECTION 6 — System Design & Edge AI

---

**Q23. What is TinyML? How is it different from regular ML?**

**A:** TinyML is the field of deploying machine learning models on **microcontrollers** — devices with:
- RAM in the range of kilobytes to low megabytes (vs gigabytes in cloud servers)
- No operating system (bare-metal or RTOS)
- No floating-point GPU — arithmetic on a simple integer ALU or small FPU
- Power consumption of milliwatts (battery-operated)

Key differences from regular ML:

| Aspect | Regular ML | TinyML |
|---|---|---|
| Hardware | GPU server, cloud | MCU (Cortex-M, RISC-V) |
| Model size | Hundreds of MB | Tens of KB |
| Inference | Milliseconds on GPU | 5–50 ms on MCU |
| Power | Watts–kilowatts | Milliwatts |
| Connectivity | Cloud required | Fully offline |
| Privacy | Data leaves device | Data never leaves device |

This project specifically targets TinyML because the target users cannot afford cloud connectivity costs, require immediate response (no network latency), and need the device to work in environments without internet (hospital wards, rural homes).

---

**Q24. "Edge AI" is in your course name. What specifically makes this an "edge" system?**

**A:** The term "edge" refers to computation happening at the **network edge** — on the sensor device itself — rather than in a centralised cloud server.

This system is edge AI because:
1. **Inference is on-device:** The Nicla Vision's STM32H747 runs the TFLite model. No data is sent to the internet.
2. **Real-time feedback:** OLED and Buzzer respond within 15–40 ms of gesture completion. Cloud round-trip latency would be 100–500 ms minimum.
3. **Offline operation:** Works in areas with no internet. This is critical for hospital wards with restricted Wi-Fi.
4. **Privacy:** Patient gestures are never uploaded to a server — medical data stays on the device.
5. **Battery-friendly:** A small MCU inference uses microwatts vs streaming raw data to cloud which requires Wi-Fi transmit power continuously.

---

**Q25. Why use Edge Impulse for the ML pipeline? Couldn't you just use TensorFlow directly?**

**A:** Both approaches were actually used in this project — Edge Impulse for the primary deployment pipeline and custom TensorFlow for the research/development pipeline. The comparison:

**Edge Impulse advantages:**
- Automatic spectral analysis block (FFT + windowing) optimised for MCU deployment
- One-click Arduino `.zip` library export with quantised TFLite model + inference engine
- Handles all DSP preprocessing on-device (the FFT runs on the MCU, not just the NN)
- Visual debugging tools (feature explorer, live inference)

**Custom TF/sklearn advantages:**
- Full control over feature engineering (our 148-feature dual-IMU pipeline)
- Easier to implement novel features like cross-IMU symmetry features
- Better for research and experimentation

The **production firmware** uses Edge Impulse's exported library (for robustness). The **custom pipeline** (`train_model.py`) provides deeper insight, baseline comparison, and is more publication-ready.

---

**Q26. The OLED displays text like "NEED WATER." What if the patient is in a dark room?**

**A:** This is why the **dual feedback design** (OLED + Buzzer) was chosen. The buzzer provides **audio feedback** that works in complete darkness, with eyes closed, or for visually impaired caregivers. Each gesture has a distinct buzzer pattern (1 beep, 2 beeps, long beep, continuous alarm) that caregivers can learn.

For improvements:
- A **vibration motor** could be added for tactile feedback
- A **wireless alert** (Bluetooth to phone) would notify a caregiver in another room
- A **high-brightness OLED** or e-ink display improves readability in bright light

This is explicitly listed in Section 13 (Future Enhancements) of the project overview.

---

## SECTION 7 — Robustness, Failure Modes & Ethics

---

**Q27. What happens if the patient accidentally nods while turning their head? How does the system avoid false positives?**

**A:** This is the **segmentation problem** — the sliding window continuously runs inference, and any window containing gesture-like motion produces a classification. Mitigation strategies:

1. **Idle class:** Trained explicitly on natural resting motion, conversation head movements, and minor fidgeting. The model learns to output "Idle" for ambiguous motion.
2. **Confidence thresholding:** Only act on predictions where `softmax_max > 0.75` (not yet implemented).
3. **Temporal smoothing / voting:** Take the mode of the last 3 window predictions before acting — a single ambiguous window is overridden by the majority.
4. **User training period:** Caregivers are instructed that the patient must perform deliberate, exaggerated gestures for reliable detection.

This is also why "Idle" is class 7 and not simply "everything else" — a dedicated trained class for non-gesture states dramatically reduces false positives.

---

**Q28. What if one board's battery dies mid-use? What does the system do?**

**A:** If the **Slave** dies:
- The Master stops receiving UDP packets from port 6000
- Master's code: `if data_from_slave: last_slave = data; else: use last_slave` — it simply continues with the **last known Slave values** frozen
- With frozen Slave values, the bilateral cross-IMU features (`cross_gx_mean_diff`, `cross_gz_corr`) become meaningless — they reflect an old state
- The model may still work for gestures that are primarily captured by Master's own IMU (Nod, Head Shake, Look Up/Down) but will **fail for Tilt Left vs Right discrimination**
- A hardware fix: add a dead-man timer — if no Slave packet in 500 ms, display "SENSOR ERROR" on OLED

If the **Master** dies, the entire system fails (it is the single point of computation).

---

**Q29. Is there an ethical concern with using this device on cognitively impaired patients?**

**A:** Yes — informed consent and error consequences are critical considerations:

1. **False positives for EMERGENCY (Look Up):** The system could trigger a continuous alarm incorrectly, causing patient distress and wasting caregiver time. This could lead caregivers to ignore future alerts — the "cry wolf" problem.
2. **Consent:** A severely paralysed patient may not be able to consent to wearing the device or correct false classifications. A proxy (family/guardian) must be involved.
3. **Dependency:** If the device fails, a patient who has come to rely on it for communication is left worse off than before. Robust failure indication is essential.
4. **Data privacy:** Although inference is on-device, any future cloud-connected version would transmit patient behaviour data — regulated under HIPAA/GDPR in medical contexts.

For an academic proof-of-concept, these concerns are documented but not fully resolved — they would be central to any clinical trial or ethics board review before deployment.

---

**Q30. If a professor asks "What is the single biggest limitation of your current system?" — what is your honest answer?**

**A:** The single biggest limitation is **lack of cross-subject generalisation testing**. The 4 data collectors are all young, able-bodied university students with typical head motion amplitudes and speeds. The target users are:
- Elderly patients with reduced range of motion (smaller, slower gestures)
- Patients with cervical tremors (involuntary head motion that may confuse Idle vs gesture)
- Patients wearing cervical collars or braces (mechanically constrained motion)

The model was trained and tested on **the same 4 subjects** — we do not have held-out subject validation. A proper evaluation would require training on subjects 1–3, testing on subject 4 (leave-one-subject-out cross-validation) to estimate true generalisation. The accuracy would likely drop from the reported figure, but by how much is unknown.

This is acknowledged in Section 12 (Known Issues) and Section 13 (Future Enhancements) of the project overview.

---

*Document generated: May 2026 | IISc Edge AI Course Project Viva Preparation*
