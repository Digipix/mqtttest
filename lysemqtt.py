import time
import paho.mqtt.client as paho
import json
import config
import requests
broker="test.mosquitto.org"

#broker="iot.eclipse.org"
#define callback
def on_message(client, userdata, message):


    time.sleep(1)
    print("received message =",str(message.payload.decode("utf-8")))
    #print(message.topic + " " + str(message.qos) + " " + str(message.payload))
    m_decode = str(message.payload.decode("utf-8", "ignore"))
    m_in = json.loads(m_decode)
    #print(type(m_in))
    #print("Value = ", m_in["value"])
    #print("Time = ", m_in["timestamp"])

    value = m_in["value"]
    timestamp = m_in["timestamp"]

    #treshold = 50
    times_to_wait = 30  # 6 ganger per minutt * 5 minutter

    if value < config.treshold:
        config.over_treshold_counter = 0
        print("Under treshold")
        config.under_treshold_counter = config.under_treshold_counter + 1
        print("under_treshold_counter =", config.under_treshold_counter)

        if config.under_treshold_counter > times_to_wait:
            config.warning_sent = False
            print("warning ready to send")

    else: # over treshold
        config.under_treshold_counter = 0
        print("Over treshold")
        config.over_treshold_counter = config.over_treshold_counter + 1

        print("over_treshold_counter =", config.over_treshold_counter)

        if config.over_treshold_counter > times_to_wait:
            if config.warning_sent:
                print("warning already sent")
            else:

                print("Send warning")
                config.warning_sent = True
    data = {}
    data["message"] = "Treshold value exceeded"
    data["lastSensorTimestamp"] = timestamp
    data["lastSensorValue"] = value
    print("data", data)

    response = requests.post(config.warning_url, data = data)
    print("RESP", response.text)



config.treshold = float(input("Terskelverdi? "))
config.warning_url = input("URL til server for varsel? (Blank hvis du ønsker testserver): ")

if len(config.warning_url) < 1:
    config.warning_url = "https://jsonplaceholder.typicode.com/posts"

print("Url:", config.warning_url)
client= paho.Client("client-001")
#create client object client1.on_publish = on_publish

######Bind function to callback
client.on_message=on_message
#####
print("connecting to broker ",broker)
client.connect(broker)#connect
client.loop_start() #start loop to process received messages
print("subscribing ")
client.subscribe("sensors/lyse-test-01")#subscribe
time.sleep(10)

client.disconnect() #disconnect
client.loop_stop() #stop loop