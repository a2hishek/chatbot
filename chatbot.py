import requests
import os
import speech_recognition as sr
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Set the API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You are a chatbot for general conversations. You have to respond to user queries in a friendly and light language.")

# Sarvam API key and headers
SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
headers = {
    "API-Subscription-Key": SARVAM_API_KEY,
    "Accept": "application/json"
}

# Function to Convert Speech to Text (Audio Input)
def speech_to_text(audio_file_path):
    audio_file = genai.upload_file(audio_file_path)
    # Initialize a Gemini model appropriate for your use case.
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Create the prompt.
    prompt = "Generate a transcript of the speech."

    # Pass the prompt and the audio file to Gemini.
    response = model.generate_content([prompt, audio_file])    
        
    if response:
        return response.text
    else:
        return f"Error in converting speech to text: {response.text}"

# Function to Process Text using Gemini Model
def get_chatbot_response_with_gemini(text_input, chat_history):
    # Send the user's message and get a response
    chat = chat_history
    response = chat.send_message(text_input)
    return response.text.strip()

# Function to Convert Text to Speech (Audio Output)
def text_to_speech(text, language_code="en-IN", speaker="meera"):
    url = "https://api.sarvam.ai/text-to-speech"
    
    payload = {
        "inputs": [text],
        "target_language_code": language_code,
        "speaker": speaker,
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.0,
        "speech_sample_rate": 16000,
        "enable_preprocessing": False,
        "model": "bulbul:v1"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        # Here, you can save the audio file and play it or stream it
        audio_url = response.json().get("audio_url")
        return audio_url
    else:
        return f"Error in generating speech: {response.text}"

# Capture Audio Input from the User 
def capture_audio():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening for your input...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    # Save the audio to a temporary .wav file
    audio_file_path = "user_audio.wav"
    with open(audio_file_path, "wb") as file:
        file.write(audio.get_wav_data())  # Ensure it's saved as .wav format
    
    print(f"Audio saved as {audio_file_path}")
    return audio_file_path


# Main Function to Run the Chatbot
def chatbot():
    print("Welcome to the Chatbot! You can type or speak your message. (or type 'exit' to quit)")

    # Initialize the chat history
    chat_history = model.start_chat(
        history=[{"role": "user", "parts": "Hello"},
                 {"role": "model", "parts": "Great to meet you. What would you like to know?"}]
    )
    
    while True:
        user_input = input("Message: ")
        
        if user_input.lower() == 'exit':
            print("Exiting the chatbot. Goodbye!")
            break
        
        # Check if the user entered audio input (if desired)
        if user_input.lower() == "speak":
            # Capture audio input from the user
            audio_file_path = capture_audio()
            text_input = speech_to_text(audio_file_path)
            print(f"Message: {text_input}")
        else:
            text_input = user_input
        
        # Get chatbot response using Gemini model
        response_text = get_chatbot_response_with_gemini(text_input, chat_history)
        print(f"Chatbot: {response_text}")
        
        

if __name__ == "__main__":
    chatbot()