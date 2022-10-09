from speechtotext import SnipsASR
from chatbot_engine import Rasa
import os
directory = os.path.dirname(os.path.realpath(__file__))

from precise_runner import PreciseEngine, PreciseRunner

class Chatbot():
	def __init__(self, disable_hotword = False):
		self.disable_hotword = disable_hotword
		print('Starting chatbot... ')
		chatbot_engine = Rasa()
		chatbot_engine.setDaemon(True)
		#chatbot_engine.start()

		self.asr_client = SnipsASR()
		self.asr_client.setDaemon(True)
		#self.asr_client.start()
		engine = PreciseEngine(directory+'/resources/static/precise-engine', directory+'/resources/static/zordon.pb')
		self.runner = PreciseRunner(engine, on_activation=self.hotword_detected)
		

	def run(self):
		self.runner.start()		

	def hotword_detected(self):
		print("hotword detected")
		self.asr_client.activate()

if __name__ == "__main__":
	chatbot = Chatbot()
	chatbot.run()
	import time
	while(True):
		time.sleep(5) 
		chatbot.run()