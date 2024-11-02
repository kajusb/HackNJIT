from flask import Flask, request, jsonify

app = Flask(__name__)

transactions = []

@app.route("/")
def home():
    return jsonify(transactions)

# GET
@app.route("/transaction/<trans_id>", methods = ["GET"])
def get_trans(trans_id):
    trans_data = {
        "trans_id": trans_id,
    }
    return jsonify(trans_data), 200

# POST
@app.route("/new_trans", methods = ["POST"])
def new_trans():
    transactions.append(request.get_json())
    return jsonify(request.get_json()), 201

if __name__ == "__main__":
    app.run(debug = True)