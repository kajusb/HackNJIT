import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, date, time

app = Flask(__name__)
load_dotenv()

# Postgres Connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

# Gets all transactions
@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM "Transactions";')
    transactions = cur.fetchall()
    cur.close()
    conn.close()

    # Converts date and time fields to string format for JSON serialization
    for transaction in transactions:
        if isinstance(transaction.get("Date"), date):
            transaction["Date"] = transaction["Date"].strftime('%Y-%m-%d')
        if isinstance(transaction.get("Time"), time):
            transaction["Time"] = transaction["Time"].strftime('%H:%M:%S')

    return jsonify(transactions)

# GET
@app.route("/transaction/<int:trans_id>", methods=["GET"])
def get_trans(trans_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM Transactions WHERE ID = %s;", (trans_id,))
    trans_data = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(trans_data) if trans_data else ('Transaction not found', 404)

# POST
@app.route("/new_trans", methods=["POST"])
def new_trans():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO \"Transactions\" (\"OrderNumber\", \"Amount\", \"Tax\", \"Date\", \"Time\", \"Currency\") VALUES (%s, %s, %s, %s, %s, %s) RETURNING \"ID\";",
        (data["OrderNumber"], data["Amount"], data["Tax"], data["Date"], data["Time"], data["Currency"])
    )
    trans_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Transaction added"}), 200

# PUT
@app.route("/edit_trans/<int:trans_id>", methods=["PUT"])
def edit_trans(trans_id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE \"Transactions\" SET \"OrderNumber\" = %s, \"Amount\" = %s, \"Tax\" = %s, \"Date\" = %s, \"Time\" = %s, \"Currency\" = %s WHERE \"ID\" = %s;",
        (data["OrderNumber"], data["Amount"], data["Tax"], data["Date"], data["Time"], data["Currency"], trans_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Transaction updated"}), 200

# DELETE
@app.route("/del_trans/<int:trans_id>", methods=["DELETE"])
def del_trans(trans_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM \"Transactions\" WHERE \"ID\" = %s;", (trans_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Transaction deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
