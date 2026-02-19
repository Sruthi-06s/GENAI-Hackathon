from gtts import gTTS
import time

def speak(text, language):

    filename = f"audio_{int(time.time())}.mp3"

    # Clean language value (remove spaces etc)
    language = language.strip().lower()

    # Strict mapping
    lang_map = {
        "en": "en",
        "hi": "hi",
        "te": "te"
    }

    lang_code = lang_map.get(language, "en")

    print("Language received in speak():", language)
    print("Language used for gTTS:", lang_code)
    print("Text:", text)

    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(filename)

    return filename
