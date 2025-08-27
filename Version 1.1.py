import io, base64
from PIL import Image
import mss
import google.generativeai as genai

API_KEY = "AIzaSyDiSBvSX7YDkaivNvFFcpiJOdVt4GHWc8M"
MODEL = "gemini-2.0-flash"

genai.configure(api_key=API_KEY)
SYSTEM_PROMPT = "Take the screenshot as context ONLY when needed."
model = genai.GenerativeModel(MODEL, system_instruction=SYSTEM_PROMPT)

def capture_screen(max_width=1280):
    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", raw.size, raw.rgb)
        w, h = img.size
        if w > max_width:
            img = img.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

def img_part(img_bytes: bytes):
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(img_bytes).decode()}}

while True:
    q = input("> ").strip()
    if not q:
        continue
    shot = capture_screen()
    parts = [img_part(shot), {"text": q}]
    resp = model.generate_content(parts)
    print(resp.text)
