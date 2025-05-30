#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging

from importlib import import_module

from apscheduler.schedulers.background import BackgroundScheduler

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorSimTask
from programmingtheiot.cda.sim.TemperatureSensorSimTask import TemperatureSensorSimTask
from programmingtheiot.cda.sim.PressureSensorSimTask import PressureSensorSimTask
from programmingtheiot.cda.sim.LuminositySensorSimTask import LuminositySensorSimTask

class SensorAdapterManager(object):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self):
		self.configUtil = ConfigUtil()

		self.pollRate     = \
			self.configUtil.getInteger( \
				section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.POLL_CYCLES_KEY, defaultVal = ConfigConst.DEFAULT_POLL_CYCLES)

		self.useEmulator  = \
			self.configUtil.getBoolean( \
				section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.ENABLE_EMULATOR_KEY)

		self.locationID   = \
			self.configUtil.getProperty( \
				section = ConfigConst.CONSTRAINED_DEVICE, key = ConfigConst.DEVICE_LOCATION_ID_KEY, defaultVal = ConfigConst.NOT_SET)

		if self.pollRate <= 0:
			self.pollRate = ConfigConst.DEFAULT_POLL_CYCLES

		# technically we only need 1 instance - important to set coalesce
		# to True and allow for misfire grace period
		self.scheduler = BackgroundScheduler()
		self.scheduler.add_job( \
			self.handleTelemetry, 'interval', seconds = self.pollRate, max_instances = 2, coalesce = True, misfire_grace_time = 15)

		self.dataMsgListener = None
		self.humidityAdapter = None
		self.pressureAdapter = None
		self.tempAdapter     = None
		self.luminosityAdapter = None

		# see PIOT-CDA-03-006 description for thoughts on the next line of code
		self._initEnvironmentalSensorTasks()

	def _initEnvironmentalSensorTasks(self):
		humidityFloor = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.HUMIDITY_SIM_FLOOR_KEY, defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY
		)
		humidityCeiling = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.HUMIDITY_SIM_CEILING_KEY, defaultVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY
		)

		pressureFloor = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.PRESSURE_SIM_FLOOR_KEY, defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE
		)
		pressureCeiling = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.PRESSURE_SIM_CEILING_KEY, defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE
		)

		tempFloor = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.TEMP_SIM_FLOOR_KEY, defaultVal=SensorDataGenerator.LOW_NORMAL_INDOOR_TEMP
		)
		tempCeiling = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=ConfigConst.TEMP_SIM_CEILING_KEY, defaultVal=SensorDataGenerator.HI_NORMAL_INDOOR_TEMP
		)

		luminosityFloor = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=getattr(ConfigConst, 'LUMINOSITY_SIM_FLOOR_KEY', 'luminositySimFloor'), defaultVal=SensorDataGenerator.DEFAULT_MIN_VALUE
		)
		luminosityCeiling = self.configUtil.getFloat(
			section=ConfigConst.CONSTRAINED_DEVICE, key=getattr(ConfigConst, 'LUMINOSITY_SIM_CEILING_KEY', 'luminositySimCeiling'), defaultVal=SensorDataGenerator.DEFAULT_MAX_VALUE
		)

		if not self.useEmulator:
			self.dataGenerator = SensorDataGenerator()

			humidityData = self.dataGenerator.generateDailyEnvironmentHumidityDataSet(
				minValue=humidityFloor, maxValue=humidityCeiling, useSeconds=False
			)
			pressureData = self.dataGenerator.generateDailyEnvironmentPressureDataSet(
				minValue=pressureFloor, maxValue=pressureCeiling, useSeconds=False
			)
			tempData = self.dataGenerator.generateDailyIndoorTemperatureDataSet(
				minValue=tempFloor, maxValue=tempCeiling, useSeconds=False
			)
			luminosityData = self.dataGenerator.generateDailySensorDataSet(
				curveType=SensorDataGenerator.FULL_WAVE, noiseLevel=SensorDataGenerator.DEFAULT_NOISE, minValue=luminosityFloor, maxValue=luminosityCeiling, startHour=0, endHour=24, useSeconds=False
			)

			self.humidityAdapter = HumiditySensorSimTask(dataSet=humidityData)
			self.pressureAdapter = PressureSensorSimTask(dataSet=pressureData)
			self.tempAdapter = TemperatureSensorSimTask(dataSet=tempData)
			self.luminosityAdapter = LuminositySensorSimTask(dataSet=luminosityData)

		else:
			heModule = import_module('programmingtheiot.cda.emulated.HumiditySensorEmulatorTask')
			heClazz = getattr(heModule, 'HumiditySensorEmulatorTask')
			self.humidityAdapter = heClazz()

			peModule = import_module('programmingtheiot.cda.emulated.PressureSensorEmulatorTask')
			peClazz = getattr(peModule, 'PressureSensorEmulatorTask')
			self.pressureAdapter = peClazz()

			teModule = import_module('programmingtheiot.cda.emulated.TemperatureSensorEmulatorTask')
			teClazz = getattr(teModule, 'TemperatureSensorEmulatorTask')
			self.tempAdapter = teClazz()

			try:
				leModule = import_module('programmingtheiot.cda.emulated.LuminositySensorEmulatorTask')
				leClazz = getattr(leModule, 'LuminositySensorEmulatorTask')
				self.luminosityAdapter = leClazz()
			except Exception:
				self.luminosityAdapter = None



	def handleTelemetry(self):
		humidityData = self.humidityAdapter.generateTelemetry()
		pressureData = self.pressureAdapter.generateTelemetry()
		tempData     = self.tempAdapter.generateTelemetry()
		luminosityData = self.luminosityAdapter.generateTelemetry() if self.luminosityAdapter else None

		humidityData.setLocationID(self.locationID)
		pressureData.setLocationID(self.locationID)
		tempData.setLocationID(self.locationID)

		logging.debug('Generated humidity data: ' + str(humidityData))
		logging.debug('Generated pressure data: ' + str(pressureData))
		logging.debug('Generated temp data: ' + str(tempData))

		if self.dataMsgListener:
			self.dataMsgListener.handleSensorMessage(humidityData)
			self.dataMsgListener.handleSensorMessage(pressureData)
			self.dataMsgListener.handleSensorMessage(tempData)
		
		if luminosityData:
			luminosityData.setLocationID(self.locationID)
			logging.debug('Generated luminosity data: ' + str(luminosityData))
			if self.dataMsgListener:
				self.dataMsgListener.handleSensorMessage(luminosityData)

	def setDataMessageListener(self, listener: IDataMessageListener):
		if listener:
			self.dataMsgListener = listener

	def startManager(self) -> bool:
		logging.info("Started SensorAdapterManager.")

		if not self.scheduler.running:
			self.scheduler.start()
			return True
		else:
			logging.info("SensorAdapterManager scheduler already started. Ignoring.")
			return False

	def stopManager(self) -> bool:
		logging.info("Stopped SensorAdapterManager.")

		try:
			self.scheduler.shutdown()
			return True
		except:
			logging.info("SensorAdapterManager scheduler already stopped. Ignoring.")
			return False
