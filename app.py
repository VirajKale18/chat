import json
from difflib import get_close_matches
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def load_knowledge_base(file_path:str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data,file, indent=2)


def find_best_match(user_question:str, questions:list[str]) -> str|None:
    matches: list = get_close_matches(user_question,questions,n=1,cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question:str,knowledge_base:dict)->str|None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
        

def chat_bot():
    knowledge_base:dict = load_knowledge_base('knowledge_base.json')

    while True:
        user_input:str = input('You: ')

        if user_input.lower() == "quit":
            break

        best_match:str|None = find_best_match(user_input,[q["question"] for q in knowledge_base["questions"]])

        if best_match:
            answer :str = get_answer_for_question(best_match,knowledge_base)
            print(f'Bot: {answer}')
        else:
            print('Bot: I don\'t know the answer.')
            new_answeer: str = input('Type your answer or "skip" to skip: ')

            if new_answeer != 'skip':
                knowledge_base["questions"].append({"question":user_input, "answer": new_answeer})
                save_knowledge_base('knowledge_base.json',knowledge_base)
                print('Bot: Thank You! I\'ve memorized it')

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
        return jsonify({'message': answer})
    else:
        return jsonify({'message': 'I don\'t know the answer.'})

if __name__ == '__main__':
    knowledge_base = load_knowledge_base('knowledge_base.json')
    app.run(debug=True)