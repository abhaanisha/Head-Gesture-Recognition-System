import network, time, socket
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX

# =========================
# CONFIG
# =========================
SSID = "Parthibg60"
KEY = "Parthib123"

MASTER_IP = "10.91.132.16"
PORT = 6000

TARGET_PERIOD = 20  # ms → 50 Hz
# =========================

# LEDs
red_led = LED("LED_RED")
green_led = LED("LED_GREEN")

# WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    time.sleep(1)

print("Slave connected:", wlan.ifconfig())
green_led.on()

# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IMU
spi = SPI(5)
cs = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
lsm = LSM6DSOX(spi, cs)

print("SLAVE READY (50 Hz)")

# =========================
# LOOP
# =========================
while True:
    loop_start = time.ticks_ms()

    a = lsm.accel()
    g = lsm.gyro()

    data = "%f,%f,%f,%f,%f,%f" % (
        a[0], a[1], a[2],
        g[0], g[1], g[2]
    )

    sock.sendto(data.encode(), (MASTER_IP, PORT))

    # Maintain 50 Hz
    elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
    sleep_time = TARGET_PERIOD - elapsed

    if sleep_time > 0:
        time.sleep_ms(sleep_time)
