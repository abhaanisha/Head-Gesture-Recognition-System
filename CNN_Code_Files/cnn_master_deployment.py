import network, time, socket, gc, sys
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX
import ml

gc.collect()
print("Free memory before model load:", gc.mem_free())
net = ml.Model('har_ann_quantized.tflite')
print("Model loaded!")
gc.collect()
print("Free memory after model load:", gc.mem_free())

SSID    = "OnePlusR"
KEY     = "abbadabbajabba"
PORT    = 6000
PC_IP   = "192.168.206.171"
PC_PORT = 5005

WINDOW_SIZE = 80

CLASS_NAMES = {
    1: "Nod", 2: "Head_Shake", 3: "Tilt_Left",
    4: "Tilt_Right", 5: "Look_Up", 6: "Look_Down", 7: "Idle"
}

SCALER_MEANS  = [0.1518586418097311, -0.7227120891108287, -0.10258878466869441,
                 -0.15682667099113337, -0.24560455374977125, -0.6224975170030378,
                 0.15338740644852286,  0.7611325523308886, -0.07146121541176283,
                 0.2862961362794703,  -0.0038595746323525602, 0.021665234433823684]

SCALER_SCALES = [0.47900941989022583, 0.20388079618646038, 0.3816902374359865,
                 7.799821540315228, 19.491956022321034, 7.539725085786051,
                 0.4671882038636089,  0.20930624041943868, 0.3373695314305047,
                 8.146055579986694,  19.64095545341594, 7.670086446860107]

TFLITE_SCALE      = 0.019820360466837883
TFLITE_ZERO_POINT = -10


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    time.sleep(1)
print("MASTER IP:", wlan.ifconfig()[0])

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(("0.0.0.0", PORT))
recv_sock.setblocking(False)
pc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

spi = SPI(5)
cs  = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
lsm = LSM6DSOX(spi, cs)

green_led = LED("LED_GREEN")
red_led   = LED("LED_RED")

pred_buffer = []
def smooth(pred):
    pred_buffer.append(pred)
    if len(pred_buffer) > 5:
        pred_buffer.pop(0)
    return max(set(pred_buffer), key=pred_buffer.count)

imu_buffer = []
last_slave = None
print("Starting inference loop")

while True:
    try:

        a = lsm.accel()
        g = lsm.gyro()
        master = [a[0], a[1], a[2], g[0], g[1], g[2]]


        try:
            data, _ = recv_sock.recvfrom(1024)
            parts = list(map(float, data.decode().split(",")))
            if len(parts) == 7:
                last_slave = parts[1:]
                green_led.on()
                red_led.off()
        except:
            red_led.on()

        if not last_slave:
            time.sleep_ms(20)
            continue


        imu_buffer.append(master + last_slave)
        if len(imu_buffer) > WINDOW_SIZE:
            imu_buffer.pop(0)
        if len(imu_buffer) < WINDOW_SIZE:
            continue

     
        for row in imu_buffer:
            for i in range(12):
                scaled    = (row[i] - SCALER_MEANS[i]) / SCALER_SCALES[i]
                quantized = int((scaled / TFLITE_SCALE) + TFLITE_ZERO_POINT)
                quantized = max(-128, min(127, quantized))
                input_data.append(quantized)

    
        input_bytes = bytearray([v & 0xFF for v in input_data])

     
        start       = time.ticks_ms()
        predictions = net.predict([input_bytes])
        end         = time.ticks_ms()
        inference_time = time.ticks_diff(end, start)
        out_probs = predictions[0].flatten().tolist()
        pred_idx  = out_probs.index(max(out_probs))
        pred      = pred_idx + 1 


        accel_x_mean   = sum(imu_buffer[j][0] for j in range(WINDOW_SIZE)) / WINDOW_SIZE
        accel_x_scaled = (accel_x_mean - SCALER_MEANS[0]) / SCALER_SCALES[0]


        if pred == 3 and accel_x_scaled < -0.9:
            pred = 6

        if pred == 7 and accel_x_scaled < -0.5:
            pred = 5

        pred    = smooth(pred)
        gesture = CLASS_NAMES.get(pred, "Unknown")

        print("Gesture:", gesture, "| Inference:", inference_time, "ms")

        try:
            pc_sock.sendto("{},{}".format(pred, gesture).encode(), (PC_IP, PC_PORT))
        except:
            pass

        gc.collect()
        time.sleep_ms(20)

    except Exception as e:
        sys.print_exception(e)
        time.sleep_ms(500)