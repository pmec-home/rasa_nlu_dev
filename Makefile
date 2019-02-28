help:
	@echo "    run"
	@echo "        Runs the chatbot on the command line."
	@echo "    run-actions"
	@echo "        Runs the action server."
	@echo "    run-core"
	@echo "        Runs the core server."
	@echo "    generate-chatette"
	@echo "        Generate the nlu train and test data from the chattete folder rasa/data_generation"
	@echo "    train-nlu"
	@echo "        Train the natural language understanding using Rasa NLU."
	@echo "    train-core"
	@echo "        Train a dialogue model using Rasa core."
	@echo "    train"
	@echo "        Generate the chatette dataset and train the models from the rasa nlu and the rasa core"
	@echo "    test"
	@echo "        Run tests"

run:
	python -m rasa.run

run-actions:
	python -m rasa_core_sdk.endpoint --actions rasa.actions

run-core:
	python -m rasa_core.run --nlu rasa/models/nlu --core rasa/models/core --endpoints rasa/endpoints.yml

generate-chatette:
	python -m rasa.generate
	python -m rasa.generate --test

train-nlu:
	python -m rasa.trainer --nlu

train-core:
	python -m rasa.trainer --core

train:
	make generate-chatette
	make train-nlu
	make train-core

test:
	python -m rasa.tests