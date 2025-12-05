import warnings
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*weights_only.*"
)
import sounddevice as sd
import numpy as np
import wave
import os
import json
import pyttsx3
import tempfile
import requests
import subprocess
import re
import platform
from gtts import gTTS
import io
import getpass
from pydub import AudioSegment
import argostranslate.package
import argostranslate.translate
import time
from vosk import Model, KaldiRecognizer
import noisereduce as nr
import soundfile as sf
from googletrans import Translator
from pypinyin import lazy_pinyin
from korean_romanizer.romanizer import Romanizer

# Get the absolute path to the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
status_file = os.path.join(BASE_DIR, "status.json")

def update_status(state):
    with open(status_file, "w") as f:
        json.dump({"status": state}, f)

update_status("LOADING")
# Load Vosk model for Filipino speech recognition
MODEL_PATH = os.path.join(BASE_DIR, "Vosk", "Filipino", "vosk-model-tl-ph-generic-0.6")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
update_status("LOADED")

# Translation Config
SOURCE_LANG = "tl"  # Filipino
TARGET_LANG = "ko"  # Korean
translator = Translator()

# Initialize pyttsx3
engine = pyttsx3.init()

def check_internet():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

def set_korean_voice():
    engine = pyttsx3.init()  # Reinitialize to ensure clean state
    voices = engine.getProperty('voices')
    
    # More comprehensive voice search
    korean_voices = [
        voice for voice in voices 
        if any(kw in voice.id.lower() or kw in voice.name.lower() 
               for kw in ["ko", "korean", "kr"])
    ]
    
    if korean_voices:
        engine.setProperty('voice', korean_voices[0].id)
    else:
        print("⚠️ Korean voice not found. Using default voice.")
    
    return engine  # Return the engine instance

def speak_text(text):
    if not text or not text.strip():
        return
    
    update_status("SPEAKING")
    
    try:
        engine = set_korean_voice()  # Get fresh engine instance
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        # Ensure proper event loop handling
        engine.say(text)
        engine.runAndWait()
        
        # More substantial delay after speaking
        time.sleep(1.5)
        
    except Exception as e:
        print(f"⚠️ TTS Error: {str(e)}")
        # Attempt recovery
        try:
            engine.endLoop()
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            print("❌ Failed to recover TTS engine")
    update_status("IDLE")

def record_audio(duration=5, samplerate=16000):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    return audio

def transcribe_audio(audio_data, samplerate=16000):
    temp_wav = os.path.join(BASE_DIR, "temp.wav")
    with wave.open(temp_wav, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    data, sr = sf.read(temp_wav)
    reduced = nr.reduce_noise(y=data, sr=sr)
    denoised_wav = os.path.join(BASE_DIR, "denoised.wav")
    sf.write(denoised_wav, reduced, sr)

    results = []
    with wave.open(denoised_wav, 'rb') as wf:
        while True:
            data = wf.readframes(4000)
            if not data:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                results.append(result.get("text", ""))
    final_result = json.loads(recognizer.FinalResult())
    results.append(final_result.get("text", ""))

    return " ".join(results).strip()

def argos_translate_chain(text):
    try:
        installed_languages = argostranslate.translate.get_installed_languages()

        tl = next((lang for lang in installed_languages if lang.code == "tl"), None)
        en = next((lang for lang in installed_languages if lang.code == "en"), None)
        ko = next((lang for lang in installed_languages if lang.code == "ko"), None)

        tl_en = tl.get_translation(en)
        text_en = tl_en.translate(text)

        en_ko = en.get_translation(ko)
        text_ko = en_ko.translate(text_en) 

        return text_ko.strip()
    except Exception as e:
        return f"Argos chain failed: {e}"

def translate_text(text):
    print(f"📝 Filipino Transcription: {text}")
    if check_internet():
        try:
            translated = translator.translate(text, src=SOURCE_LANG, dest=TARGET_LANG)
            return translated.text.strip()
        except Exception as e:
            pass

    return argos_translate_chain(text)

def romanize_translation(text):
    return Romanizer(text).romanize()

def get_translation_data():
    """Retrieve transcription, translation, and romanized text."""
    audio_data = record_audio(duration=5)
    transcription = transcribe_audio(audio_data)
    
    if transcription:
        translated_text = translate_text(transcription)
        romanized_text = romanize_translation(translated_text)
        return transcription, translated_text, romanized_text
    return None, None, None

def continuous_translation():
    output_path = os.path.join(BASE_DIR, "translation_data.json")
    
    while True:
        try:
            # Clear previous translation
            with open(output_path, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
            
            audio_data = record_audio(duration=5)
            transcription = transcribe_audio(audio_data)
            
            if transcription:
                translated_text = translate_text(transcription)
                romanized_text = romanize_translation(translated_text)
                
                # Save to JSON file
                with open(output_path, "w") as f:
                    json.dump({
                        "transcription": transcription,
                        "translated_text": translated_text,
                        "romanized_text": romanized_text
                    }, f)
                
                speak_text(translated_text)
        
        except KeyboardInterrupt:
            print("\nStopping listener...")
            break
        except Exception as e:
            print(f"Error in translation: {e}")
        
        time.sleep(0.5)  # Shorter sleep for more responsive UI

def update_status(state):
    with open(status_file, "w") as f:
        json.dump({"status": state}, f)

if __name__ == "__main__":
    time.sleep(1)
    continuous_translation()
