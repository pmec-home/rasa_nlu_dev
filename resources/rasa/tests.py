import unittest
import pandas
from rasa_nlu.model import Interpreter
import os
import json

directory = os.path.dirname(os.path.realpath(__file__))

def hasSlot(slot, nlu_result):
	present = False
	for entity in nlu_result['entities']:
		if(entity['value'] == slot or entity['entity'] == slot):
			present = True
	return present

class NLUTestCase(unittest.TestCase):
	def setUp(self):
		self.interpreter = Interpreter.load(directory+"/models/current/nlu/")
		self.tests = pandas.read_csv(directory+"/tests/test_data.csv")
		self.tests.fillna("")

	def test_nlu(self):
		print(self.tests)
		for index,test in self.tests.iterrows():
			result = self.interpreter.parse(test['text'])
			message = "\nText: {}\n    Intent found: {} / Intent target: {}".format(test['text'], result['intent']['name'], test['intent'])
			self.assertEqual(result['intent']['name'], test['intent'], message)
			if(test['slots']):
				slots = test['slots'].split(',')
				for slot in slots:
					message = "\nText: {}\n    Slot target: {}\n    Slots found:\n         {}".format(test['text'], slot, json.dumps(result['entities'], indent=2))
					self.assertTrue(hasSlot(slot, result), message)
					
			

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(NLUTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)