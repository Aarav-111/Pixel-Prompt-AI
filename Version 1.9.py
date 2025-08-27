import io, base64
from PIL import Image
import mss, google.generativeai as genai
import sounddevice as sd
import soundfile as sf
import pyttsx3

API_KEY = "AIzaSyDiSBvSX7YDkaivNvFFcpiJOdVt4GHWc8M"
MODEL = "gemini-2.0-flash"

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
Take the screenshot as context ONLY when needed.

"""

model = genai.GenerativeModel(MODEL, system_instruction=SYSTEM_PROMPT)

engine = pyttsx3.init()

def capture_screen(max_width=1280):
    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", raw.size, raw.rgb)
        w, h = img.size
        if w > max_width:
            img = img.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
        buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

def img_part(b):
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b).decode()}}

def record_wav(seconds=5, sr=16000):
    print("Recording...")
    x = sd.rec(int(seconds*sr), samplerate=sr, channels=1, dtype='float32')
    sd.wait()
    buf = io.BytesIO(); sf.write(buf, x, sr, format='WAV')
    return buf.getvalue()

def wav_part(b):
    return {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(b).decode()}}

while True:
    wav = record_wav()
    shot = capture_screen()
    print("Sending to Gemini...")
    parts = [img_part(shot), wav_part(wav)]
    resp = model.generate_content(parts)
    text = resp.text
    print(text)
    engine.say(text)
    engine.runAndWait()
