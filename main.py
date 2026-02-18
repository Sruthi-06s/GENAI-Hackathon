from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import json
import os
import time

from model.predict import predict
from tts.speak import speak

app = FastAPI(title="AI Rice Crop Disease Detector")

# ---------------- CORS ---------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Load Disease Info ---------------- #
with open("data/disease_info.json", encoding="utf-8") as f:
    disease_data = json.load(f)

current_audio_file = None


# ---------------- Root ---------------- #
@app.get("/")
async def root():
    return {"message": "Rice Disease API Running"}


# ---------------- Detection ---------------- #
@app.post("/detect")
async def detect(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    global current_audio_file

    # 🔥 CLEAN LANGUAGE VALUE
    language = language.strip().lower()

    # 🔥 FORCE VALID LANGUAGE CODES
    if language not in ["en", "hi", "te"]:
        language = "en"

    print("Language received from frontend:", language)

    temp_path = "temp.jpg"

    # Save image
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Predict disease
    disease = predict(temp_path)

    # Get info in selected language
    disease_info = disease_data.get(disease, {})
    info = disease_info.get(language, disease_info.get("en", "No info available"))

    # Disease name translations
    disease_names = {
        "Bacterial Leaf Blight": {
            "en": "Bacterial Leaf Blight",
            "hi": "बैक्टीरियल लीफ ब्लाइट",
            "te": "బ్యాక్టీరియల్ లీఫ్ బ్లైట్"
        },
        "Brown Spot": {
            "en": "Brown Spot",
            "hi": "ब्राउन स्पॉट",
            "te": "బ్రౌన్ స్పాట్"
        },
        "Healthy Rice Leaf": {
            "en": "Healthy Rice Leaf",
            "hi": "स्वस्थ धान की पत्ती",
            "te": "ఆరోగ్యకరమైన వరి ఆకు"
        }
    }

    disease_name = disease_names.get(disease, {}).get(language, disease)

    # 🔥 TEXT IN SELECTED LANGUAGE
    if language == "hi":
        text = f"रोग का पता चला: {disease_name}. {info}"
    elif language == "te":
        text = f"వ్యాధి గుర్తించబడింది: {disease_name}. {info}"
    else:
        text = f"Disease detected: {disease_name}. {info}"

    print("Text sent to TTS:", text)

    # 🔊 Generate speech
    try:
        audio_file = speak(text, language)
        current_audio_file = audio_file
        print("Audio generated:", audio_file)

    except Exception as e:
        print("Speech error:", e)
        current_audio_file = None

    # Remove temp image
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {
        "disease": disease_name,
        "info": info,
        "language": language,
        "audio_available": current_audio_file is not None
    }


# ---------------- Serve Audio ---------------- #
@app.get("/audio")
async def get_audio():
    global current_audio_file

    if current_audio_file and os.path.exists(current_audio_file):
        return FileResponse(
            current_audio_file,
            media_type="audio/mpeg",
            filename="speech.mp3"
        )

    return JSONResponse(
        status_code=404,
        content={"message": "No audio file"}
    )
