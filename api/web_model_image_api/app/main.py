from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
import os

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Load model dan tokenizer
model = load_model('gambling_detection_model_new_balanced.h5')

with open('tokenizer_new_balanced.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Maksimal panjang sequence (harus sesuai dengan model training)
maxlen = 100

# Fungsi untuk membersihkan teks
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)  
    text = re.sub(r'\s+', ' ', text).strip()  
    text = text.lower()  
    return text

# Fungsi untuk prediksi teks
def predict_text(text):
    text_cleaned = clean_text(text)
    
    # Tokenisasi dan padding
    sequence = tokenizer.texts_to_sequences([text_cleaned])  
    padded = pad_sequences(sequence, maxlen=maxlen)  
    
    prediction = model.predict(padded)[0][0]
    
    return {
        'text': text,
        'probability': float(prediction),
        'prediction': 'Judi Online' if prediction > 0.5 else 'Bukan Judi Online'
    }

# Endpoint untuk prediksi
@app.route('/predict', methods=['POST'])
def predict_endpoint():
    try:
        input_data = request.get_json()
        text = input_data.get('text', '')
        if not text:
            return jsonify({'error': 'Field `text` is required'}), 400
        result = predict_text(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Jalankan aplikasi
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Baca port dari environment atau gunakan 8000
    app.run(host='0.0.0.0', port=port)