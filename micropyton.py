import machine
import time
import network
import dht
import urequests  
import gc  

SSID = "KELAS INDUSTRI RPL"
PASSWORD = "Skansaba_123!"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("🔄 Menghubungkan ke WiFi...", end="")
    timeout = 10  
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print("\n✅ Terhubung ke WiFi")
        print(f"📶 IP Address: {wlan.ifconfig()[0]}")
        return True
    else:
        print("\n❌ Gagal terhubung! Periksa SSID dan Password.")
        return False

def reconnect_wifi():
    """Coba hubungkan ulang WiFi jika koneksi terputus."""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("🔄 Koneksi WiFi hilang. Menghubungkan ulang...")
        connect_wifi()

if not connect_wifi():
    raise SystemExit()

sensor = dht.DHT11(machine.Pin(15))

led1 = machine.Pin(2, machine.Pin.OUT)
led2 = machine.Pin(4, machine.Pin.OUT)

UBIDOTS_TOKEN = "BBUS-x3dQDcqmN4rtTqMgorTYDPlBE9hYGG"  
UBIDOTS_DEVICE = "esp32"  
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"
FLASK_ENDPOINT = "http://192.168.2.4:5000/save"

HEADERS = {"Content-Type": "application/json", "X-Auth-Token": UBIDOTS_TOKEN}
HEADERS_FLASK = {"Content-Type": "application/json"}

data = {
    "suhu": 0,
    "kelembaban": 0
}

def control_leds(mode):
    """Mengontrol LED sesuai mode ('bersamaan' atau 'bergantian')."""
    if mode == "bersamaan":
        for _ in range(5):
            led1.on()
            led2.on()
            time.sleep(0.5)
            led1.off()
            led2.off()
            time.sleep(0.5)
    elif mode == "bergantian":
        for _ in range(5):
            led1.on()
            led2.off()
            time.sleep(0.5)
            led1.off()
            led2.on()
            time.sleep(0.5)

last_condition = None

while True:
    try:
        reconnect_wifi()  

        sensor.measure()
        suhu = sensor.temperature()
        kelembaban = sensor.humidity()

        print(f"🌡️ Suhu: {suhu}°C, 💧 Kelembaban: {kelembaban}%")

        data["suhu"] = suhu
        data["kelembaban"] = kelembaban

        try:
            response = urequests.post(UBIDOTS_URL, json=data, headers=HEADERS)
            if response.status_code in [200, 201]:
                print("✅ Data berhasil dikirim ke Ubidots!")
            else:
                print(f"⚠️ Gagal mengirim data ke Ubidots. Status Code: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"❌ Gagal mengirim data ke Ubidots: {e}")

        try:
            response = urequests.post(FLASK_ENDPOINT, json=data, headers=HEADERS_FLASK)
            print(f"✅ Data berhasil dikirim ke Flask! Status: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"❌ Gagal mengirim data ke Flask: {e}")

        if suhu >= 27:
            print("🔥 Suhu ≥ 27°C: LED berkedip bersamaan")
            last_condition = "bersamaan"
        else:
            print("❄️ Suhu < 27°C: LED berkedip bergantian")
            last_condition = "bergantian"

        control_leds(last_condition)

    except OSError as e:
        print(f"❌ Error membaca sensor: {e}")
        if last_condition:
            control_leds(last_condition)

    except Exception as e:
        print(f"⚠️ Error lain: {e}")

    gc.collect()
    time.sleep(2)  
