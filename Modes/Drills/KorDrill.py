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
import unicodedata
import requests
import subprocess
import re
import random
import platform
from difflib import SequenceMatcher
from gtts import gTTS
import io
import getpass
from pydub import AudioSegment
import argostranslate.package
import argostranslate.translate
import time
import noisereduce as nr
import pyttsx3
import soundfile as sf
from googletrans import Translator
from korean_romanizer.romanizer import Romanizer

# ===============================
# CONFIGURATION
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER =  getpass.getuser()
WHISPER_BIN = os.path.join("/", "home", USER, "whisper.cpp", "build", "bin", "whisper-cli")
MODEL_PATH = os.path.join("/", "home", USER, "whisper.cpp", "models", "ggml-base.bin")

SOURCE_LANG = "tl"  # Filipino
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "Drill", "drill_results.json")

translator = Translator()
engine = pyttsx3.init()

def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

def normalize_text(text):
    return unicodedata.normalize("NFKC", text.strip().lower())

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


def translate_text(text, target_lang):
    if check_internet():
        try:
            translated = translator.translate(text, dest=target_lang)
            return translated.text.strip()
        except Exception as e:
            print(f"⚠️ Google Translate error: {e} — using ArgosTranslate.")
    return argos_translate_chain(text)

def preprocess_text(text: str) -> str:
    if text and not text.endswith((".", "!", "?")):
        return text + "."
    return text

def romanize_korean(text):
    try:
        return Romanizer(text).romanize()
    except Exception:
        return ""

def speak_text(text, lang, use_gtts=False):
    if not check_internet():
        print("Offline mode playback skipped")
        return
    try:
        print(f"🔈 Speaking Filipino: {text}")
        tts = gTTS(text=text, lang=lang)
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

def whisper_stt(audio_data):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_wav:
        # Save raw int16 recording first
        sf.write(tmp_wav.name, audio_data, 16000)

        # Reload as float32 for noise reduction
        data, sr = sf.read(tmp_wav.name, dtype="float32")

        # Apply noise reduction
        reduced = nr.reduce_noise(y=data, sr=sr)

        # Overwrite with denoised version
        sf.write(tmp_wav.name, reduced, sr)

        result = subprocess.run(
            [WHISPER_BIN, "-m", MODEL_PATH, "-l", "ko", "--no-timestamps", "-f", tmp_wav.name],
            capture_output=True, text=True
        )

        raw_output = result.stdout.strip()
        cleaned = re.sub(r"\[\d+:\d+\.\d+ --> \d+:\d+\.\d+\]", "", raw_output)
        transcription = cleaned.strip()

    return transcription
    
def record_audio():
    print("Recording... Speak clearly.")
    audio = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype=np.int16)
    sd.wait()
    return audio

def is_close(a, b, threshold=0.83):
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio() >= threshold

def save_drill_results(data):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_drill():
    filename = os.path.join(BASE_DIR, "randword.txt")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = list(set(f.read().splitlines()))
            if len(lines) < 5:
                print("[!] Not enough words in the file.")
                return
            selected_words = random.sample(lines, 5)
    except FileNotFoundError:
        print("[!] randword.txt not found.")
        return

    score = 0
    all_results = []

    for i, chosen_text in enumerate(selected_words, start=1):
        save_drill_results({
            "status": "QUESTION",
            "current_word": chosen_text
        })
        speak_text(chosen_text, "tl", use_gtts=True)
        
        user_translation = whisper_stt(record_audio())
        user_romanized = romanize_korean(user_translation)

        save_drill_results({
            "status": "ANSWER",
            "current_word": chosen_text,
            "user_input": user_translation,
            "user_romanized": user_romanized
        })

        # Always translate Filipino → Korean
        korean_text = translate_text(chosen_text, "ko")
        romanized = romanize_korean(korean_text)
        is_correct = is_close(romanize_korean(user_translation), romanize_korean(korean_text), threshold=0.8)
        
        save_drill_results({
            "status": "RESULT",
            "current_word": chosen_text,
            "user_input": user_translation,
            "user_romanized": user_romanized,
            "translation": korean_text,
            "romanized": romanized,
            "is_correct": is_correct
        })
        
        if is_correct:
            print("✅ Correct!")
            score += 1
        else:
            print("❌ Incorrect.")
            
        drill_data = {
            "current_word": chosen_text,
            "user_input": user_translation,
            "translation": korean_text,
            "romanized": romanized,
            "is_correct": is_correct    
        }

        all_results.append(drill_data)

    final_data = {
        "status": "COMPLETE",
        "results": all_results,
        "final_score": score
    }
    save_drill_results(final_data)
    print(f"\nDrill complete! Your score: {score}/5")

if __name__ == "__main__":
    run_drill()
