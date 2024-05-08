from flask import Flask, render_template, request, send_file
import pytesseract
from PIL import Image
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import os

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_summary(text):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Remove stop words
    stop_words = set(stopwords.words("english"))
    filtered_sentences = [sentence for sentence in sentences if sentence.lower() not in stop_words]
    
    # Stemming
    ps = PorterStemmer()
    stemmed_sentences = [ps.stem(word) for word in filtered_sentences]
    
    # Take first 3 sentences as summary
    summary = ' '.join(stemmed_sentences[:3])
    
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return render_template('result.html', file_path=file_path)

@app.route('/preview')
def preview():
    file_path = request.args.get('file_path')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found."

@app.route('/results', methods=['POST'])
def results():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                img = Image.open(file)
                text = pytesseract.image_to_string(img)
                if text:
                    summary = generate_summary(text)
                    return render_template('result.html', text=text, summary=summary)
                else:
                    return "Text extraction failed. Please upload a clearer image."
            except Exception as e:
                return str(e)
        else:
            return "No file uploaded."

if __name__ == '__main__':
    app.run(debug=True)
