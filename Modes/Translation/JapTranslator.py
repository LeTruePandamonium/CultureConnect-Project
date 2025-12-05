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
import configparser
import threading
from pypinyin import lazy_pinyin  # For Chinese Romanization
from korean_romanizer.romanizer import Romanizer  # For Korean Romanization
from googletrans import Translator
import pykakasi  # For Japanese Romanization

stop_thread = False

# Get the absolute path to the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
status_file = os.path.join(BASE_DIR, "status.json")

def update_status(state):
    with open(status_file, "w") as f:
        json.dump({"status": state}, f)

kks = pykakasi.kakasi()
kks.setMode("H", "a")
kks.setMode("K", "a")
kks.setMode("J", "a")
kks.setMode("r", "Hepburn")
kks.setMode("s", True)

# Load Vosk model for Filipino speech recognition
update_status("LOADING")
MODEL_PATH = os.path.join(BASE_DIR, "Vosk", "Filipino", "vosk-model-tl-ph-generic-0.6")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
update_status("LOADED")

# LibreTranslate API configuration
LIBRETRANSLATE_URL = "http://localhost:5000/translate"
SOURCE_LANG = "tl"  # Filipino
translator = Translator()

# Language mappings
LANGUAGES = {
    "ja": {"name": "Japanese", "code": "ja", "romanizer": None},
}

# Initialize pyttsx3
engine = pyttsx3.init()

def check_internet():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

def set_voice(language_code):
    found = False
    for voice in engine.getProperty('voices'):
        if language_code in voice.id.lower():
            engine.setProperty('voice', voice.id)
            found = True
            break
    if not found:
        print(f"Warning: No {language_code} voice found. Using default voice.")

def load_openjtalk_config():
    voice_path = "/home/cultureconnect/open_jtalk/new_voices/takumi_normal.htsvoice"
    dic_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
    return voice_path, dic_path

def speak_text(text, lang_code):
    update_status("SPEAKING")
    if lang_code == "ja":
        voice, dic = load_openjtalk_config()
        run_open_jtalk(text, voice, dic, speed=1, volume=1, pitch=145, gain=10)
    elif lang_code == "zh" or lang_code == "ko":
        speak_espeak_ng(text, lang_code)
    else:
        set_voice(lang_code)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.setProperty('pitch', 100)
        engine.say(text)
        engine.runAndWait()
    update_status("IDLE")

def speak_espeak_ng(text, lang_code):
    if lang_code == "zh":
        voice = "zh"
    elif lang_code == "ko":
        voice = "ko"
    else:
        voice = "en"

    text = text.encode("utf-8").decode("utf-8")
    output_file = "output.wav"

    subprocess.run([
        "espeak-ng",
        "-v", voice,
        "-s", "190",
        "-p", "55",
        "-a", "200",
        "-g", "3",
        "-w", output_file,
        text
    ], check=True)

    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        subprocess.run(["aplay", output_file])
    else:
        print(f"[!] Error: Output file {output_file} is empty or invalid.")

def run_open_jtalk(text, voice_path, dic_path, output_wav="output.wav", speed=1, volume=1, pitch=145, gain=10):
    try:
        cmd = [
            "open_jtalk",
            "-m", voice_path,
            "-x", dic_path,
            "-r", str(speed),
            "-p", str(pitch),
            "-g", str(gain),
            "-ow", output_wav
        ]
        subprocess.run(cmd, input=text, text=True, check=True)

        output_wav_louder = "output_louder.wav"
        subprocess.run(["sox", output_wav, output_wav_louder, "vol", str(volume)])

        subprocess.run(["aplay", output_wav_louder])

    except subprocess.CalledProcessError as e:
        print(f"[!] Error running Open JTalk: {e}")

def announcement(text):
    try:
        subprocess.run(["espeak-ng", "-v", "en", "-s", "130", text])
    except FileNotFoundError:
        print("espeak-ng not found. Please install")

def record_audio(duration=5, samplerate=16000):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    return audio

def transcribe_audio(audio_data, samplerate=16000):
    wav_filename = "temp.wav"
    with wave.open(wav_filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    data, sr = sf.read(wav_filename)
    reduced = nr.reduce_noise(y=data, sr=sr)
    denoised_wav = os.path.join(BASE_DIR, "denoised.wav")
    sf.write(denoised_wav, reduced, sr)

    rec_data = []
    with wave.open(denoised_wav, 'rb') as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                rec_data.append(result.get("text", "").strip())

    final_result = json.loads(recognizer.FinalResult())
    rec_data.append(final_result.get("text", "").strip())

    return " ".join(rec_data).strip() if rec_data else None

def argos_translate_chain(text):
    try:
        installed_languages = argostranslate.translate.get_installed_languages()

        tl = next((lang for lang in installed_languages if lang.code == "tl"), None)
        en = next((lang for lang in installed_languages if lang.code == "en"), None)
        ja = next((lang for lang in installed_languages if lang.code == "ja"), None)

        tl_en = tl.get_translation(en)
        text_en = tl_en.translate(text)

        en_ja = en.get_translation(ja)
        text_ja = en_ja.translate(text_en) 

        return text_ja.strip()
    except Exception as e:
        return f"Argos chain failed: {e}"

def translate_text(text, target_lang_code):
    if check_internet():
        try:
            corrected_lang_code = "zh-CN" if target_lang_code == "zh" else target_lang_code
            translated_text = translator.translate(text, src=SOURCE_LANG, dest=corrected_lang_code).text
            return translated_text.strip()
        except Exception as e:
            pass  # Fail silently and use ArgosTranslate
    return argos_translate_chain(text)

def romanize_translation(text, lang_code):
    if lang_code == "zh":
        return " ".join(lazy_pinyin(text))
    elif lang_code == "ko":
        return Romanizer(text).romanize()
    elif lang_code == "ja":
        result = kks.convert(text)
        return " ".join([item['hepburn'] for item in result])
    return ""

def get_translation_data():
    audio_data = record_audio(duration=5)
    transcription = transcribe_audio(audio_data)
    
    if transcription:
        translated_text = translate_text(transcription, "ja")
        romanized_text = romanize_translation(translated_text, "ja")
        return transcription, translated_text, romanized_text
    return None, None, None

def continuous_translation():
    global stop_thread
    output_path = os.path.join(BASE_DIR, "translation_data.json")
    
    while not stop_thread:
        try:
            with open(output_path, "w") as f:
                json.dump({
                    "transcription": "",
                    "translated_text": "",
                    "romanized_text": ""
                }, f)
            
            audio_data = record_audio(duration=5)
            transcription = transcribe_audio(audio_data)
            
            if transcription:
                translated_text = translate_text(transcription, "ja")
                romanized_text = romanize_translation(translated_text, "ja")
                
                with open(output_path, "w") as f:
                    json.dump({
                        "transcription": transcription,
                        "translated_text": translated_text,
                        "romanized_text": romanized_text
                    }, f)
                
                speak_text(translated_text, "ja")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error in translation: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    time.sleep(1)

    translation_thread = threading.Thread(target=continuous_translation)
    translation_thread.daemon = True
    translation_thread.start()
    translation_thread.join()
