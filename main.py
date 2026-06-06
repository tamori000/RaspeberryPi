import network
import socket
import time

SSID = "PicoW_Drone"
PASSWORD = "12345678"

# =========================
# Pico Wをアクセスポイント化
# =========================
ap = network.WLAN(network.AP_IF)
ap.active(False)
time.sleep(1)

ap.active(True)
ap.config(ssid=SSID, password=PASSWORD)

time.sleep(2)

ip = ap.ifconfig()[0]

print("Access Point started")
print("SSID:", SSID)
print("Password:", PASSWORD)
print("Pico IP:", ip)

# =========================
# UDPサーバー開始
# =========================
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

# タイムアウトを設定
# 通信が途切れたら安全値に戻すため
sock.settimeout(0.2)

print("UDP server listening on", ip, "port", PORT)

# 初期値：安全状態
roll = 1500
pitch = 1500
throttle = 1000
yaw = 1500

last_receive_time = time.ticks_ms()

while True:
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()

        print("Received from", addr, ":", message)

        values = message.split(",")

        if len(values) == 4:
            new_roll = int(values[0])
            new_pitch = int(values[1])
            new_throttle = int(values[2])
            new_yaw = int(values[3])

            # 値を安全範囲に制限
            roll = max(1000, min(2000, new_roll))
            pitch = max(1000, min(2000, new_pitch))
            throttle = max(1000, min(2000, new_throttle))
            yaw = max(1000, min(2000, new_yaw))

            last_receive_time = time.ticks_ms()

            print("CH:", roll, pitch, throttle, yaw)

    except OSError:
        # UDP受信タイムアウト
        pass

    # 500ms以上PCから信号が来なければ安全値へ戻す
    if time.ticks_diff(time.ticks_ms(), last_receive_time) > 500:
        roll = 1500
        pitch = 1500
        throttle = 1000
        yaw = 1500

    # ここで後ほどフライトコントローラーへ出力する
    # 例：
    # send_to_flight_controller(roll, pitch, throttle, yaw)