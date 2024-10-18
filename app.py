from flask import Flask, request, jsonify, render_template
import json
import openai

app = Flask(__name__)

with open('medicine_data.json', 'r', encoding='utf-8') as f:
    medicine_data = json.load(f)

openai.api_key = "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"

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('searchTerm', '').lower()
    filtered_data = [item for item in medicine_data if search_term in item['product_name'].lower()]
    sorted_data = sorted(filtered_data, key=lambda x: float(x['product_price'].replace('₹', '')))
    
    for i, item in enumerate(sorted_data):
        next_index_1 = (i + 1) % len(medicine_data)
        next_index_2 = (i + 2) % len(medicine_data)
        alternative_1 = medicine_data[next_index_1]
        alternative_2 = medicine_data[next_index_2]
        item['alternatives'] = [alternative_1, alternative_2]

    return jsonify(sorted_data)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_input = data.get('message')
    search_term = data.get('searchTerm', '')

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        messages = [{"role": "system", "content": "You are Ivy, a helpful assistant and medication advisor."}]
        
        if search_term:
            messages.append({"role": "user", "content": f"The user has recently searched for '{search_term}'."})

        messages.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150
        )

        chatbot_reply = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": chatbot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
