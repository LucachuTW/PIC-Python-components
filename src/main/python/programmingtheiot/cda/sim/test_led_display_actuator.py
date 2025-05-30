import logging
from programmingtheiot.cda.sim.LedDisplayActuatorSimTask import LedDisplayActuatorSimTask
from programmingtheiot.data.ActuatorData import ActuatorData
import programmingtheiot.common.ConfigConst as ConfigConst

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    actuator = LedDisplayActuatorSimTask()
    data = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE, name=ConfigConst.LED_ACTUATOR_NAME)
    data.setCommand(ConfigConst.COMMAND_ON)
    data.setValue(100.0)
    response = actuator.updateActuator(data)
    print(f"LedDisplay Actuator Response: command={response.getCommand()}, value={response.getValue()}, isResponse={response.isResponseFlagEnabled()}")
