import os
import json
import speech_recognition as sr
from datetime import datetime
from .translator import LanguageTranslator
from .multilingual_tts import MultilingualTTS
import asyncio

class VoiceAssistant:
    def __init__(self, disease_info_path='data/disease_info.json'):
        self.translator = LanguageTranslator()
        self.tts = MultilingualTTS()
        self.recognizer = sr.Recognizer()
        
        # Load disease information
        with open(disease_info_path, 'r', encoding='utf-8') as f:
            self.disease_info = json.load(f)
        
        # Predefined responses
        self.responses = {
            'greeting': {
                'en': 'Hello! How can I help you with your crops today?',
                'hi': 'नमस्ते! आज मैं आपकी फसलों के बारे में कैसे मदद कर सकता हूँ?',
                'bn': 'নমস্কার! আজ আমি আপনার ফসল সম্পর্কে কিভাবে সাহায্য করতে পারি?',
                'te': 'నమస్కారం! ఈరోజు మీ పంటల గురించి నేను ఎలా సహాయపడగలను?',
                'ta': 'வணக்கம்! இன்று உங்கள் பயிர்களைப் பற்றி நான் எப்படி உதவ முடியும்?'
            },
            'help': {
                'en': 'You can ask me about crop diseases, treatments, or weather. For example: "What is bacterial leaf blight?" or "How to treat brown spot?"',
                'hi': 'आप मुझसे फसल रोगों, उपचारों या मौसम के बारे में पूछ सकते हैं। उदाहरण के लिए: "बैक्टीरियल लीफ ब्लाइट क्या है?" या "भूरा धब्बा का इलाज कैसे करें?"',
                'bn': 'আপনি আমাকে ফসলের রোগ, চিকিৎসা বা আবহাওয়া সম্পর্কে জিজ্ঞাসা করতে পারেন। উদাহরণস্বরূপ: "ব্যাকটেরিয়াল লিফ ব্লাইট কী?" বা "বাদামী দাগের চিকিৎসা কীভাবে করবেন?"'
            },
            'weather_query': {
                'en': 'I can help with weather information. Please specify your location.',
                'hi': 'मैं मौसम की जानकारी में मदद कर सकता हूँ। कृपया अपना स्थान बताएं।',
                'bn': 'আমি আবহাওয়ার তথ্যে সাহায্য করতে পারি। অনুগ্রহ করে আপনার অবস্থান জানান।'
            }
        }
    
    def listen_for_speech(self, timeout=5):
        """Listen for speech input"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio)
                    return {'success': True, 'text': text}
                except sr.UnknownValueError:
                    return {'success': False, 'error': 'Could not understand audio'}
                except sr.RequestError:
                    return {'success': False, 'error': 'Speech recognition service error'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def process_query(self, text, user_language='en'):
        """Process the user's query"""
        # Translate query to English for processing
        translated_query = await self.translator.translate_text(text, 'en')
        query_en = translated_query['translated_text'].lower()
        
        response_en = ""
        
        # Check for greetings
        if any(word in query_en for word in ['hello', 'hi', 'hey', 'greetings']):
            response_en = self.responses['greeting']['en']
        
        # Check for help
        elif any(word in query_en for word in ['help', 'what can you do', 'capabilities']):
            response_en = self.responses['help']['en']
        
        # Check for disease information
        elif any(word in query_en for word in ['disease', 'infection', 'blight', 'spot', 'problem']):
            response_en = self.get_disease_info(query_en)
        
        # Check for treatment information
        elif any(word in query_en for word in ['treat', 'cure', 'medicine', 'pesticide', 'solution']):
            response_en = self.get_treatment_info(query_en)
        
        # Check for weather
        elif any(word in query_en for word in ['weather', 'temperature', 'rain', 'climate']):
            response_en = self.get_weather_info(query_en)
        
        # Default response
        else:
            response_en = "I'm not sure about that. You can ask me about crop diseases, treatments, or weather. Say 'help' for more information."
        
        # Translate response back to user's language
        translated_response = await self.translator.translate_text(response_en, user_language)
        
        return {
            'original_query': text,
            'processed_query': query_en,
            'response': translated_response['translated_text'],
            'response_language': user_language,
            'audio_file': await self.tts.text_to_speech(translated_response['translated_text'], user_language)
        }
    
    def get_disease_info(self, query):
        """Extract disease information from query"""
        for disease in self.disease_info.get('diseases', []):
            if disease['name'].lower() in query:
                return f"{disease['name']}: {disease['description']}"
        
        # Return general info if no specific disease found
        return "I found information about several crop diseases. Please specify which disease you're interested in: Bacterial Leaf Blight, Brown Spot, or Healthy Rice Leaf."
    
    def get_treatment_info(self, query):
        """Extract treatment information from query"""
        for disease in self.disease_info.get('diseases', []):
            if disease['name'].lower() in query:
                return f"Treatment for {disease['name']}: {disease.get('treatment', 'Consult local agricultural expert for treatment options.')}"
        
        return "For treatment information, please specify which disease you want to treat."
    
    def get_weather_info(self, query):
        """Get weather information using free API"""
        # Using OpenWeatherMap free API
        api_key = os.getenv('OPENWEATHER_API_KEY', '')  # Get from environment variable
        if not api_key:
            return "Weather information requires an API key. Please set OPENWEATHER_API_KEY environment variable."
        
        # Extract location from query (simplified)
        location = self.extract_location(query) or 'Delhi'
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                return f"Weather in {location}: {data['weather'][0]['description']}, Temperature: {data['main']['temp']}°C, Humidity: {data['main']['humidity']}%"
            else:
                return f"Could not fetch weather for {location}"
        except:
            return "Weather service temporarily unavailable"
    
    def extract_location(self, query):
        """Simple location extraction from query"""
        # This is a simplified version - you can enhance this with NLP
        words = query.split()
        location_indicators = ['in', 'at', 'for', 'weather of']
        
        for i, word in enumerate(words):
            if word in location_indicators and i + 1 < len(words):
                return words[i + 1]
        
        return None