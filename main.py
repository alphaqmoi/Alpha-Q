from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
import logging
from enhanced_ai import EnhancedAI
from memory import append_conversation

app = Flask(__name__)
swagger = Swagger(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIApp")

# AI Instance
ai = EnhancedAI()

@app.route("/ask", methods=["POST"])
@swag_from({
    'tags': ['Ask AI'],
    'parameters': [
        {
            'name': 'message',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user_id': {'type': 'string'},
                    'history': {'type': 'array'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'AI response with reasoning',
            'examples': {
                'application/json': {
                    "AI Message": "...",
                    "Reasoning": "...",
                    "Model Used": "gpt2",
                    "Task": "text-generation"
                }
            }
        }
    }
})
def ask():
    data = request.get_json()
    message = data.get("message")
    user_id = data.get("user_id", "anonymous")
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = ai.generate_response(message, conversation_history=history)
    append_conversation(user_id, message, response)

    return jsonify({
        "AI Message": response["message"],
        "Reasoning": response["reasoning"],
        "Model Used": response["model"],
        "Task": response["task"]
    })

@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.get_json().get("text", "")
    return jsonify(ai.summarize_text(text))

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.get_json().get("text", "")
    return jsonify(ai.process_large_text(text))

@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.get_json().get("expression", "")
    return jsonify(ai.calculate_expression(expression))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
