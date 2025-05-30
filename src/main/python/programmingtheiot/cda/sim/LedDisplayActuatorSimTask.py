#####
# Simulación de actuador display LED

import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class LedDisplayActuatorSimTask(BaseActuatorSimTask):
    def __init__(self):
        super().__init__(
            name=ConfigConst.LED_ACTUATOR_NAME,
            typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE,
            simpleName="LED_DISPLAY"
        )
        
    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Simulates turning on the LED display with the given value/state data.
        
        @param val The value to display
        @param stateData The string to display
        @return int 0 on success; non-zero on failure
        """
        msg = f"{self.getSimpleName()} ON: Value={val}"
        if stateData:
            msg += f", State={stateData}"
            
        logging.info(msg)
        return 0
        
    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Simulates turning off the LED display.
        
        @param val The value that was being displayed
        @param stateData The string that was being displayed
        @return int 0 on success; non-zero on failure
        """
        logging.info(f"{self.getSimpleName()} OFF")
        return 0
