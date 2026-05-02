import network, time, socket, math
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX

SSID        = "Parthibg60"
KEY         = "Parthib123"

PORT        = 6000          # receive from slave

PC_IP       = "10.91.63.79"
PC_PORT     = 5005          # send to PC

UNO_IP      = "10.91.63.59" # Uno R4 WiFi IP
UNO_PORT    = 5006          # port for Uno R4 WiFi

WINDOW_SIZE = 20

CLASS_NAMES = {
    1: "Nod",
    2: "Head_Shake",
    3: "Tilt_Left",
    4: "Tilt_Right",
    5: "Look_Up",
    6: "Look_Down",
    7: "Idle"
}


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    time.sleep(1)

print("Master IP:", wlan.ifconfig()[0])


recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(("0.0.0.0", PORT))
recv_sock.setblocking(False)

pc_sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
uno_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

spi = SPI(5)
cs  = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
lsm = LSM6DSOX(spi, cs)

green_led = LED("LED_GREEN")
red_led   = LED("LED_RED")


imu_buffer = []
last_slave = None


def mean(x):
    return sum(x) / len(x)

def variance(x, m):
    return sum((v - m) * (v - m) for v in x) / len(x)

def rms(x):
    return math.sqrt(sum(v * v for v in x) / len(x))

def energy(x):
    return sum(v * v for v in x)

def median_iqr(x):
    s = sorted(x)
    n = len(s)
    return s[n // 2], s[3 * n // 4] - s[n // 4]


def extract_features(window):
    features = []

    for ch in range(12):
        data = [row[ch] for row in window]

        m   = mean(data)
        var = variance(data, m)
        med, iq = median_iqr(data)

        features.extend([
            m,
            math.sqrt(var),
            min(data),
            max(data),
            var,
            rms(data),
            energy(data),
            iq,
            med
        ])  ## 9 features * 12 chaneels = 108 features

    # Cross-IMU features (5)
    gx1 = [row[3]  for row in window]
    gx2 = [row[9]  for row in window]
    gz1 = [row[5]  for row in window]
    gz2 = [row[11] for row in window]
    ay1 = [row[1]  for row in window]
    ay2 = [row[7]  for row in window]

    features.extend([
        mean(gx1) - mean(gx2),
        rms(gx1)  - rms(gx2),
        mean(gz1) - mean(gz2),
        energy(gx1) + energy(gz1) + energy(gx2) + energy(gz2),
        mean(ay1) - mean(ay2)
    ]) ## 5 IMU cross channel features

    return features


def score(input):
    if input[78] <= 2.9801491498947144:
        if input[111] <= 6447.829833984375:
            if input[8] <= 0.5377808511257172:
                if input[3] <= -0.1123657338321209:
                    var0 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                else:
                    if input[42] <= 3293.8863525390625:
                        var0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
                    else:
                        var0 = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            else:
                var0 = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        else:
            if input[96] <= 10047.057373046875:
                if input[3] <= -0.1484375186264515:
                    var0 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
                else:
                    if input[51] <= 4963.455078125:
                        var0 = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
                    else:
                        var0 = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            else:
                var0 = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        if input[74] <= -0.07305900380015373:
            if input[8] <= -0.5585937574505806:
                var0 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
            else:
                var0 = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
        else:
            if input[0] <= 0.6474524587392807:
                var0 = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
            else:
                var0 = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    return var0


pred_buffer = []

def smooth(pred):
    pred_buffer.append(pred)
    if len(pred_buffer) > 5:
        pred_buffer.pop(0)
    counts = {}
    for p in pred_buffer:
        counts[p] = counts.get(p, 0) + 1
    return max(counts, key=counts.get)

counter       = 0
last_cls      = None
TARGET_PERIOD = 20  # ms → 50 Hz to match slave

next_tick = time.ticks_add(time.ticks_ms(), TARGET_PERIOD)

def _wait(next_tick):
    now = time.ticks_ms()
    diff = time.ticks_diff(next_tick, now)
    if diff > 0:
        time.sleep_ms(diff)

while True:

    a = lsm.accel()
    g = lsm.gyro()
    master_data = [a[0], a[1], a[2], g[0], g[1], g[2]]

    try:
        data, _ = recv_sock.recvfrom(256)
        parts = data.decode().strip().split(",")
        if len(parts) == 7:
            _, ax2, ay2, az2, gx2, gy2, gz2 = map(float, parts)
            last_slave = [ax2, ay2, az2, gx2, gy2, gz2]
            green_led.on()
            red_led.off()
    except:
        red_led.on()

    if last_slave is None:
        _wait(next_tick)
        next_tick = time.ticks_add(next_tick, TARGET_PERIOD)
        continue

    
    sample = master_data + last_slave
    imu_buffer.append(sample)

    if len(imu_buffer) > WINDOW_SIZE:
        imu_buffer.pop(0)

    if len(imu_buffer) < WINDOW_SIZE:
        _wait(next_tick)
        next_tick = time.ticks_add(next_tick, TARGET_PERIOD)
        continue

    features = extract_features(imu_buffer)

    if len(features) != 113:
        print("Feature error:", len(features))
        _wait(next_tick)
        next_tick = time.ticks_add(next_tick, TARGET_PERIOD)
        continue

    probs     = score(features)
    pred_idx  = probs.index(max(probs))
    cls       = pred_idx + 1        # 1-indexed
    cls       = smooth(cls)

    gesture_name = CLASS_NAMES[cls]


    counter += 1
    if counter % 10 == 0:
        print("Gesture:", cls, "→", gesture_name)


    try:
        pc_sock.sendto("{},{}".format(cls, gesture_name).encode(), (PC_IP, PC_PORT))
    except:
        pass


    if cls != last_cls:
        try:
            uno_sock.sendto("{},{}".format(cls, gesture_name).encode(), (UNO_IP, UNO_PORT))
        except:
            pass
        last_cls = cls

    # --- TICK-ACCURATE WAIT ---
    _wait(next_tick)
    next_tick = time.ticks_add(next_tick, TARGET_PERIOD)
