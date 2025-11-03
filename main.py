import speech_recognition as sr
import os
import webbrowser
from config import apikey
import datetime
import random
import numpy as np
from google import genai
from google.genai import types
from google.genai.errors import APIError
import pyttsx3


os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"



def say(text):
    """Speaks the text using the pyttsx3 engine (Non-blocking by re-initialization)."""
    try:
        # Initialize and configure the engine locally for each call
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 175)

        engine.say(text)
        engine.runAndWait()
        engine.stop()  # Crucial cleanup

    except Exception as e:
        # Fallback if TTS engine fails (e.g., missing drivers, Windows issue)
        print(f"Jarvis (TTS Failed): {text} [Error: {e}]")



try:
    client = genai.Client(api_key=apikey)
    GEMINI_MODEL = "gemini-2.5-flash"
except Exception as e:
    print(f"ERROR: Could not initialize Gemini client. Details: {e}")
    client = None
# ---------------------------

chatStr = ""



def chat(query):
    """Handles multi-turn conversation using the Gemini API."""
    global chatStr
    print(chatStr)

    if client is None:
        say("Jarvis client is not operational.")
        return "ERROR: Gemini client not initialized."

    chatStr += f"professor: {query}\n Jarvis: "

    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=1024,
        top_p=1
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=chatStr,
            config=config
        )

        # Robust Content Check (Handles MAX_TOKENS/SAFETY blocks)
        if response.candidates and response.candidates[0].content:
            response_text = response.text
        else:
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            error_message = f"Response blocked by model policies or max token limit: {finish_reason}"
            say(f"Sorry, {error_message}")
            chatStr += f"[Error: {error_message}]\n"
            return error_message

    except APIError as e:
        response_text = f"API Error: {e}"
        say("I had a problem connecting to the AI system.")
    except Exception as e:
        response_text = f"System Error: {e}"
        say("A core error occurred in the AI processing.")

    say(response_text)
    chatStr += f"{response_text}\n"
    return response_text


def ai(prompt):
    """Handles single-turn requests for writing content and saving to a file."""
    if client is None:
        print("Jarvis client is not operational. Cannot run AI function.")
        return

    text = f"Gemini response for Prompt: {prompt} \n *************************\n\n"

    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=1024,
        top_p=1
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config
        )

        response_text = response.text

    except Exception as e:
        response_text = f"Error during AI generation: {e}"

    text += response_text

    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    file_name_part = ''.join(prompt.split('intelligence')[1:]).strip()
    if not file_name_part:
        file_name_part = f"prompt-{random.randint(1, 2343434356)}"

    safe_file_name = file_name_part.replace(' ', '_')[:50]

    with open(f"Openai/{safe_file_name}.txt", "w") as f:
        f.write(text)


# ==========================================================
# 3. COMMAND LOGIC (ADJUSTED FOR WINDOWS/CROSS-PLATFORM)
# ==========================================================

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            say("Sorry, I didn't understand that. Please try again.")
            return "none"
        except Exception:
            say("A recognition error occurred.")
            return "none"


if __name__ == '__main__':
    print('Welcome to Jarvis A.I')
    say("Jarvis A.I")
    while True:
        print("Listening...")
        query = takeCommand()

        sites = [
    ["Google", "https://www.google.com"],
    ["YouTube", "https://www.youtube.com)"],
    ["Facebook", "https://www.facebook.com"],
    ["Instagram", "https://www.instagram.com"],
    ["ChatGPT", "https://chatgpt.com"],
    ["Wikipedia", "https://www.wikipedia.org"],
    ["Reddit", "https://www.reddit.com"],
    ["X (formerly Twitter)", "https://x.com"],
    ["Amazon", "https://www.amazon.com"],
    ["TikTok", "https://www.tiktok.com"],
    ["Netflix", "https://www.netflix.com"],
    ["LinkedIn", "https://www.linkedin.com"],
    ["Bing", "https://www.bing.com"],
    ["Pinterest", "https://www.pinterest.com"],
    ["xHamster","https://xhamster.com/"]
]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
                break
        else:

            if "open music" in query.lower():
                # Uses 'start' command for Windows
                musicPath = "C:\\path\\to\\your\\music\\file.mp3"  # <--- MUST BE UPDATED
                os.system(f"start {musicPath}")

            elif "the time" in query.lower():
                hour = datetime.datetime.now().strftime("%H")
                min = datetime.datetime.now().strftime("%M")
                say(f"Sir time is {hour} bajke {min} minutes")

            # App-specific commands are often OS-dependent and removed/generalized
            # If you are on Windows, replace these with specific Windows commands
            elif "open facetime".lower() in query.lower():
                say("I am sorry, that command is for a Mac operating system.")

            elif "open pass".lower() in query.lower():
                say("I am sorry, I cannot open that application on this system.")

            elif "using artificial intelligence".lower() in query.lower():
                say("Starting dedicated AI content generation.")
                ai(prompt=query)

            elif "jarvis quit".lower() in query.lower():
                say("Goodbye, sir. Shutting down systems.")
                # Ensure pyttsx3 engine is stopped globally if possible before exit
                try:
                    if 'engine' in globals(): engine.stop()
                except:
                    pass
                exit()

            elif "reset chat".lower() in query.lower():
                chatStr = ""
                say("Chat history has been reset.")
            elif query.lower() != "none":
                print("Chatting...")
                chat(query)