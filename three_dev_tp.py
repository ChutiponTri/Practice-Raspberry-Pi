from wifi_check import check_wifi_connected
while not check_wifi_connected():
    print("WiFi is not connected.")
print("WiFi is connected.")
from bleak import BleakClient, BleakScanner
from multiprocessing import Process
from datetime import datetime, timedelta
from threading import Thread
import numpy as np
import asyncio
import json
from mqtt_client import MQTT_Client
from line_bot import line_bot, send_plot_to_line
from line_notify import user

today = datetime.now().day

# Define Nordic Uart Service (NUS) characteristic UUIDs
UART_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX
UART_HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# List of MQTT Data
ax1_mqtt, ay1_mqtt, az1_mqtt = [], [], []
gx1_mqtt, gy1_mqtt, gz1_mqtt = [], [], []
ax2_mqtt, ay2_mqtt, az2_mqtt = [], [], []
gx2_mqtt, gy2_mqtt, gz2_mqtt = [], [], []

data_dict = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0}
hr_dict = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0}

hour = datetime.now().hour

broker = MQTT_Client()

running = True

ret = False

def discon_callback(sender):
    print("Disconnected from", sender.address)
    global ret 
    ret = True

async def conn(address):
    while True:
        if ret:
            return
        try:
            async with BleakClient(address[0], disconnected_callback=discon_callback) as client1, \
                    BleakClient(address[1], disconnected_callback=discon_callback) as client2, \
                    BleakClient(address[2], disconnected_callback=discon_callback) as client3:
                x = client1.is_connected
                print("Connected: {0}".format(x))
                x = client2.is_connected
                print("Connected: {0}".format(x))
                x = client3.is_connected
                print("Connected: {0}".format(x))

                # Notification handler function, prints received data and sets dataFlag to True
                def notification_handler1(sender, data):
                    # print(f"Dev1 : {data}") 
                    data = json.loads(data)
                    ax1_mqtt.append(data["ax"])
                    ay1_mqtt.append(data["ay"])
                    az1_mqtt.append(data["az"])
                    gx1_mqtt.append(data["gx"])
                    gy1_mqtt.append(data["gy"])
                    gz1_mqtt.append(data["gz"])
                    task_1 = Thread(target=check_list_1)
                    task_1.start()

                def notification_handler2(sender, data):
                    # print(f"Dev2 : {data}") 
                    data = json.loads(data)
                    ax2_mqtt.append(data["ax"])
                    ay2_mqtt.append(data["ay"])
                    az2_mqtt.append(data["az"])
                    gx2_mqtt.append(data["gx"])
                    gy2_mqtt.append(data["gy"])
                    gz2_mqtt.append(data["gz"])
                    task_2 = Thread(target=check_list_2)
                    task_2.start()

                def notification_handler_hr(sender, data):
                    # print(f"Dev2 : {data}") 
                    data = decode(data)
                    task_hr = Thread(target=check_hr, args=(data,))
                    task_hr.start()

                await client1.start_notify(UART_TX_UUID, notification_handler1)
                await client2.start_notify(UART_TX_UUID, notification_handler2)
                await client3.start_notify(UART_HR_UUID, notification_handler_hr)
                while True : 
                    if ret:
                        return
                    await asyncio.sleep(0)
        except Exception as E:
            await asyncio.sleep(1)
            print(E)

async def day_check():
    while True:
        if ret:
            return
        now = datetime.now().day
        global today
        if now != today:
            for key in data_dict:
                data_dict[key] = 0
                hr_dict[key] = 0
            today = now
            date = datetime.now() - timedelta(days=1)
            message = "%s moves total of %.2f meters in %s with average heart rate of %d bpm\nHere's overview of motion data" % (user, np.sum(list(data_dict.values())), date.strftime("%d-%m-%Y"), np.mean(list(hr_dict.values())))
            send = Thread(target=send_plot_to_line, args=(data_dict, hr_dict, message))
            send.start()
            print("It's a new day")

        global hour 
        timestamp = datetime.now()
        time_delta = timestamp.hour - hour
        # time_delta = 1
        hour += time_delta
        message = "%s moves total of %.2f meters in %s with average heart rate of %d bpm\nHere's overview of motion data" % (user, np.sum(list(data_dict.values())), (timestamp-timedelta(days=1)).strftime("%d-%m-%Y"), np.mean(list(hr_dict.values())))
        # send = Thread(target=send_plot_to_line, args=(data_dict, hr_dict, message))
        # send.start()
        await asyncio.sleep(1)

