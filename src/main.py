import stmpy
import paho.mqtt.client as mqtt

from .device import Device
from .receiver import Receiver
from .ack_timout import AckTimeout
# from .ui import UI
mqtt_client = mqtt.Client()

device = Device(mqtt_client)
receiver = Receiver(mqtt_client)
ackTimeout = AckTimeout(mqtt_client)
driver = Driver()
driver.add_machine(device.stm)
driver.add_machine(ackTimeout.stm)
driver.add_machine(receiver.stm)
driver.start()
