from bleak import BleakClient, BleakScanner
import paho.mqtt.client as mqtt
from multiprocessing import Process
from threading import Thread
import asyncio
import json
from mqtt_client import MQTT_Client

# Define Nordic Uart Service (NUS) characteristic UUIDs
UART_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX

# Global flag to check for new data
ax1_mqtt, ay1_mqtt, az1_mqtt = [], [], []
gx1_mqtt, gy1_mqtt, gz1_mqtt = [], [], []
ax2_mqtt, ay2_mqtt, az2_mqtt = [], [], []
gx2_mqtt, gy2_mqtt, gz2_mqtt = [], [], []

broker = MQTT_Client()

async def conn(address):
    async with BleakClient(address[1],) as client1, \
               BleakClient(address[0],) as client2:
        x = await client1.is_connected()
        print("Connected: {0}".format(x))
        x = await client2.is_connected()
        print("Connected: {0}".format(x))

        # Notification handler function, prints received data and sets dataFlag to True
        def notification_handler1(sender, data):
            print(f"Dev1 : {data}") 
            data = json.loads(data)
            ax1_mqtt.append(data["ax"])
            ay1_mqtt.append(data["ay"])
            az1_mqtt.append(data["az"])
            gx1_mqtt.append(data["gx"])
            gy1_mqtt.append(data["gy"])
            gz1_mqtt.append(data["gz"])
            task1 = Thread(target=check_list_1)
            task1.start()

        def notification_handler2(sender, data):
            print(f"Dev2 : {data}") 
            data = json.loads(data)
            ax2_mqtt.append(data["ax"])
            ay2_mqtt.append(data["ay"])
            az2_mqtt.append(data["az"])
            gx2_mqtt.append(data["gx"])
            gy2_mqtt.append(data["gy"])
            gz2_mqtt.append(data["gz"])
            task2 = Thread(target=check_list_2)
            task2.start()

        await client1.start_notify(UART_TX_UUID, notification_handler1)
        await client2.start_notify(UART_TX_UUID, notification_handler2)
        while True : 
            await asyncio.sleep(0)

async def async_main(address):
    try:
        await asyncio.gather(conn(address))
    except asyncio.TimeoutError:
        print("Finish")

def check_list_1():
    if len(gz1_mqtt) >= 10:
        msg = {"ax1":ax1_mqtt, "ay1":ay1_mqtt, "az1":az1_mqtt, "gx1":gx1_mqtt, "gy1":gy1_mqtt, "gz1":gz1_mqtt}
        json_payload = json.dumps(msg)
        try:
            broker.publish("ton/server/one", json_payload)
        except Exception as e:
            print(e)
        ax1_mqtt.clear()
        ay1_mqtt.clear()
        az1_mqtt.clear()
        gx1_mqtt.clear()
        gy1_mqtt.clear()
        gz1_mqtt.clear()  

def check_list_2():
    if len(gz2_mqtt) >= 10:
        msg = {"ax2":ax2_mqtt, "ay2":ay2_mqtt, "az2":az2_mqtt, "gx2":gx2_mqtt, "gy2":gy2_mqtt, "gz2":gz2_mqtt}
        json_payload = json.dumps(msg)
        try:
            broker.publish("ton/server/two", json_payload)
        except Exception as e:
            print(e)
        ax2_mqtt.clear()
        ay2_mqtt.clear()
        az2_mqtt.clear()
        gx2_mqtt.clear()
        gy2_mqtt.clear()
        gz2_mqtt.clear()

if __name__ == '__main__':
    address = (
        "E3:CD:91:AC:53:CD",                               # สำหรับตัวมีจอ
        "FF:09:AA:27:E2:E8",                               # สำหรับตัวเล็ก
    )

    data = asyncio.run(async_main(address))