import pyttsx3
import speech_recognition as sr

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Simple keyword-based intents
keywords = {
    "weather": ["rain", "temperature", "weather"],
    "fertilizer": ["fertilizer", "manure", "nutrient"],
    "disease": ["spot", "blight", "infection", "disease"],
    "irrigation": ["water", "irrigation", "watering"]
}

# Static responses
responses = {
    "weather": "Check local weather forecast before farming.",
    "fertilizer": "Use balanced fertilizer depending on the crop.",
    "disease": "Inspect leaves, remove infected parts, and apply treatment.",
    "irrigation": "Ensure proper irrigation. Avoid overwatering.",
    "general": "Focus on healthy practices for better yield."
}

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return "Sorry, I could not understand."

def detect_intent(text):
    text = text.lower()
    for intent, words in keywords.items():
        if any(word in text for word in words):
            return intent
    return "general"

def main():
    query = listen()
    print("You said:", query)
    intent = detect_intent(query)
    response = responses[intent]
    print("SmartKrishi says:", response)
    speak(response)

if __name__ == "__main__":
    main()
