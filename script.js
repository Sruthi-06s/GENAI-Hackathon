//////////////////////////////////////////////////////
// 📌 ELEMENT REFERENCES
//////////////////////////////////////////////////////

const imageInput = document.getElementById("imageInput");
const fileNameText = document.getElementById("fileName");
const previewImg = document.getElementById("previewImg");
const imagePreview = document.getElementById("imagePreview");
const placeholder = document.getElementById("placeholder");

//////////////////////////////////////////////////////
// 📂 OPEN FILE PICKER WHEN BOX CLICKED
//////////////////////////////////////////////////////

placeholder.addEventListener("click", () => {
    imageInput.click();
});

//////////////////////////////////////////////////////
// 🖼️ SHOW IMAGE PREVIEW
//////////////////////////////////////////////////////

imageInput.addEventListener("change", showPreview);

function showPreview() {
    const file = imageInput.files[0];

    if (file) {
        fileNameText.textContent = file.name;

        const reader = new FileReader();
        reader.onload = function (e) {
            previewImg.src = e.target.result;
            imagePreview.style.display = "flex";
        };
        reader.readAsDataURL(file);
    }
}

//////////////////////////////////////////////////////
// 🔊 SPEECH FUNCTION (AUTO VOICE SELECTION)
//////////////////////////////////////////////////////

function speakText(text, langCode) {

    if (!("speechSynthesis" in window)) {
        alert("Speech not supported in this browser");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = langCode;
    utterance.volume = 1;
    utterance.rate = 1;
    utterance.pitch = 1;

    function speakNow() {
        const voices = speechSynthesis.getVoices();

        // Try to find matching voice
        const voice = voices.find(v =>
            v.lang.toLowerCase().includes(langCode.toLowerCase())
        );

        if (voice) utterance.voice = voice;

        speechSynthesis.cancel(); // clear previous speech
        speechSynthesis.speak(utterance);
    }

    // Voices may load late in Chrome
    if (speechSynthesis.getVoices().length === 0) {
        speechSynthesis.onvoiceschanged = speakNow;
    } else {
        speakNow();
    }
}

//////////////////////////////////////////////////////
// 🚀 MAIN FUNCTION — SEND IMAGE TO BACKEND
//////////////////////////////////////////////////////
async function uploadImage() {

    const file = imageInput.files[0];

    if (!file) {
        alert("Please select an image first.");
        return;
    }

    // 🔥 GET LANGUAGE PROPERLY
    const languageSelect = document.getElementById("language");
    const selectedLang = languageSelect.options[languageSelect.selectedIndex].value.trim();

    console.log("Selected language being sent:", selectedLang);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", selectedLang);

    document.getElementById("status").innerText = "Detecting...";

    try {
        const response = await fetch("http://127.0.0.1:8000/detect", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        let resultText = "";

        if (selectedLang === "hi") {
            resultText = `रोग का पता चला: ${data.disease}. ${data.info}`;
        }
        else if (selectedLang === "te") {
            resultText = `వ్యాధి గుర్తించబడింది: ${data.disease}. ${data.info}`;
        }
        else {
            resultText = `Disease detected: ${data.disease}. ${data.info}`;
        }

        document.getElementById("result").innerText = resultText;
        document.getElementById("status").innerText = "Done ✔";

        // 🔊 PLAY BACKEND AUDIO
        const audio = new Audio("http://127.0.0.1:8000/audio?ts=" + new Date().getTime());
        audio.play();

    } catch (error) {
        document.getElementById("status").innerText = "Error ❌";
        console.error(error);
    }
}
