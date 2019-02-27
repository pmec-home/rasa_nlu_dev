import data_generation.generate as generate
import rasa.tests as tests

generate.main(test=False)
generate.main(test=True)
tests.main(train_arg=True)