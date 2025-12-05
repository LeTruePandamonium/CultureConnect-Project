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
import pyttsx3
import soundfile as sf
from vosk import Model, KaldiRecognizer
from googletrans import Translator
from pypinyin import lazy_pinyin

# Get the absolute path to the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
status_file = os.path.join(BASE_DIR, "status.json")


def update_status(state):
    with open(status_file, "w") as f:
        json.dump({"status": state}, f)

# pyttsx3 Initialization
engine = pyttsx3.init()

update_status("LOADING")
# Vosk Filipino Model
MODEL_PATH = os.path.join(BASE_DIR, "Vosk", "Filipino", "vosk-model-tl-ph-generic-0.6")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
update_status("LOADED")

# Translation Config
SOURCE_LANG = "tl"
TARGET_LANG = "zh-CN"
translator = Translator()

def check_internet():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

def set_chinese_voice():
    found = False
    for voice in engine.getProperty('voices'):
        if "zh" in voice.id.lower() or "chinese" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            found = True
            break
    if not found:
        print("⚠️ Chinese voice not found. Using default voice.")

def speak_text(text, lang="zh"):
    update_status("SPEAKING")
    print(f"🔈 Speaking Chinese ({lang}): {text}")
    try:
        if lang == "en":
            subprocess.run(["espeak-ng", "-v", "en", "-s", "130", text])
        elif lang == "zh":
            subprocess.run(["espeak-ng", "-v", "cmn", "-s", "130", text])
        else:
            subprocess.run(["espeak-ng", "-v", lang, "-s", "130", text])
    except FileNotFoundError:
        print("❌ espeak-ng not found. Please install espeak-ng to enable Chinese TTS.")
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
        zh = next((lang for lang in installed_languages if lang.code == "zh"), None)

        tl_en = tl.get_translation(en)
        text_en = tl_en.translate(text)

        en_zh = en.get_translation(zh)
        text_zh = en_zh.translate(text_en) 

        return text_zh.strip()
    except Exception as e:
        return f"Argos chain failed: {e}"


def translate_text(text):
    if check_internet():
        try:
            translated = translator.translate(text, src=SOURCE_LANG, dest=TARGET_LANG)
            return translated.text.strip()
        except Exception as e:
            pass
    
    return argos_translate_chain(text)

def romanize_translation(text):
    return " ".join(lazy_pinyin(text))

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

if __name__ == "__main__":
    time.sleep(1)
    continuous_translation()