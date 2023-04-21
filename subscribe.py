# python3.6

import random

from paho.mqtt import client as mqtt_client

broker = 'labdigi.wiseful.com.br'
port = 80
topic = "grupo1-bancadaB4/1"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'grupo1-bancadaB4'
password = 'digi#@1B4'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, received, function, questions):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        lastMsg = msg.payload.decode()
        function(questions[0])
    client.subscribe(topic)
    client.on_message = on_message


def run(received, function, questions):
    if (received == 0):
        client = connect_mqtt()
        subscribe(client,received, function, questions)
        client.loop_start()


if __name__ == '__main__':
    run()