import network, time, socket, math
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX


SSID    = "OnePlusR"
KEY     = "abbadabbajabba"
PORT    = 6000
PC_IP   = "192.168.206.171"
PC_PORT = 5005

WINDOW_SIZE = 20

CLASS_NAMES = {
    1: "Nod", 2: "Head_Shake", 3: "Tilt_Left",
    4: "Tilt_Right", 5: "Look_Up", 6: "Look_Down", 7: "Idle"
}


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    time.sleep(1)


recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(("0.0.0.0", PORT))
recv_sock.setblocking(False)

pc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


spi = SPI(5)
cs = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
lsm = LSM6DSOX(spi, cs)

green_led = LED("LED_GREEN")
red_led   = LED("LED_RED")


def mean(x): return sum(x)/len(x)
def variance(x, m): return sum((v-m)*(v-m) for v in x)/len(x)
def rms(x): return math.sqrt(sum(v*v for v in x)/len(x))
def energy(x): return sum(v*v for v in x)
def median(x): return sorted(x)[len(x)//2]
def iqr(x):
    s = sorted(x)
    return s[3*len(s)//4] - s[len(s)//4]

def extract_features(window):
    features = []

    for ch in range(12):
        data = [row[ch] for row in window]
        m = mean(data)
        var = variance(data, m)

        features.extend([
            m, math.sqrt(var), min(data), max(data),
            var, rms(data), energy(data), iqr(data), median(data)
        ])


    gx1 = [r[3] for r in window]; gx2 = [r[9] for r in window]
    gz1 = [r[5] for r in window]; gz2 = [r[11] for r in window]
    ay1 = [r[1] for r in window]; ay2 = [r[7] for r in window]

    features.extend([
        mean(gx1)-mean(gx2),
        rms(gx1)-rms(gx2),
        mean(gz1)-mean(gz2),
        energy(gx1)+energy(gz1)+energy(gx2)+energy(gz2),
        mean(ay1)-mean(ay2)
    ])

    return features

def score(input):

    if input[78] <= 2.98:
        return [0,0,0,0,1,0,0]
    else:
        return [0,0,1,0,0,0,0]

pred_buffer = []
def smooth(pred):
    pred_buffer.append(pred)
    if len(pred_buffer) > 5:
        pred_buffer.pop(0)
    return max(set(pred_buffer), key=pred_buffer.count)

imu_buffer = []
last_slave = None

while True:

    a = lsm.accel()
    g = lsm.gyro()
    master = [a[0], a[1], a[2], g[0], g[1], g[2]]

    # receive slave
    try:
        data, _ = recv_sock.recvfrom(1024)
        parts = list(map(float, data.decode().split(",")))
        if len(parts) == 7:
            last_slave = parts[1:]
            green_led.on(); red_led.off()
    except:
        red_led.on()

    if not last_slave:
        time.sleep_ms(20)
        continue

    imu_buffer.append(master + last_slave)
    imu_buffer = imu_buffer[-WINDOW_SIZE:]

    if len(imu_buffer) < WINDOW_SIZE:
        continue

    features = extract_features(imu_buffer)
    if len(features) != 113:
        continue

    probs = score(features)
    pred = probs.index(max(probs)) + 1
    pred = smooth(pred)

    gesture = CLASS_NAMES[pred]

    print("Gesture:", gesture)

    try:
        pc_sock.sendto(f"{pred},{gesture}".encode(), (PC_IP, PC_PORT))
    except:
        pass

    time.sleep_ms(20)