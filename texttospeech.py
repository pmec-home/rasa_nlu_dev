#!/usr/bin/env python

"""Google Cloud Text-To-Speech API sample application .
NOTE: To use the Google Cloud Client Library for Python is necessary the instalation and configuration of the Google Cloud SDK:
    https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries
NOTE: This module requires the additional dependency `pyaudio`, `wave` and `Google Cloud Client Library for Python`. To install
using pip:
    pip install pyaudio
    pip install wave
    pip install --upgrade google-cloud-texttospeech
Example usage:
    python texttospeech.py --text "hello"
    python texttospeech.py --ssml "<speak>Hello there.</speak>"
"""

#Modify from https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/texttospeech/cloud-client

from google.cloud import texttospeech
import pyaudio
import wave
import os

"""
credentials (google.auth.credentials.Credentials) [https://google-auth.readthedocs.io/en/stable/reference/google.auth.credentials.html] 
The authorization credentials to attach to requests. These credentials identify this application to the service. If none are specified, the client will attempt to ascertain the credentials from the environment. This argument is mutually exclusive with providing a transport instance to transport; doing so will raise an exception

language_code
The language (and optionally also the region) of the voice expressed as a BCP-47 language tag, e.g. “en-US”. Required. This should not include a script tag (e.g. use “cmn- cn” rather than “cmn-Hant-cn”), because the script will be inferred from the input provided in the SynthesisInput. The TTS service will use this parameter to help choose an appropriate voice. Note that the TTS service may choose a voice with a slightly different language code than the one selected; it may substitute a different region (e.g. using en- US rather than en-CA if there isn’t a Canadian voice available), or even a different language, e.g. using “nb” (Norwegian Bokmal) instead of “no” (Norwegian)”.

name
The name of the voice. Optional; if not set, the service will choose a voice based on the other parameters such as language_code and gender.
You can get the list of avalible voices names by running GoogleTextToSpeech().list_voices()

ssml_gender
The preferred gender of the voice. Optional; if not set, the service will choose a voice based on the other parameters such as language_code and name. Note that this is only a preference, not requirement; if a voice of the appropriate gender is not available, the synthesizer should substitute a voice with a different gender rather than failing the request.
speaking_rate
Possible Values:
*'NEUTRAL'
*'MALE'
*'FEMALE'
*'SSML_VOICE_GENDER_UNSPECIFIED'

Optional speaking rate/speed, in the range [0.25, 4.0]. 1.0 is the normal native speed supported by the specific voice. 2.0 is twice as fast, and 0.5 is half as fast. If unset(0.0), defaults to the native 1.0 speed. Any other values < 0.25 or > 4.0 will return an error.

pitch
Optional speaking pitch, in the range [-20.0, 20.0]. 20 means increase 20 semitones from the original pitch. -20 means decrease 20 semitones from the original pitch.

volume_gain_db
Optional volume gain (in dB) of the normal native volume supported by the specific voice, in the range [-96.0, 16.0]. If unset, or set to a value of 0.0 (dB), will play at normal native signal amplitude. A value of -6.0 (dB) will play at approximately half the amplitude of the normal native signal amplitude. A value of +6.0 (dB) will play at approximately twice the amplitude of the normal native signal amplitude. Strongly recommend not to exceed +10 (dB) as there’s usually no effective increase in loudness for any value greater than that.

sample_rate_hertz
The synthesis sample rate (in hertz) for this audio. Optional. If this is different from the voice’s natural sample rate, then the synthesizer will honor this request by converting to the desired sample rate (which might result in worse audio quality), unless the specified sample rate is not supported for the encoding chosen, in which case it will fail the request and return [google.rpc.Code.INVALID_ARGUMENT][].
"""
class GoogleTextToSpeech():
    def __init__(self, credentials=None, language_code='en-US', voice_name=None, gender='NEUTRAL', speaking_rate=1.0, pitch=0, volume_gain_db=0, sample_rate_hertz=24000):
        
        self.sample_rate_hertz = sample_rate_hertz
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        
        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        self.voice = texttospeech.types.VoiceSelectionParams(
            name=voice_name,
            language_code=language_code,
            ssml_gender=gender)
        
        # Note: you can pass in multiple effects_profile_id. They will be applied
        # in the same order they are provided.
        self.audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
            speaking_rate=speaking_rate,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
            sample_rate_hertz=sample_rate_hertz)
        
        #To reproduce audio
        self.p = pyaudio.PyAudio()
            
    def synthesize_text(self, text):
        """Synthesizes speech from the input string of text."""

        input_text = texttospeech.types.SynthesisInput(text=text)
        
        self.play(input_text)
       
            
    def synthesize_ssml(self, ssml):
        """Synthesizes speech from the input string of ssml.
        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        Example: <speak>Hello there.</speak>
        """
        input_text = texttospeech.types.SynthesisInput(ssml=ssml)
        
        self.play(input_text)

    def play(self, input_text):
        response = self.client.synthesize_speech(input_text, self.voice, self.audio_config)
        
        filename = 'output.wav'
        with open(filename, 'wb') as out:
            out.write(response.audio_content)
            print('Audio content written to file "output.wav"')
            
        wf = wave.open(filename, 'rb')
        
        # The response's audio_content is binary.
        stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
        CHUNK = 1024
        data = wf.readframes(CHUNK)

        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        
        os.remove(filename)
            
    def list_voices(self):
        # Performs the list voices request
        voices = self.client.list_voices()

        for voice in voices.voices:
            # Display the voice's name. Example: tpc-vocoded
            print('Name: {}'.format(voice.name))

            # Display the supported language codes for this voice. Example: "en-US"
            for language_code in voice.language_codes:
                print('Supported language: {}'.format(language_code))

            ssml_gender = texttospeech.enums.SsmlVoiceGender(voice.ssml_gender)

            # Display the SSML Voice Gender
            print('SSML Voice Gender: {}'.format(ssml_gender.name))

            # Display the natural sample rate hertz for this voice. Example: 24000
            print('Natural Sample Rate Hertz: {}\n'.format(
                voice.natural_sample_rate_hertz))
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text',
                       help='The text from which to synthesize speech.')
    group.add_argument('--ssml',
                       help='The ssml string from which to synthesize speech.')

    args = parser.parse_args()
    
    client = GoogleTextToSpeech()
    client.list_voices()
    
    if args.text:
        client.synthesize_text(args.text)
    else:
        client.synthesize_ssml(args.ssml)