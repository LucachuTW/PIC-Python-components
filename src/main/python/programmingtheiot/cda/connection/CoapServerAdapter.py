#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging

from threading import Thread
from time import sleep

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.handlers.GetTelemetryResourceHandler import GetTelemetryResourceHandler
from programmingtheiot.cda.connection.handlers.UpdateActuatorResourceHandler import UpdateActuatorResourceHandler
from programmingtheiot.cda.connection.handlers.GetSystemPerformanceResourceHandler import GetSystemPerformanceResourceHandler

class CoapServerAdapter():
	"""
	Definition for a CoAP communications server, with embedded test functions.
	
	"""
	
	def __init__(self, dataMsgListener = None):
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False

		# NOTE: host may need to be the actual IP address - see Kanban board notes
		self.host = self.config.getProperty(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
		self.port = self.config.getInteger(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_COAP_PORT)

		self.coapServer     = None
		self.coapServerTask = None

		# NOTE: the self.rootResource = None only used for aiocoap
		self.rootResource   = None

		# NOTE: the self.listenTimeout = 30 only used for CoAPthon3
		# self.listenTimeout = 30

		logging.info("CoAP server configured for host and port: coap://%s:%s", self.host, str(self.port))
			

	def _initServer(self):
		pass

	def _runServer(self):
		pass

	def addResource(self, resourcePath: ResourceNameEnum = None, endName: str = None, resource = None):
		pass
				
	def startServer(self):
		pass
	
	def stopServer(self):
		pass
	
	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		pass
