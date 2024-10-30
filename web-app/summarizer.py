import os
import google.generativeai as genai

# API KEY 
genai.configure(api_key= os.environ["API_KEY"])

# Model yapılandırması
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
    system_instruction="Summarize the following text:",
)

# Metin özetleme fonksiyonu
def create_summary(obj):
    
    prompt = f"Summarize the following text: {obj}"
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    
    return response.text.strip()  # Özetlenen metni al ve temizle
    