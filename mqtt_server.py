import paho.mqtt.client as mqtt
import pyautogui
import json

class MQTT_Server():
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        broker_address = "broker.emqx.io"
        broker_port = 1883
        try:
            self.client.connect(broker_address, broker_port)
        except Exception as e:
            print(e)

    def on_connect(self, client, userdata, connect_flags, reason_code, properties):
        self.client.subscribe("ton/server/#")
        print(f"MQTT Connected {reason_code}")

    def on_message(self, client, userdata, message):
        print(message.payload)
        # data = json.loads(message.payload)
        # if data["gz1"][0] > 100:
        #     pyautogui.press("up")
        # elif data["gz1"][0] < -100:
        #     pyautogui.press("down")

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        print("Disconnected", reason_code)
        self.client.reconnect()

if __name__ == '__main__':
    server = MQTT_Server()
    server.client.loop_forever()