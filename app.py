import json
from difflib import get_close_matches
from flask import Flask, render_template, request, jsonify
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def preprocess_text(text):
    # Convert to lowercase and remove punctuation
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

def find_best_match(user_question:str, questions:list[str]) -> str|None:
    user_question = preprocess_text(user_question)
    questions = [preprocess_text(q) for q in questions]
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.8)
    return matches[0] if matches else None

def get_answer_for_question(question:str, knowledge_base:dict) -> str|None:
    for q in knowledge_base["questions"]:
        if preprocess_text(q["question"]) == question:
            return q["answer"]

def search_web(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find_all("div", class_="BNeawe iBp4i AP7Wnd")
        return results[0].text if results else None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

knowledge_base = load_knowledge_base('knowledge_base.json')

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.json['message']
    if user_input.lower() == "quit":
        return jsonify({'message': 'Goodbye!'})
    
    best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        if answer:
            return jsonify({'message': answer})

    # If no answer is found in knowledge base, try web search
    web_result = search_web(user_input)
    if web_result:
        return jsonify({'message': web_result})

    return jsonify({'message': 'I don\'t know the answer.'})

if __name__ == '__main__':
    app.run(debug=True)
