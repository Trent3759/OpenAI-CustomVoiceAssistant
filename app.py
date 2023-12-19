import os
import pygame
import speech_recognition as sr
from threading import Timer
from openai import OpenAI
import config as cfg

# Initialize OpenAI client
client = OpenAI(api_key=cfg.OPENAI_API_KEY)

# Speech recognition setup
r = sr.Recognizer()

# Main program loop
listening = False

# Function to set listening to True
def set_listening_true():
    global listening
    listening = False

# Timer setup
t = Timer(30.0, set_listening_true)

# Function to convert speech to text
def listen_for_input():
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return text
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return ""
        except:
            return ""

# Function to send user input to ChatGPT and get a response
def get_chatbot_response(messages):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500,
        frequency_penalty=0.4,
        presence_penalty=0.5,
        stop=["Outline:"]
    )
    messages.append({"role": "system", "content": response.choices[0].message.content})
    safe_response = response.choices[0].message.content
    generate_audio(safe_response, cfg.VOICE)
    return safe_response

# Function to play audio
def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    pygame.quit()

# Function to generate audio from text
def generate_audio(paragraph, voice="alloy"):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=paragraph,
    )
    root = os.path.dirname(os.path.realpath(__file__))
    response.stream_to_file(root + "\\output.mp3")
    play_audio(root + "\\output.mp3")
    global t
    try:
        t.cancel()
    except:
        pass
    #reset timer
    t = Timer(30.0, set_listening_true)
    t.start()

messages = [
    {"role": "system", "content": "I am " + cfg.BOT_NAME.capitalize() + "."},
    {"role": "system", "content": "I give short responses that will be spoken. All responses will be conversational."},
    {"role": "system", "content": cfg.CUSTOM_COMMAND}
]

while True:
    user_input = listen_for_input()
    if user_input and ((cfg.BOT_NAME.lower() in user_input or cfg.BOT_NAME.capitalize() in user_input) or listening):
        print("You: " + user_input)
        listening = True
        messages.append({"role": "user", "content": user_input})
        response = get_chatbot_response(messages)
        print(cfg.BOT_NAME.capitalize() + ": " + response)
