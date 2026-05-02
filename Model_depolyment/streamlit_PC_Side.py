import streamlit as st
import socket
import threading
import json
import os
import time
import urllib.request
import subprocess
from datetime import datetime
from collections import deque, Counter

# =========================
# CONFIGURATION
# =========================
LOG = "gesture_data.json"
NTFY_TOPIC = "Head_Gesture_Recognition"
NTFY_COOLDOWN = 15 

# Smoothing Parameters
DEBOUNCE_N = 50           # Buffer size (Increase for more smoothing, 30-50 is ideal)
STABILITY_THRESHOLD = 0.95  # 70% of buffer must agree to change the gesture

COLORS = {
    "Nod": "#00C48C", "Head_Shake": "#FF4D4D", "Tilt_Left": "#F5A623",
    "Tilt_Right": "#4CAF50", "Look_Up": "#2979FF", "Look_Down": "#FF6D00", "Idle": "#9E9E9E"
}
EMOJI = {
    "Nod": "⬇️⬆️", "Head_Shake": "↔️", "Tilt_Left": "↙️",
    "Tilt_Right": "↘️", "Look_Up": "⬆️", "Look_Down": "⬇️", "Idle": "😐"
}
MESSAGES = {
    "Nod": "User nodded - may need assistance.",
    "Head_Shake": "User shaking head - check on them.",
    "Tilt_Left": "User tilting left.",
    "Tilt_Right": "User tilting right.",
    "Look_Up": "User looking up.",
    "Look_Down": "User looking down."
}

# =========================
# RELIABLE WINDOWS SPEECH (PowerShell)
# =========================
def speak_text(text):
    """Uses Windows PowerShell to speak. Bypasses Python sound library issues."""
    def _run():
        clean_text = text.replace("_", " ")
        # PowerShell command for Text-to-Speech
        ps_command = f'Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{clean_text}")'
        subprocess.run(["powershell", "-Command", ps_command], capture_output=True)

    threading.Thread(target=_run, daemon=True).start()

# =========================
# NTFY SENDER
# =========================
def send_ntfy(gesture):
    msg = MESSAGES.get(gesture)
    if not msg: return
    def _send():
        try:
            req = urllib.request.Request(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=msg.encode(),
                headers={"Title": f"Alert: {gesture}", "Priority": "high", "Tags": "brain"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=5)
        except: pass
    threading.Thread(target=_send, daemon=True).start()

# =========================
# UDP THREAD WITH MAJORITY VOTING (SMOOTHING)
# =========================
_started = False

def start_udp():
    global _started
    if _started: return
    _started = True

    def listen():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", 5005))
            sock.settimeout(2.0)

            counts = {}
            history = []
            raw_buffer = deque(maxlen=DEBOUNCE_N)
            stable_gesture = "Idle"
            stable_cls = 7
            last_sent = {}

            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    parts = data.decode().strip().split(",")
                    if len(parts) == 2:
                        cls, gesture = int(parts[0]), parts[1].strip()
                        raw_buffer.append((cls, gesture))

                        if len(raw_buffer) == DEBOUNCE_N:
                            # --- MAJORITY VOTING LOGIC ---
                            gesture_list = [g for _, g in raw_buffer]
                            occurence_count = Counter(gesture_list)
                            most_common_gesture, count = occurence_count.most_common(1)[0]

                            # Only change if the gesture is dominant in the buffer
                            if count >= (DEBOUNCE_N * STABILITY_THRESHOLD):
                                if most_common_gesture != stable_gesture:
                                    stable_gesture = most_common_gesture
                                    
                                    # Get the class number for the most common gesture
                                    cls_list = [c for c, g in raw_buffer if g == stable_gesture]
                                    stable_cls = Counter(cls_list).most_common(1)[0][0]
                                    
                                    now_str = datetime.now().strftime("%H:%M:%S")
                                    counts[stable_gesture] = counts.get(stable_gesture, 0) + 1
                                    history.insert(0, {"cls": stable_cls, "gesture": stable_gesture, "time": now_str})
                                    history = history[:20]

                                    # Trigger Sound and Notifications
                                    if stable_gesture != "Idle":
                                        speak_text(stable_gesture)
                                        now_ts = time.time()
                                        if now_ts - last_sent.get(stable_gesture, 0) >= NTFY_COOLDOWN:
                                            send_ntfy(stable_gesture)
                                            last_sent[stable_gesture] = now_ts

                        # Write state to disk for Streamlit UI
                        with open(LOG, "w") as f:
                            json.dump({
                                "cls": stable_cls, 
                                "gesture": stable_gesture, 
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "counts": counts, 
                                "history": history
                            }, f)

                except socket.timeout: continue
        except Exception as e: print(f"UDP Error: {e}")

    threading.Thread(target=listen, daemon=True).start()

start_udp()

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Gesture Monitor", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    .stApp { background: #FFFFFF; }
    .big-gesture { text-align: center; padding: 48px 32px; border-radius: 24px; margin-bottom: 24px; border: 2px solid #EEE; transition: all 0.3s; }
    .gesture-emoji { font-size: 4.5rem; margin-bottom: 10px; }
    .gesture-name { font-size: 3.5rem; font-weight: 900; letter-spacing: -1px; }
    .hist-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-radius: 12px; margin-bottom: 8px; background: #F7F7F7; border-left: 6px solid var(--c); font-family: 'Courier New', monospace; font-weight: bold; }
    .section-label { font-family: monospace; font-size: 0.8rem; color: #BBB; text-transform: uppercase; margin: 20px 0 10px; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Gesture Monitor")
st.markdown("<p style='color:gray; font-family:monospace;'>SMOOTHED OUTPUT + TTS ON</p>", unsafe_allow_html=True)

# Audio Test Button
if st.sidebar.button("🔊 Test Audio System"):
    speak_text("System online")

placeholder = st.empty()

while True:
    d = {"cls": 7, "gesture": "Idle", "time": "—", "counts": {}, "history": []}
    if os.path.exists(LOG):
        try:
            with open(LOG) as f: d = json.load(f)
        except: pass

    gesture = d["gesture"]
    color = COLORS.get(gesture, "#999")
    emoji = EMOJI.get(gesture, "😐")

    with placeholder.container():
        # Large Gesture Card
        st.markdown(f"""
            <div class="big-gesture" style="background:{color}10; border-color:{color}40;">
                <div class="gesture-emoji">{emoji}</div>
                <div class="gesture-name" style="color:{color}">{gesture.replace('_', ' ')}</div>
                <div style="color:#AAA; font-family:monospace; margin-top:10px;">CLASS {d['cls']} | LAST UPDATED: {d['time']}</div>
            </div>
        """, unsafe_allow_html=True)

        # Activity History
        st.markdown('<div class="section-label">Recent Activity</div>', unsafe_allow_html=True)
        if not d["history"]:
            st.info("Waiting for gesture data on Port 5005...")
        else:
            for item in d["history"][:10]:
                c = COLORS.get(item["gesture"], "#999")
                st.markdown(f"""
                    <div class="hist-row" style="--c:{c}">
                        <span>{item['gesture'].replace('_', ' ')}</span>
                        <span style="color:#CCC; font-size:0.8rem;">{item['time']}</span>
                    </div>
                """, unsafe_allow_html=True)

    time.sleep(0.4)