# python 3.6

import random
import time, sched

from paho.mqtt import client as mqtt_client
broker = 'labdigi.wiseful.com.br'
port = 80
topic = "grupo1-bancadaB4/Q1"
# generate client ID with pub poprefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'grupo1-bancadaB4'
password = 'digi#@1B4'
value = 0
array = [0,1,2]

def connect_mqtt():
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


def test_publish(client):
    msg_count = 0
    while True:
        value = 1
        while (value != 0):
            rand = random.randint(0,31)
            value = array.count(rand)
            if (value != 0):
                array.remove(rand)
            msg = f"{rand}"
            count = 0
        while(count < 10):
            time.sleep(0.5)
            result = client.publish(topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")
            msg_count += 1
            count += 1

def p_publish(client,msg,p_topic):
    msg_count = 0
    s_msg = f"{msg}"
    result = client.publish(p_topic, s_msg)
    status = result[0]
    if status == 0:
        print(f"Send `{s_msg}` to topic `{p_topic}`")
    else:
        print(f"Failed to send message to topic {p_topic}")
    msg_count += 1




def run():
    client = connect_mqtt()
    client.loop_start()
    test_publish(client)


#if __name__ == '__main__':
#run()

#run()
