import logging

from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener  # Import IDataMessageListener
# NOTE: We don't have a separate ISystemPerformanceDataListener or ITelemetryDataListener
#       We'll use IDataMessageListener for all listeners for now.  If you later
#       create more specific interfaces, you can add those imports.
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DeviceDataManager(IDataMessageListener):
    """
    Main data manager class for the Constrained Device Application.
    """

    def __init__(self, enableMqtt: bool = True, enableCoap: bool = True):
        self.configUtil = ConfigUtil()

        self.enableSystemPerf = \
            self.configUtil.getBoolean(
                section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_SYSTEM_PERF_KEY)

        self.enableSensing = \
            self.configUtil.getBoolean(
                section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.ENABLE_SENSING_KEY)

        self.enableActuation = True  # TODO: Get from config

        self.sysPerfMgr = None
        self.sensorAdapterMgr = None
        self.actuatorAdapterMgr = None

        self.mqttClient = None  # Will be initialized in Part III
        self.coapClient = None  # Will be initialized in Part III
        self.coapServer = None  # Not used in this example

        if self.enableSystemPerf:
            self.sysPerfMgr = SystemPerformanceManager()
            self.sysPerfMgr.setDataMessageListener(self)
            logging.info("Local system performance tracking enabled")

        if self.enableSensing:
            self.sensorAdapterMgr = SensorAdapterManager()
            self.sensorAdapterMgr.setDataMessageListener(self)
            logging.info("Local sensor tracking enabled")

        if self.enableActuation:
            self.actuatorAdapterMgr = ActuatorAdapterManager(dataMsgListener=self)
            logging.info("Local actuation capabilities enabled")

        self.handleTempChangeOnDevice = \
            self.configUtil.getBoolean(
                ConfigConst.CONSTRAINED_DEVICE, ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY)

        self.triggerHvacTempFloor = \
            self.configUtil.getFloat(
                ConfigConst.CONSTRAINED_DEVICE, ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY)

        self.triggerHvacTempCeiling = \
            self.configUtil.getFloat(
                ConfigConst.CONSTRAINED_DEVICE, ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY)

        # Caches for storing latest data
        self.actuatorResponseCache: dict[str, ActuatorData] = {}
        self.sensorDataCache: dict[str, SensorData] = {}
        self.sysPerfDataCache: dict[str, SystemPerformanceData] = {}

    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData | None:
        """Retrieves the named actuator data (response) from the cache."""
        if name:
            return self.actuatorResponseCache.get(name)
        return None

    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData | None:
        """Retrieves the named sensor data from the cache."""
        if name:
            return self.sensorDataCache.get(name)
        return None

    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData | None:
        """Retrieves the named system performance data from the cache."""
        if name:
            return self.sysPerfDataCache.get(name)
        return None

    def handleActuatorCommandMessage(self, data: ActuatorData = None) -> ActuatorData | None:
        """Handles an actuator command (sends it to the ActuatorAdapterManager)."""
        logging.info("Actuator data: %s", str(data))

        if data:
            logging.info("Processing actuator command message.")
            return self.actuatorAdapterMgr.handleActuation(data.getCommand(), data.getValue(), data.getStateData())
        else:
            logging.warning("Incoming actuator command is invalid (null). Ignoring.")
            return None

    def handleActuatorCommandResponse(self, data: ActuatorData = None) -> bool:
        """Handles an actuator command *response* (stores it in the cache)."""
        if data:
            logging.debug("Incoming actuator response received (from actuator manager): %s", str(data))

            # store the data in the cache
            self.actuatorResponseCache[data.getName()] = data

            # convert ActuatorData to JSON and get the msg resource
            actuatorMsg = DataUtil().actuatorDataToJson(data)
            resourceName = ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE

            # delegate to the transmit function any potential upstream comm's
            self._handleUpstreamTransmission(resourceName=resourceName, msg=actuatorMsg)

            return True
        else:
            logging.warning("Incoming actuator response is invalid (null). Ignoring.")
            return False

    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        """Handles an incoming message (currently just logs it)."""
        logging.info("Incoming message received: %s, Resource: %s", msg, resourceEnum.getFieldName())
        # TODO:  Add logic to handle different message types (e.g., JSON parsing)
        return True

    def handleSensorMessage(self, data: SensorData = None) -> bool:
        """Handles incoming sensor data (stores it and analyzes it)."""
        if data:
            logging.debug("Incoming sensor data received (from sensor manager): %s", str(data))
            self.sensorDataCache[data.getName()] = data
            self._handleSensorDataAnalysis(data=data)  # Corrected call
            return True
        else:
            logging.warning("Incoming sensor data is invalid (null). Ignoring.")
            return False

    def handleSystemPerformanceMessage(self, data: SystemPerformanceData = None) -> bool:
        """Handles incoming system performance data (stores it)."""
        if data:
            logging.debug("Incoming system performance message received (from sys perf manager): %s", str(data))
            self.sysPerfDataCache[data.getName()] = data
            return True
        else:
            logging.warning("Incoming system performance data is invalid (null). Ignoring.")
            return False

    def setSystemPerformanceDataListener(self, listener: IDataMessageListener = None):
        """Sets a listener for system performance data (not used in this example)."""
        # NOTE: This method is not currently used, but kept for potential future use
        pass

    def setTelemetryDataListener(self, name: str = None, listener: IDataMessageListener = None):
        """Sets a listener for telemetry data (not used in this example)."""
        # NOTE: This method is not currently used, but kept for potential future use
        pass
    def startManager(self):
        """Starts the managers (SystemPerformanceManager, SensorAdapterManager)."""
        logging.info("Starting DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.startManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.startManager()

        logging.info("Started DeviceDataManager.")

    def stopManager(self):
        """Stops the managers."""
        logging.info("Stopping DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.stopManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.stopManager()

        logging.info("Stopped DeviceDataManager.")

    def _handleIncomingDataAnalysis(self, msg: str):
        """
        Placeholder for handling incoming data analysis (currently does nothing).
        """
        # TODO: Implement data analysis logic
        pass

    def _handleSensorDataAnalysis(self, data: SensorData):
        """Handles temperature sensor data analysis and triggers HVAC if needed."""
        if self.handleTempChangeOnDevice and data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
            logging.info("Handle temp change: %s - type ID: %s", self.handleTempChangeOnDevice, data.getTypeID())

            ad = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
            ad.setName(ConfigConst.HVAC_ACTUATOR_NAME)

            if data.getValue() > self.triggerHvacTempCeiling:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempCeiling)  # Set to ceiling, not just ON
            elif data.getValue() < self.triggerHvacTempFloor:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempFloor) # Set to floor, not just ON
            else:
                ad.setCommand(ConfigConst.COMMAND_OFF)
                ad.setValue(0.0) #Set default value

            self.handleActuatorCommandMessage(ad) # Actually, its not needed to store in a variable

    def _handleUpstreamTransmission(self, resourceName: ResourceNameEnum, msg: str):
        """Placeholder for handling upstream data transmission (not used in NoComms test)."""
        # TODO: Implement upstream transmission logic (for Part III)
        pass