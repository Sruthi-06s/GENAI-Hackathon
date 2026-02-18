from flask import Flask, request, jsonify, send_file
from gtts import gTTS
from openai import OpenAI
import uuid
import os

app = Flask(__name__)

# 🔑 Add your OpenAI API Key
client = OpenAI(api_key="YOUR_OPENAI_KEY")

# Detect language from text
def detect_language(text):
    if any('\u0C00' <= ch <= '\u0C7F' for ch in text):
        return "te"
    if any('\u0900' <= ch <= '\u097F' for ch in text):
        return "hi"
    return "en"


@app.route("/query", methods=["POST"])
def query():

    data = request.json
    question = data["question"]

    # Detect language
    lang = detect_language(question)

    # Ask AI in SAME language
    prompt = f"Answer the following farming question in {lang} language:\n{question}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    # Convert answer to speech
    filename = f"{uuid.uuid4()}.mp3"
    tts = gTTS(text=answer, lang=lang)
    tts.save(filename)

    return jsonify({
        "answer": answer,
        "audio": filename
    })


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_file(filename, mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(debug=True)
