# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
import json
from rasa_core_sdk import Action
from rasa_core_sdk.endpoint import *

logger = logging.getLogger(__name__)

import sys
current_module = sys.modules[__name__]

#'tracker' object reference: https://rasa.com/docs/core/api/tracker/
#'dispatcher' object reference: https://rasa.com/docs/core/api/dispatcher/

class ActionPlanner(Action):
	def name(self):
		# define the name of the action which can then be included in training stories
		return "action_planner"

	def run(self, dispatcher, tracker, domain):
		#print(json.dumps(tracker.current_state(), indent=2))
		intent = tracker.latest_message["intent"].get("name")
		entities = [{"entity": x.get("entity"), "value": x.get("value")} for x in tracker.latest_message.get("entities")]
		message = "Your message intent: \"{}\" , extracted entities: {}".format(intent,entities)
		dispatcher.utter_message(message)  # send the message back to the user
		return []

class ActionExecuter(Action):
	def name(self):
		# define the name of the action which can then be included in training stories
		return "action_execute_plan"

	def run(self, dispatcher, tracker, domain):
		intent = tracker.latest_message["intent"].get("name")
		if(intent == "affirm"):
			dispatcher.utter_message('Executing the message')  # send the message back to the user
			#send command to robot
		else:
			dispatcher.utter_message('Ok, I will be waiting for your command')  # send the message back to the user
		return []

def run_action_server(port=DEFAULT_SERVER_PORT, cors='*'):
	print("Starting action endpoint server...")
	edp_app = endpoint_app(cors_origins=cors,
							action_package_name=current_module)

	http_server = WSGIServer(('0.0.0.0', port), edp_app)

	http_server.start()
	print("Action endpoint is up and running. on {}"
				"".format(http_server.address))

	http_server.serve_forever()

if __name__ == "__main__":
	run_action_server()

