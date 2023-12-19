import os
import pygame
import speech_recognition as sr
from threading import Timer
from openai import OpenAI
import config as cfg

class ChatBot:
    def __init__(self, voice):
        self.client = OpenAI(api_key=cfg.OPENAI_API_KEY)
        self.r = sr.Recognizer()
        self.listening = False
        if voice: 
            self.voice = voice
        else:
            self.voice = cfg.VOICE
        self.t = Timer(30.0, self.set_listening_true)
        self.messages = [
            {"role": "system", "content": "I am " + cfg.BOT_NAME.capitalize() + "."},
            {"role": "system", "content": "I give short responses that will be spoken. All responses will be conversational."},
            {"role": "system", "content": cfg.CUSTOM_COMMAND}
        ]

    def set_listening_true(self):
        self.listening = False

    def listen_for_input(self):
        with sr.Microphone() as source:
            audio = self.r.listen(source)
            try:
                text = self.r.recognize_google(audio)
                return text
            except sr.RequestError:
                print("Sorry, there was an error with the speech recognition service.")
                return ""
            except:
                return ""

    def get_chatbot_response(self, messages):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            frequency_penalty=0.4,
            presence_penalty=0.5,
            stop=["Outline:"]
        )
        messages.append({"role": "system", "content": response.choices[0].message.content})
        safe_response = response.choices[0].message.content
        self.generate_audio(safe_response)
        return safe_response

    def play_audio(self, file_path):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        pygame.quit()

    def generate_audio(self, paragraph):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=self.voice,
            input=paragraph,
        )
        root = os.path.dirname(os.path.realpath(__file__))
        response.stream_to_file(root + "\\output.mp3")
        self.play_audio(root + "\\output.mp3")
        try:
            self.t.cancel()
        except:
            pass
        self.t = Timer(30.0, self.set_listening_true)
        self.t.start()

    def run(self):
        while True:
            user_input = self.listen_for_input()
            if user_input and ((cfg.BOT_NAME.lower() in user_input or cfg.BOT_NAME.capitalize() in user_input) or self.listening):
                print("You: " + user_input)
                self.listening = True
                self.messages.append({"role": "user", "content": user_input})
                response = self.get_chatbot_response(self.messages)
                print(cfg.BOT_NAME.capitalize() + ": " + response)

if __name__ == "__main__":
    bot = ChatBot()
    bot.run()