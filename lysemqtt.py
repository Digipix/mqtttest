# April 2018

# Sverre Stendal

# inspiration from http://www.steves-internet-guide.com/python-mqtt-publish-subscribe/
# and https://stackoverflow.com/questions/42473168/send-http-post-with-python
# and https://pythonspot.com/json-encoding-and-decoding-with-python/


import time
import paho.mqtt.client as paho
import json
import requests

# here we get the sensor value
broker = "test.mosquitto.org"

# set the threshold value. A good value is 50
threshold = float(input("Terskelverdi? "))

# where to send the warning message
warning_url = input("URL til server for varsel? (Trykk ENTER hvis du ønsker default): ")

# counts how many times we get a sensor value below the threshold
under_threshold_counter = 0

# counts how many times we get a sensor value above the threshold
over_threshold_counter = 0

# a boolean variable to check if a warning is already sent
warning_sent = False


def on_message(client, userdata, message):
    # not optimal to use global variables...
    global under_threshold_counter
    global over_threshold_counter
    global warning_sent
    global threshold
    global warning_url
    time.sleep(1)
    print("received message =", str(message.payload.decode("utf-8")))
    json_message_to_decode = str(message.payload.decode("utf-8", "ignore"))
    decoded_json_message = json.loads(json_message_to_decode)

    # current timestamp and sensorvalue
    value = decoded_json_message["value"]
    timestamp = decoded_json_message["timestamp"]

    # We must wait 5 minutes before we can send a warning
    times_to_wait = 30  # 6 times per minute * 5 minutes

    if value < threshold:  # below threshold

        # first we reset the over_threshold_counter
        over_threshold_counter = 0
        print("Value is below threshold")

        # start counting how many times we are below threshold
        under_threshold_counter = under_threshold_counter + 1
        print("under_threshold_counter =", under_threshold_counter)

        # if we have waited 5 minutes below threshold, we can allow a new warning to be sent
        if under_threshold_counter > times_to_wait:
            warning_sent = False
            print("warning ready to send")

    else:  # above threshold

        # first we reset the under_threshold_counter
        under_threshold_counter = 0
        print("Value is above threshold")

        # start counting how many times we are above threshold
        over_threshold_counter = over_threshold_counter + 1
        print("over_threshold_counter =", over_threshold_counter)

        # if we have waited 5 minutes above threshold, we can send one warning message
        if over_threshold_counter > times_to_wait:
            # first we check if a recent warning was sent
            if warning_sent:
                print("warning already sent")
            else:
                # SENDING THE WARNING HERE !!!!
                print("Send warning")
                data = dict()
                data["message"] = "threshold value exceeded"
                data["lastSensorTimestamp"] = timestamp
                data["lastSensorValue"] = value
                # here we need to add some error handling (try / except)
                response = requests.post(warning_url, data=data)
                print("Response from server: ", response.text)
                warning_sent = True


# set a default url if the user presses ENTER without adding an url
if len(warning_url) < 1:
    warning_url = "http://jsonplaceholder.typicode.com/posts"

print('Valgt Url:', warning_url)
client = paho.Client("client-001")
client.on_message = on_message
print("connecting to broker ", broker)

# here we need to add some error handling (try / except)
client.connect(broker)  # connect
print("subscribing ")
client.subscribe("sensors/lyse-test-01")  # subscribe
client.loop_forever()

