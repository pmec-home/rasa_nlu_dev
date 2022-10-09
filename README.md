## Pequi Mecânico @Home ~ Chatbot

**Project**

The RoboCup@Home league is a competition aims to develop service and assistive robot technology with high relevance for future personal domestic applications.

This project is developed for the team Pequi Mecânico from the Ferderal University of Goiás (Brazil), this is submodule of the project responsible for the voice recognition and natural language processing of the robot.

**Requirements**

* **Python 3.6** (Rasa NLU Tensorflow dependence do not support 3.7 [01/03/19])
* **[Rasa Core](https://rasa.com/docs/core/)**
* **[Rasa NLU](https://rasa.com/docs/nlu/)**
* **[Chatette](https://github.com/SimGus/Chatette)**

To facilitate the requirements instalation just run:
```shell
sudo apt-get install libasound-dev
sudo apt-get install python-pyaudio python3-pyaudio
conda install tensorflow=1.12 pyaudio
pip install -r requirements.txt
```

**Usage**

First we need to generate the traning data that we will feed to the Rasa NLU model, to that this project uses an data generation tool called **[Chatette](https://github.com/SimGus/Chatette)**, the .chatette files are localized in *rasa/data_generation*.  
To generate the traning data to the default folder (*/rasa/data*) just run:  
```shell
make generate-chatette
```


To the train the Rasa NLU model run the command below, the model will be saved on */rasa/models/nlu*  
```shell
make train-nlu
```


To the train the Rasa Core model run the command below, the model will be saved on */rasa/models/core*
```shell
make train-core
```


Finally to run the Rasa Stack(the chatbot and the action server):
 ```shell
make run
```
