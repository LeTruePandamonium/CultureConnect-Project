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
import noisereduce as nr
import soundfile as sf
from googletrans import Translator
from pypinyin import lazy_pinyin

# Get the absolute path to the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER = getpass.getuser()
WHISPER_BIN = os.path.join("/", "home", USER, "whisper.cpp", "build", "bin", "whisper-cli")
MODEL_PATH = os.path.join("/", "home", USER, "whisper.cpp", "models", "ggml-base.bin")
status_file = os.path.join(BASE_DIR, "status.json")


# OS Detection
IS_WINDOWS = platform.system() == "Windows"

# Translation Config
SOURCE_LANG = "ko"
TARGET_LANG = "tl"
translator = Translator()

def check_internet():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

def speak_text(text):
    update_status("SPEAKING")
    if not check_internet():
        print("Offline mode playback skipped")
        return
    try:
        print(f"🔈 Speaking Filipino: {text}")
        tts = gTTS(text=text, lang="tl")
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        audio = AudioSegment.from_file(audio_bytes, format="mp3")
        audio = audio.set_frame_rate(16000).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
        sd.play(samples, samplerate=16000)
        sd.wait()
    except Exception as e:
        print("")
    update_status("IDLE")

def record_audio(duration=5, samplerate=16000):
    print("🎙 Recording... Speak in Korean.")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    print("✅ Recording complete.")
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

    result = subprocess.run(
        [WHISPER_BIN, "-m", MODEL_PATH, "-l", "ko", "--no-timestamps", "-f", denoised_wav],
        capture_output=True,
        text=True
    )

    raw_output = result.stdout.strip()
    cleaned =re.sub(r"\[\d+:\d+\.\d+ --> \d+:\d+\.\d+\]", "", raw_output)

    transcription = cleaned.strip()
    return transcription

def argos_translate_chain(text):
    try:
        installed_languages = argostranslate.translate.get_installed_languages()

        ko = next((lang for lang in installed_languages if lang.code == "ko"), None)
        en = next((lang for lang in installed_languages if lang.code == "en"), None)
        tl = next((lang for lang in installed_languages if lang.code == "tl"), None)

        ko_en = ko.get_translation(en)
        text_en = ko_en.translate(text)

        en_tl = en.get_translation(tl)
        text_tl = en_tl.translate(text_en)

        return text_tl.strip()
    except Exception as e:
        return f"Argos chain failed: {e}"


def translate_text(text):
    if check_internet():
        try:
            translated = translator.translate(text, src=SOURCE_LANG, dest=TARGET_LANG)
            return translated.text.strip()
        except Exception as e:
            print(f"⚠️ Google Translate error: {e} — using ArgosTranslate.")

    return argos_translate_chain(text)

def preprocess_text(text: str) -> str:
    if text and not text.endswith((".", "!", "?")):
        return text + "."
    return text

def update_status(state):
    with open(status_file, "w") as f:
        json.dump({"status": state}, f)

def get_translation_data():
    """Retrieve transcription, translation, and romanized text."""
    audio_data = record_audio(duration=5)
    transcription = transcribe_audio(audio_data)
    
    if transcription:
        transcription = preprocess_text(transcription)
        print(f"📝 Korean Transcription: {transcription}")
        translated_text = translate_text(transcription)
        return transcription, translated_text
    return None, None

def continuous_translation():
    output_path = os.path.join(BASE_DIR, "translation_data.json")
    
    while True:
        transcription, translated_text = get_translation_data()
        if transcription and translated_text:
            print(f"Filipino Translation: {translated_text}")
            
            # Save to JSON file
            with open(output_path, "w") as f:
                json.dump({
                    "transcription": transcription,
                    "translated_text": translated_text
                }, f)
            
            speak_text(translated_text)
        
        time.sleep(2)

if __name__ == "__main__":
    continuous_translation()