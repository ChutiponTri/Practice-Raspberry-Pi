import paho.mqtt.client as mqtt

class MQTT_Client():
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect

        broker_address = "broker.emqx.io"
        broker_port = 1883
        try:
            self.client.connect(broker_address, broker_port)
        except Exception as e:
            print(e)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def on_connect(self, client, userdata, connect_flags, reason_code, properties):
        print(f"MQTT Connected {reason_code}")

    def on_publish(self, client, userdata, mid, reason_code, properties):
        pass

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        print("Disconnected", reason_code)
        self.client.reconnect()

if __name__ == '__main__':
    client = MQTT_Client()
    client.client.publish("ton/server/get", "Sam")