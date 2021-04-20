import stmpy

from .device import Device
from .receiver import Receiver
from .ack_timout import ackTimeout
# from .ui import UI

device = Device()
driver = Driver()
driver.add_machine(device.stm)
driver.start()




