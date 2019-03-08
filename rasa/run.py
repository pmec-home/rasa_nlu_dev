from rasa.actions import run_action_server
from rasa_core_sdk.endpoint import *
import os
import rasa_core.run

logger = logging.getLogger(__name__)
directory = os.path.dirname(os.path.realpath(__file__))
 

def run_core():
    print("Starting rasa core...")
    cmd = "python -m rasa_core.run --nlu {} --core {} --endpoints {}".format(directory+"/models/nlu", directory+"/models/core", directory+"/endpoints.yml")
    os.system(cmd)

if __name__ == "__main__":
    #run action server as thread
    import threading
    t1 = threading.Thread(target=run_action_server)
    t1.setDaemon(True)
    t1.start()
    #run core
    run_core()