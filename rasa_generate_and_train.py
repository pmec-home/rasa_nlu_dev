#shortcut script...
import rasa.generate as generate
import rasa.tests as tests
import rasa.trainer as train

def main():
	#Generate train and test dataset from the chatette folder (rasa/data_generation)
	generate.main(test=False)
	generate.main(test=True)
	#Train the Rasa NLU
	train.main(nlu=True)
	#Train the Rasa Core
	train.main(core=True)
	#Run tests
	tests.main(train_arg=False)

if __name__ == '__main__':
	main()
