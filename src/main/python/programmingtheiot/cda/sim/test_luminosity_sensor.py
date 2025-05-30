import logging
from programmingtheiot.cda.sim.LuminositySensorSimTask import LuminositySensorSimTask

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sensor = LuminositySensorSimTask()
    data = sensor.generateTelemetry()
    print(f"Luminosity Sensor Data: value={data.getValue()}, name={data.getName()}, typeID={data.getTypeID()}")