def check_list_1():
    if len(gz1_mqtt) >= 10:
        msg = {"ax1":ax1_mqtt, "ay1":ay1_mqtt, "az1":az1_mqtt, "gx1":gx1_mqtt, "gy1":gy1_mqtt, "gz1":gz1_mqtt}
        json_payload = json.dumps(msg)
        try:
            broker.publish("ton/server/one", json_payload)
        except Exception as e:
            print(e)
        update_dist()
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

def update_dist():
    if len(gz1_mqtt) >= 10:
        dist = np.max(np.cumsum(np.deg2rad(np.abs(gz1_mqtt))) / 10 * 0.3)
        if (dist > 0.005):
            data_dict[str(hour)] += dist

def check_hr(hr):
    json_payload = json.dumps(hr)
    try:
        broker.publish("ton/server/hr", json_payload)
    except Exception as e:
        print(e)
    hr_dict[str(hour)] = hr["hr"]
    
def decode(data: bytearray):
    """
    See www.bluetooth.com/specifications/specs/heart-rate-service-1-0/ 
    for the structure of the frame.
    NOTE: Polar H10 does not support contact bit or energy expenditure,
    so these features are untested
    """
    # the first byte contains flags
    flags = data[0]
    payload={}

    # format for hr: 1 or 2 bits, little endian
    uint8_format = (flags & 1) == 0  # bit 0, can change
    energy_expenditure = (flags & 8)>0 # bit 3, can change
    rr_intervals = (flags & 16) >0  # bit 4, can change
    
    contact_detection= (flags & 4) > 0 # bit 2, static
    if contact_detection:
        # good contact if bit is set
        payload['contact']= (flags & 2) >0 # bit 1, can change
        
    if uint8_format:
        payload['hr'] = data[1]
        offset=2
    else:
        payload['hr'] = int.from_bytes(data[1:3], 'little', signed=False)
        offset=3
    if energy_expenditure:
        nrg = int.from_bytes(data[offset:offset+2], 'little', signed=False)
        offset += 2
        payload['nrg']=nrg

    if rr_intervals:
        payload['rr']=[]
        for i in range(offset, len(data), 2):
            rr = int.from_bytes(data[i:i+2],
                                'little', signed=False)
            # Polar H7, H9, and H10 record RR intervals
            # in 1024-th parts of a second. Convert this
            # to milliseconds.
            rr = round(rr * 1000 / 1024)
            payload['rr'].append(rr)
    return payload

# Async Function To Check Whether Wheelchair is Falling
async def falling_detection():
    count_1 = 0
    count_2 = 0
    message = "Alert !! %s has fallen !" % user

    while True:
        if ret:
            return
        try:
            await asyncio.sleep(1)
            if len(ax1_mqtt) > 0:
                if (-0.7 < az1_mqtt[-1] < 0.7):
                    count_1 = 0
                else:
                    count_1 += 1
                    if count_1 % 10 == 5:
                        try:
                            # tasks = [line_bot(i) for i in user_ids]
                            # await asyncio.gather(*task)
                            task = Thread(target=line_bot, args=(message,))
                            task.start()
                        except:
                            print("Please Connect to the internet")

            if len(ax2_mqtt) > 0:
                if (-0.7 < az2_mqtt[-1] < 0.7):
                    count_2 = 0
                else:
                    count_2 += 1
                    if count_2 % 10 == 5:
                        try:
                            task = Thread(target=line_bot, args=(message,))
                            task.start()
                        except:
                            print("Please Connect to the internet")
        except Exception as e:
            print("Fall", e)

async def async_main(address):
    while True:
        global ret
        ret = False
        try:
            print("Start")
            task = [
                conn(address),
                falling_detection(),
                day_check(),
            ]
            await asyncio.gather(*task)
        except asyncio.TimeoutError:
            print("Finish")
        except KeyboardInterrupt:
            print("Bye")
    
def run(address):
    asyncio.run(async_main(address))

if __name__ == '__main__':
    address = (
        "E3:CD:91:AC:53:CD",                               # สำหรับตัวมีจอ
        "FF:09:AA:27:E2:E8",                               # สำหรับตัวเล็ก
        "A0:9E:1A:C3:59:40",
    )

    process = Process(target=run, args=(address,))
    process.start()
