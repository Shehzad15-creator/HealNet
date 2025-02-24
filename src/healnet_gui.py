import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import pygame
import speech_recognition as sr
import pyttsx3
import firebase_admin
from firebase_admin import credentials, auth, firestore
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize Tkinter Window
window = tk.Tk()
window.title("HealNet - Mental Health Companion")
window.geometry("800x600")
window.configure(bg="#E3F2FD")

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Speech Engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Function to Predict Next Mood
def predict_next_mood(user_id):
    """Predicts the next mood based on past moods."""
    mood_file = "data/mood_log.json"
    if not os.path.exists(mood_file):
        return "Not enough data to predict mood."

    with open(mood_file, "r") as f:
        moods = json.load(f)

    if user_id not in moods or len(moods[user_id]) < 5:
        return "Not enough history for predictions."

    mood_scores = {"stressed": 1, "anxious": 2, "sad": 3, "happy": 4, "angry": 2, "lonely": 1, "overwhelmed": 3, "tired": 2}
    data = moods[user_id][-10:]  # Use the last 10 mood entries

    X = np.array([i for i in range(len(data))]).reshape(-1, 1)
    y = np.array([mood_scores.get(entry["mood"], 3) for entry in data])

    model = LinearRegression()
    model.fit(X, y)

    next_mood_score = model.predict([[len(data)]])[0]

    predicted_mood = min(mood_scores, key=lambda x: abs(mood_scores[x] - next_mood_score))
    return f"Based on past trends, your next mood may be: {predicted_mood}."

# Function to Handle Chatbot Responses
def chatbot_response(user_input, user_id):
    responses = {
        "stressed": "Try deep breathing: inhale for 4 sec, hold, then exhale. Want more tips?",
        "anxious": "Focus on one thing you can control today. Need help relaxing?",
        "progress": "Generating your progress report...",
        "prediction": predict_next_mood(user_id),
    }
    return responses.get(user_input.lower(), "Tell me how you’re feeling or type 'progress' or 'prediction'.")

# Function to Send Messages
def send_message(user_input=None):
    """Handles sending a message in the chatbot."""
    user_id = "test_user"  # Temporary user ID

    if not user_input:
        user_input = user_entry.get().strip()
        user_entry.delete(0, tk.END)

    if not user_input:
        return

    chat.insert(tk.END, f"You: {user_input}\n")
    response = chatbot_response(user_input, user_id)
    chat.insert(tk.END, f"HealNet: {response}\n")

    speak(response)

# Speech Recognition
import speech_recognition as sr

def recognize_speech():
    """Converts spoken words into text with error handling."""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            chat.insert(tk.END, "🎤 Listening...\n")
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            chat.insert(tk.END, f"You (Voice): {text}\n")
            send_message(text)
    except sr.UnknownValueError:
        chat.insert(tk.END, "🤖 Sorry, I couldn't understand that. Please try again.\n")
    except sr.RequestError:
        chat.insert(tk.END, "❌ Speech recognition service is unavailable.\n")
    except AttributeError:
        chat.insert(tk.END, "❌ PyAudio is missing. Please install it using 'pip install pyaudio'.\n")

# Text to Speech
def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

# Function to Play Meditation Audio
def play_meditation_audio():
    """Plays a meditation audio file."""
    audio_file = "audio/meditation.mp3"
    if not os.path.exists(audio_file):
        chat.insert(tk.END, "Meditation audio not found.\n")
        return

    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
import pygame
import os

def play_meditation_audio():
    """Plays a meditation audio file if it exists."""
    audio_file = "audio/meditation.mp3"
    
    if not os.path.exists(audio_file):
        chat.insert(tk.END, "❌ Meditation audio file not found. Please add 'meditation.mp3' to the 'audio' folder.\n")
        return
    
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    chat.insert(tk.END, "🎵 Playing meditation music...\n")
# Function to Generate and Save Progress Report
def generate_progress_report():
    """Generates a progress report and saves as PDF."""
    report_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All Files", "*.*")])
    if not report_file:
        return

    from reportlab.pdfgen import canvas
    c = canvas.Canvas(report_file)
    c.drawString(100, 750, "HealNet - Mental Health Companion Progress Report")
    c.drawString(100, 730, "--------------------------------------------")
    c.drawString(100, 710, "Your recent mood log:")
    
    # Example Mood Data (Replace with actual user data)
    sample_moods = ["stressed", "anxious", "happy", "overwhelmed"]
    y_pos = 690
    for mood in sample_moods:
        c.drawString(100, y_pos, f"- {mood}")
        y_pos -= 20

    c.save()
    chat.insert(tk.END, f"Progress report saved: {report_file}\n")

# UI Elements
chat = tk.Text(window, width=80, height=20)
chat.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

user_entry = tk.Entry(window, width=50)
user_entry.grid(row=1, column=0, padx=10, pady=10)

send_button = tk.Button(window, text="Send", command=send_message, bg="#64B5F6", fg="white")
send_button.grid(row=1, column=1, padx=5, pady=5)

voice_button = tk.Button(window, text="🎤 Speak", command=recognize_speech, bg="#81C784", fg="white")
voice_button.grid(row=1, column=2, padx=5, pady=5)

progress_button = tk.Button(window, text="📄 Progress Report", command=generate_progress_report, bg="#FFB74D", fg="white")
progress_button.grid(row=1, column=3, padx=5, pady=5)

meditation_button = tk.Button(window, text="🎵 Meditation", command=play_meditation_audio, bg="#A1887F", fg="white")
meditation_button.grid(row=2, column=3, padx=5, pady=5)

moods = ["Stressed", "Anxious", "Sad", "Happy", "Overwhelmed", "Lonely", "Tired", "Meditation", "Progress"]
row_idx = 3
for i, mood in enumerate(moods):
    btn = tk.Button(window, text=mood, command=lambda m=mood.lower(): send_message(m), bg="#64B5F6", fg="white")
    btn.grid(row=row_idx, column=i % 4, padx=5, pady=5)
    if (i + 1) % 4 == 0:
        row_idx += 1

# Run the Application
window.mainloop()
