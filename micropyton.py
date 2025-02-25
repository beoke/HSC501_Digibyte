import machine
import time
import network
import dht
import urequests  
import gc  

# Konfigurasi WiFi
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
    else:
        print("\n❌ Gagal terhubung! Periksa SSID dan Password.")
        return False
    
    return True

# Coba koneksi ke WiFi
if not connect_wifi():
    raise SystemExit()

sensor = dht.DHT11(machine.Pin(15))

led1 = machine.Pin(2, machine.Pin.OUT)
led2 = machine.Pin(4, machine.Pin.OUT)

# Konfigurasi API Ubidots
UBIDOTS_TOKEN = "BBUS-x3dQDcqmN4rtTqMgorTYDPlBE9hYGG"  
UBIDOTS_DEVICE = "esp32"  
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"

HEADERS = {
    "Content-Type": "application/json",
    "X-Auth-Token": UBIDOTS_TOKEN
}

# Menyimpan kondisi terakhir
last_condition = None  

def control_leds(mode):
    """Mengontrol LED sesuai mode ('bersamaan' atau 'bergantian')."""
    if mode == "bersamaan":
        for _ in range(5):  # Berkedip 5 kali
            led1.on()
            led2.on()
            time.sleep(0.5)
            led1.off()
            led2.off()
            time.sleep(0.5)

    elif mode == "bergantian":
        for _ in range(5):  # Berkedip 5 kali
            led1.on()
            led2.off()
            time.sleep(0.5)
            led1.off()
            led2.on()
            time.sleep(0.5)

while True:
    try:
        # Membaca suhu dan kelembaban dari sensor
        sensor.measure()
        suhu = sensor.temperature()
        kelembaban = sensor.humidity()

        print(f"🌡️ Suhu: {suhu}°C, 💧 Kelembaban: {kelembaban}%")

        # Kirim data sensor ke Ubidots
        data = {
            "suhu": suhu,
            "kelembaban": kelembaban
        }

        response = urequests.post(UBIDOTS_URL, json=data, headers=HEADERS)
        
        if response.status_code in [200, 201]:
            print("✅ Data berhasil dikirim ke Ubidots!")
        else:
            print(f"⚠️ Gagal mengirim data. Status Code: {response.status_code}")
        
        response.close()

        # **Mengontrol LED berdasarkan suhu**
        if suhu >= 27:
            print("🔥 Suhu ≥ 27°C: LED berkedip bersamaan")
            last_condition = "bersamaan"
        else:
            print("❄️ Suhu < 27°C: LED berkedip bergantian")
            last_condition = "bergantian"

        control_leds(last_condition)  # Jalankan LED sesuai kondisi terbaru

    except OSError as e:
        print(f"❌ Error membaca sensor: {e}")
        print("⚠️ Tidak ada pembaruan, menjalankan mode terakhir:", last_condition)
        if last_condition:
            control_leds(last_condition)  # Gunakan kondisi terakhir jika terjadi error

    except Exception as e:
        print(f"⚠️ Error lain: {e}")

    gc.collect()  
    time.sleep(0.5)  
