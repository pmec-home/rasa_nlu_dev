#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.
NOTE: To use the Google Cloud Client Library for Python is necessary the instalation and configuration of the Google Cloud SDK:
    https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries?hl=pt-br#client-libraries-install-python
NOTE: This module requires the additional dependency `pyaudio` and `Google Cloud Client Library for Python`. To install
using pip:
    pip install pyaudio
    pip install --upgrade google-cloud-speech
Example usage:
    python speechtotext.py
"""

#Modify from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/speech/cloud-client/transcribe_streaming_mic.py

# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
           
"""
credentials (google.auth.credentials.Credentials) [https://google-auth.readthedocs.io/en/stable/reference/google.auth.credentials.html] 
The authorization credentials to attach to requests. These credentials identify this application to the service. If none are specified, the client will attempt to ascertain the credentials from the environment. This argument is mutually exclusive with providing a transport instance to transport; doing so will raise an exception

language_code
Required The language of the supplied audio as a BCP-47 language tag. Example: “en-US”.

RATE
Sample rate in Hertz of the audio data sent in all RecognitionAudio messages. Valid values are: 8000-48000. 16000 is optimal. For best results, set the sampling rate of the audio source to 16000 Hz. If that’s not possible, use the native sample rate of the audio source (instead of re- sampling). This field is optional for FLAC and WAV audio files and required for all other audio formats. For details, see [AudioEncoding][google.cloud.speech.v1.Recognitio nConfig.AudioEncoding].
"""
class GoogleSpeechToText():
    def __init__(self, credentials=None, RATE=16000, CHUNK=1024, language_code='en-US'):
        self.RATE = RATE
        self.CHUNK = CHUNK
        self.language_code = language_code

        self.client = speech.SpeechClient(credentials=credentials)

        #TODO: speech_contexts -> https://cloud.google.com/speech-to-text/docs/basics#phrase-hints
        self.config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
            model='command_and_search',
            enable_automatic_punctuation=True)

        self.streaming_config = types.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True,
            single_utterance=True)

    def recognize_from_mic(self):
        with MicrophoneStream(self.RATE, self.CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)

            responses = self.client.streaming_recognize(self.streaming_config, requests)
            print("Listening...")
            num_chars_printed = 0
            for response in responses:
                #print(response)
                if not response.results:
                    continue

                # The `results` list is consecutive. For streaming, we only care about
                # the first result being considered, since once it's `is_final`, it
                # moves on to considering the next utterance.
                result = response.results[0]
                if not result.alternatives:
                    continue

                # Display the transcription of the top alternative.
                transcript = result.alternatives[0].transcript

                # Display interim results, but with a carriage return at the end of the
                # line, so subsequent lines will overwrite them.
                #
                # If the previous result was longer than this one, we need to print
                # some extra spaces to overwrite the previous result
                overwrite_chars = ' ' * (num_chars_printed - len(transcript))
                #print(result)
                if not result.is_final:
                    sys.stdout.write(transcript + overwrite_chars + '\r')
                    sys.stdout.flush()

                    num_chars_printed = len(transcript)

                else:
                    print(transcript + overwrite_chars)
                    return transcript + overwrite_chars

import paho.mqtt.client as mqtt
import json
import requests
from threading import Thread
import paho.mqtt.publish as publish

class SnipsASR(Thread):
	def __init__(self, MQTT_IP_ADDR = "localhost", MQTT_PORT=1883):
		super().__init__()
		self.client = mqtt.Client()
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.MQTT_IP_ADDR = MQTT_IP_ADDR
		self.MQTT_PORT = MQTT_PORT
	
	def run(self):
		self.client.connect(self.MQTT_IP_ADDR, self.MQTT_PORT, 60)

		# Blocking call that processes network traffic, dispatches callbacks and
		# handles reconnecting.
		# Other loop*() functions are available that give a threaded interface and a
		# manual interface
		self.client.loop_forever()
		
	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		self.client.subscribe("hermes/asr/textCaptured")
		

	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		payload = json.loads(msg.payload.decode('utf8'))
		requests.post('http://localhos:5004/webhooks/rest/webhook', json={"sender": "zordon", "message": payload['text']})

	def activate(self):
		publish.single("hermes/asr/startListening", '{"siteId": "default"}', hostname="localhost", port=1883)


if __name__ == "__main__":
    #client = GoogleSpeechToText()
    #while True:
    #    client.recognize_from_mic()
	client = SnipsASR()
	client.setDaemon(True)
	client.start()
	#client.run()
	#import threading
	#t1 = threading.Thread(target=client.run)
	#t1.setDaemon(True)
	#t1.start()

	import paho.mqtt.publish as publish
	import time
	while True:
		publish.single("hermes/asr/startListening", '{"siteId": "default"}', hostname="localhost", port=1883)
		time.sleep(10)
