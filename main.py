# Imports
import os
import csv
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, date, time
from flask_cors import CORS


# Flask
app = Flask(__name__)
CORS(app)
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

# Function to insert transactions from CSV
def insert_transactions_from_csv(conn, csv_file_path):
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        with conn.cursor() as cur:
            for row in reader:

                # Remove Orders with Blank #
                if row["OrderNumber"] == "":
                    continue
                
                # Parse the date from DD-MM-YYYY to YYYY-MM-DD
                date_str = datetime.strptime(row["Date"], '%d-%m-%Y').date()

                # Add transactions to table while reading
                cur.execute(
                    '''
                    INSERT INTO "Transactions" ("OrderNumber", "Amount", "Tax", "Date", "Time", "Currency")
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING "ID";
                    ''',
                    (
                        row["OrderNumber"],
                        float(row["Amount"]),
                        float(row["Tax"]),
                        date_str,
                        row["Time"],
                        row["Currency"]
                    )
                )
            conn.commit()

# Function to insert items from CSV
def insert_items_from_csv(conn, csv_file_path):
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        with conn.cursor() as cur:
            for row in reader:

                # Add items to table while reading
                cur.execute(
                    '''
                    INSERT INTO "Items" ("Currency", "TransactionID", "Quantity", "itemName", "Amount", "VAT", "VATPercent")
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING "ID";
                    ''',
                    (
                        row["Currency"],
                        row["TransactionID"],
                        row["Quantity"],
                        row["itemName"],
                        row["Amount"],
                        row["VAT"],
                        row["VATPercent"].replace("%", "")
                    ), 
                )
                
                # Match item's transaction ID with transaction's ID
                cur.execute(
                    '''
                    UPDATE "Items"
                    SET "TransactionID" = "Transactions"."ID"
                    FROM "Transactions"
                    WHERE "TransactionID" = "OrderNumber"       
                    '''
                )
            conn.commit()

# Populate database from CSV files
@app.route("/populate_db", methods=["POST"])
def populate_db():
    conn = get_db_connection()
    try:
        insert_transactions_from_csv(conn, 'Transactions.csv')
        insert_items_from_csv(conn, 'Items.csv')
        return jsonify({"message": "Database populated successfully!"}), 200
    finally:
        conn.close()

# Gets all transactions
@app.route("/")
def home():
    conn = get_db_connection()
    
    # Fetch transactions
    trans_cur = conn.cursor(cursor_factory=RealDictCursor)
    trans_cur.execute('SELECT * FROM "Transactions" ORDER BY "Date" ASC')
    transactions = trans_cur.fetchall()
    
    # Convert date and time fields to string format for JSON serialization
    for transaction in transactions:
        transaction["Amount"] = transaction.get("Amount").replace("$", "")
        if isinstance(transaction.get("Date"), date):
            transaction["Date"] = transaction["Date"].strftime('%Y-%m-%d')
        if isinstance(transaction.get("Time"), time):
            transaction["Time"] = transaction["Time"].strftime('%H:%M:%S')

        # Initialize items list in the transaction
        transaction["Items"] = []
    
    # Fetch items
    items_cur = conn.cursor(cursor_factory=RealDictCursor)
    items_cur.execute('SELECT * FROM "Items";')
    items = items_cur.fetchall()
    
    # Close cursors
    trans_cur.close()

    # Group items by transaction
    for item in items:
        item["Amount"] = item.get("Amount").replace("$", "")

        transaction_id = item["TransactionID"]
        for transaction in transactions:
            if transaction["ID"] == transaction_id:
                transaction["Items"].append(item)
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

@app.route("/item/<int:item_id>", methods=["GET"])
def get_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM \"Items\" WHERE \"ID\" = %s;", (item_id,))
    item_data = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(item_data) if item_data else ('Item not found', 404)

@app.route("/new_item", methods=["POST"])
def new_item():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO \"Items\" (\"Currency\", \"TransactionID\", \"Quantity\", \"itemName\", \"Amount\", \"VAT\", \"VATPercent\") VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING \"ID\";",
        (data["Currency"], data["TransactionID"], data["Quantity"], data["itemName"], data["Amount"], data["VAT"], data["VATPercent"])
    )
    item_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Item added"}), 200

@app.route("/edit_item/<int:item_id>", methods=["PUT"])
def edit_item(item_id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE \"Items\" SET \"Currency\" = %s, \"TransactionID\" = %s, \"Quantity\" = %s, \"itemName\" = %s, \"Amount\" = %s, \"VAT\" = %s, \"VATPercent\" = %s WHERE \"ID\" = %s;",
        (data["Currency"], data["TransactionID"], data["Quantity"], data["itemName"], data["Amount"], data["VAT"], data["VATPercent"], item_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Item updated"}), 200

@app.route("/del_item/<int:item_id>", methods=["DELETE"])
def del_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM \"Items\" WHERE \"ID\" = %s;", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Item deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
