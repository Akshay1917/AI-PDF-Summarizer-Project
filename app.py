import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf_utils import extract_text_from_pdf
from summarizer import AISummarizer

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize AI Summarizer
# Note: In production, you might want to load this lazily or in a separate worker
ai_summarizer = None

def get_summarizer():
    global ai_summarizer
    if ai_summarizer is None:
        ai_summarizer = AISummarizer()
    return ai_summarizer

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        text = extract_text_from_pdf(file_path)
        
        if text:
            return jsonify({
                "message": "File uploaded successfully",
                "filename": filename,
                "text_preview": text[:500] + "...",
                "full_text": text
            })
        else:
            return jsonify({"error": "Failed to extract text from PDF"}), 500
            
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        summarizer = get_summarizer()
        summary = summarizer.summarize(text)
        key_points = summarizer.extract_key_points(summary)
        keywords = summarizer.extract_keywords(text)
        
        return jsonify({
            "summary": summary,
            "key_points": key_points,
            "keywords": keywords
        })
    except Exception as e:
        print(f"Summarization error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
