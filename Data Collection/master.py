import network, time, socket
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX

# =========================
# CONFIG
# =========================
SSID = "Parthibg60"
KEY = "Parthib123"

PC_IP = "10.91.132.79"
PC_PORT = 5005

SLAVE_PORT = 6000
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

print("Master connected:", wlan.ifconfig())
green_led.on()

# Sockets
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(("0.0.0.0", SLAVE_PORT))
recv_sock.setblocking(False)

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IMU
spi = SPI(5)
cs = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
lsm = LSM6DSOX(spi, cs)

last_slave = [0, 0, 0, 0, 0, 0]

# Debug counter
counter = 0

print("MASTER READY (50 Hz + SYNC)")
print("timestamp,ax1,ay1,az1,gx1,gy1,gz1,ax2,ay2,az2,gx2,gy2,gz2")

while True:
    loop_start = time.ticks_ms()

    # MASTER IMU
    a = lsm.accel()
    g = lsm.gyro()

    master_data = [
        a[0], a[1], a[2],
        g[0], g[1], g[2]
    ]


    try:
        data, addr = recv_sock.recvfrom(1024)
        parts = list(map(float, data.decode().split(",")))

        if len(parts) == 6:
            last_slave = parts

    except:
        pass

 
    ts = time.ticks_ms()

    combined = [ts] + master_data + last_slave
    out = ",".join(map(str, combined))


    send_sock.sendto(out.encode(), (PC_IP, PC_PORT))

    counter += 1
    if counter % 10 == 0:   # print every 10 loops (~5 Hz)
        print(out)

    elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
    sleep_time = TARGET_PERIOD - elapsed

    if sleep_time > 0:
        time.sleep_ms(sleep_time)


#nicla master code