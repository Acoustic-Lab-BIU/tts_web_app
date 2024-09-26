from flask import Flask, request, jsonify, render_template
from google.cloud import texttospeech
from google.oauth2 import service_account
import paramiko
from pathlib import Path
import wave
import json
import re

class HebrewTTS:
    def __init__(self):
        json_path=Path(__file__).parent/'static/Google_key.json'
        creds = service_account.Credentials.from_service_account_file(json_path)
        self.client = texttospeech.TextToSpeechClient(credentials=creds)
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="he-IL",
            name="he-IL-Wavenet-A",
        )

    def text_to_ssml(self, text):
        ssml = "<speak>{}</speak>".format(
            text.replace("\n", '\n<break time="1s"/>').replace('.', '\n<break time="1s"/>')
        )
        return ssml

    def play_wav(self, local_file):
        local_file = Path(local_file)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('ari-14c', username='pal')
        ftp = client.open_sftp()
        remote_file = '/home/pal/yoav/tmp_tts.wav'
        ftp.put(local_file, remote_file)
        _, _, _ = client.exec_command(f'aplay {remote_file}')
        client.close()

    def text_to_wav(self, txt):
        synthesis_input = texttospeech.SynthesisInput(ssml=self.text_to_ssml(txt))
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
        response = self.client.synthesize_speech(input=synthesis_input, voice=self.voice, audio_config=audio_config)
        tmp_wav_path = Path(__file__).parent/'tmp.wav'
        self.audio_file = wave.open(str(tmp_wav_path), 'w')
        self.audio_file.setnchannels(1)
        self.audio_file.setsampwidth(2)
        self.audio_file.setframerate(24000)
        self.audio_file.writeframes(response.audio_content)
        self.audio_file.close()
        self.play_wav(str(tmp_wav_path))

class EnglishTTS:
    def __init__(self):
        pass
    
    def text_to_wav(self, txt):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('ari-14c', username='pal')
        stdin, stdout, stderr = client.exec_command(f'source /home/pal/deployed_ws/setup.bash && python3 /home/pal/yoav/publish_txt.py "{txt}"')
        print(stderr.read().decode())
        client.close()

class TTS:
    def __init__(self, lang='Hebrew'):
        self.heb = HebrewTTS()
        self.en = EnglishTTS()
        self.lang = lang
        print('TTS is initialized')

    def contains_hebrew(self, text):
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
        return bool(hebrew_pattern.search(text))

    def play_txt(self, txt):
        lang = self.contains_hebrew(txt)
        if lang:
            self.heb.text_to_wav(txt)
        else:
            self.en.text_to_wav(txt)

app = Flask(__name__)
tts = TTS()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            tts.play_txt(text)
            return jsonify({'message': 'Text-to-speech processing started.'})
        else:
            return jsonify({'error': 'No text provided.'}), 400
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

# # app.py

# import wave
# import re
# import paramiko
# from google.cloud import texttospeech
# from google.oauth2 import service_account
# from flask import Flask, render_template, request, redirect, url_for, flash
# from pathlib import Path

# app = Flask(__name__)
# app.secret_key = "your_secret_key"

# class HebrewTTS:
#     def __init__(self):
#         json_path = 
#         creds = service_account.Credentials.from_service_account_file(json_path)
#         self.client = texttospeech.TextToSpeechClient(credentials=creds)
#         self.voice = texttospeech.VoiceSelectionParams(
#             language_code="he-IL",
#             name="he-IL-Wavenet-A",
#         )

#     def text_to_ssml(self, text):
#         ssml = "<speak>{}</speak>".format(
#             text.replace("\n", '\n<break time="1s"/>').replace('.', '\n<break time="1s"/>')
#         )
#         return ssml

#     def play_wav(self, local_file):
#         local_file = Path(local_file)
#         client = paramiko.SSHClient()
#         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         private_key_path = "/root/.ssh/id_rsa"  # Path to the SSH key in the container
#         private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

#         client.connect('ari-14c', username='pal', pkey=private_key)
#         ftp = client.open_sftp()
#         remote_file = f'/home/pal/yoav/tmp_tts.wav'
#         ftp.put(local_file, remote_file)

#         _, _, _ = client.exec_command(f'aplay {remote_file}')
#         client.close()

#     def text_to_wav(self, txt):
#         synthesis_input = texttospeech.SynthesisInput(ssml=self.text_to_ssml(txt))
#         audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
#         response = self.client.synthesize_speech(input=synthesis_input, voice=self.voice, audio_config=audio_config)
        
#         self.audio_file = wave.open('/home/ros/tmp.wav', 'w')
#         self.audio_file.setnchannels(1)
#         self.audio_file.setsampwidth(2)
#         self.audio_file.setframerate(24000)
#         self.audio_file.writeframes(response.audio_content)
#         self.audio_file.close()
#         self.play_wav('/home/ros/tmp.wav')


# class EnglishTTS:
#     def __init__(self):
#         pass

#     def text_to_wav(self, txt):
#         client = paramiko.SSHClient()
#         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         private_key_path = "/root/.ssh/id_rsa"  # Path to the SSH key in the container
#         private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

#         client.connect('ari-14c', username='pal', pkey=private_key)
#         stdin, stdout, stderr = client.exec_command(f'source /home/pal/deployed_ws/setup.bash && python3 /home/pal/yoav/publish_txt.py "{txt}"')
#         print(stderr.read().decode())
#         client.close()


# class TTS:
#     def __init__(self, lang='Hebrew'):
#         self.heb = HebrewTTS()
#         self.en = EnglishTTS()
#         self.lang = lang
#         print('TTS is initialized')

#     def contains_hebrew(self, text):
#         hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
#         return bool(hebrew_pattern.search(text))

#     def play_txt(self, txt):
#         if self.contains_hebrew(txt):
#             self.heb.text_to_wav(txt)
#         else:
#             self.en.text_to_wav(txt)


# tts = TTS()


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/speak', methods=['POST'])
# def speak():
#     text = request.form['text']
#     tts.play_txt(text)
#     return json.dumps({"status": "success"}), 200, {'ContentType': 'application/json'}


# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000)