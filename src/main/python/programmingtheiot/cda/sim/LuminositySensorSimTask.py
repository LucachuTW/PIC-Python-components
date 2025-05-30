#####
# Simulación de sensor de luminosidad

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.common.ConfigUtil import ConfigUtil

class LuminositySensorSimTask(BaseSensorSimTask):
    def __init__(self, dataSet=None):
        configUtil = ConfigUtil()
        
        # Get configuration values for luminosity simulation
        minVal = configUtil.getFloat(
            ConfigConst.CONSTRAINED_DEVICE, 
            ConfigConst.LUMINOSITY_SIM_FLOOR_KEY,
            SensorDataGenerator.DEFAULT_MIN_VALUE
        )
        
        maxVal = configUtil.getFloat(
            ConfigConst.CONSTRAINED_DEVICE, 
            ConfigConst.LUMINOSITY_SIM_CEILING_KEY,
            SensorDataGenerator.DEFAULT_MAX_VALUE
        )
        
        if dataSet is None:
            # Si no se pasa un dataset, generamos uno por defecto
            dataSet = SensorDataGenerator().generateDailySensorDataSet(
                curveType=SensorDataGenerator.FULL_WAVE,
                noiseLevel=SensorDataGenerator.DEFAULT_NOISE,
                minValue=minVal,
                maxValue=maxVal,
                startHour=0,
                endHour=24,
                useSeconds=False
            )
        super().__init__(
            name=ConfigConst.LUMINOSITY_SENSOR_NAME,
            typeID=ConfigConst.LUMINOSITY_SENSOR_TYPE,
            dataSet=dataSet,
            minVal=minVal,
            maxVal=maxVal
        )
