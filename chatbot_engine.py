from rasa.run import run_core
from rasa.actions import run_action_server
from threading import Thread
    
class Rasa(Thread):
	def __init__(self):
		super().__init__()

	def run(self):
		action_server = Thread(target=run_action_server)
		action_server.setDaemon(True)
		action_server.start()
		#run core
		run_core()



if __name__ == '__main__':
	chatbot_engine = Rasa()
	chatbot_engine.run()