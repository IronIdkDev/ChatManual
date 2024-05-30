from flask import Flask, request, jsonify, render_template
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string
import fitz  # PyMuPDF

app = Flask(__name__)

# Download necessary NLTK data
nltk.download('punkt')

# Placeholder for manual content
manual_content = ""

# Function to load and parse PDF content
def load_manual(file_path):
    global manual_content
    manual_content = extract_text_from_pdf(file_path)
    preprocess_text()

# Extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Preprocess the text
def preprocess_text():
    global manual_content
    manual_content = manual_content.lower()
    manual_content = re.sub(rf"[{re.escape(string.punctuation)}]", " ", manual_content)
    manual_content = re.sub(r"\s+", " ", manual_content)

# Function to answer casual conversation
def handle_conversation(query):
    greetings = ["hello", "hi", "hey"]
    if any(greeting in query.lower() for greeting in greetings):
        return "Hello! How can I assist you today?"
    else:
        return "Sorry, I'm just a manual chatbot. If you have any questions related to the manual, feel free to ask!"

def answer_query(query):
    # Check if the query is casual conversation
    casual_response = handle_conversation(query)
    if casual_response:
        return casual_response
    
    query = query.lower()
    relevant_section = None
    manual_sections = manual_content.split("\n")
    for section in manual_sections:
        section_lower = section.lower()
        if any(keyword in section_lower for keyword in query.split()):
            relevant_section = section
            break

    if relevant_section:
        return "Here's the information you need:\n" + relevant_section
    else:
        return "Sorry, I couldn't find relevant information in the manual."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and file.filename.endswith('.pdf'):
        file_path = f"uploads/{file.filename}"
        file.save(file_path)
        load_manual(file_path)
        return jsonify({"message": "Manual uploaded and processed successfully."})
    else:
        return jsonify({"message": "Invalid file format. Please upload a PDF file."}), 400

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json['query']
    response = answer_query(user_query)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
