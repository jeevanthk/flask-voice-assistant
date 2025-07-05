from flask import Flask, jsonify
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import threading
app = Flask(__name__)
recognizer = sr.Recognizer()
engine = pyttsx3.init()
def detect_intent(text):
    text = text.lower()
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "greeting", "Hi, how can I help you?"
    elif "time" in text:
        current_time = datetime.now().strftime("%I:%M %p")
        return "time_query", f"The current time is {current_time}."
    elif any(word in text for word in ["bye", "exit", "goodbye"]):
        return "exit", "Goodbye! Have a nice day."
    else:
        return "unknown", "Sorry, I didn't understand that."
def speak(message):
    engine.say(message)
    engine.runAndWait()
@app.route("/voice", methods=["GET"])
def handle_voice():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            print("Recognizing speech...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
    except sr.WaitTimeoutError:
        return jsonify({"error": "Listening timed out"}), 408
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Speech service error: {e}"}), 500
    except OSError:
        return jsonify({"error": "Microphone not found or not accessible"}), 500
    intent, response = detect_intent(text)
    print(f"Intent: {intent} | Response: {response}")
    threading.Thread(target=speak, args=(response,)).start()
    return jsonify({
        "text": text,
        "intent": intent,
        "response": response
    })
if __name__ == "__main__":
    app.run(debug=True)
