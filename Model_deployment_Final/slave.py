import network, time, socket
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX

# =========================
# CONFIG
# =========================
SSID = "Parthibg60"
KEY = "Parthib123"

MASTER_IP = "10.91.63.16"
PORT = 6000
###########

TARGET_PERIOD = 20  # ms → 50 Hz
# =========================

# LEDs
red_led = LED("LED_RED")
green_led = LED("LED_GREEN")

# =========================
# WIFI SETUP
# =========================
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    time.sleep(1)

print("Slave connected:", wlan.ifconfig())
green_led.on()

# =========================
# SOCKET (UDP)
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# =========================
# IMU SETUP
# =========================
spi = SPI(5)
cs = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
lsm = LSM6DSOX(spi, cs)

print("SLAVE READY (50 Hz)")

# =========================
# MAIN LOOP
# =========================
next_time = time.ticks_add(time.ticks_ms(), TARGET_PERIOD)

while True:
    # Read IMU
    a = lsm.accel()
    g = lsm.gyro()

    # Timestamp (important for sync)
    t = time.ticks_ms()

    # Send as FLOATS (matches your training)
    data = "%d,%f,%f,%f,%f,%f,%f" % (
        t,
        a[0], a[1], a[2],
        g[0], g[1], g[2]
    )

    print(data)

    sock.sendto(data.encode(), (MASTER_IP, PORT))

    # =========================
    # STABLE 50 Hz TIMING
    # =========================
    now = time.ticks_ms()
    sleep_time = time.ticks_diff(next_time, now)

    if sleep_time > 0:
        time.sleep_ms(sleep_time)

    next_time = time.ticks_add(next_time, TARGET_PERIOD)
