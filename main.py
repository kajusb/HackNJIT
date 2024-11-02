from flask import Flask, request, jsonify

app = Flask(__name__)

transactions = []

@app.route("/")
def home():
    return jsonify(transactions)

# GET
@app.route("/transaction/<int:trans_id>", methods = ["GET"])
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

# PUT
@app.route("/edit_trans/<int:trans_id>", methods = ["PUT"])
def edit_trans(trans_id):
    for index, trans in enumerate(transactions):
        if trans.get("trans_id") == trans_id:
            trans.update(request.get_json())
    return jsonify(transactions)

# DELETE
@app.route("/del_trans/<int:trans_id>", methods=["DELETE"])
def del_trans(trans_id):
    for index, trans in enumerate(transactions):
        if trans.get("trans_id") == trans_id:
            deleted_trans = transactions.pop(index)
    return jsonify(transactions)
    
if __name__ == "__main__":
    app.run(debug = True)