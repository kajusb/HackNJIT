import os
import re
import csv

# Get the current working directory
current_directory = os.getcwd()

# Construct the path to the Transactions directory
transactions_directory = os.path.join(current_directory, 'Transactions')
count = 0

# Specify the filenames
transactionsFile = "Transactions.csv"
ItemsFile = "Items.csv"

# Writing to csv file
with open(transactionsFile, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["OrderID","Amount","Tax", "Currency","Date", "Time", "FileName"])

with open(ItemsFile, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["OrderID","Name","Quantity","Amount", "VAT","VAT%", "Currency"])

try:
    # List all files in the Transactions directory
    files = os.listdir(transactions_directory)
    for file in files:
        items = []
        file_path = os.path.join(transactions_directory, file)
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            file_name = file
            write = False
            access = False
            # tax = ""
            total = 0
            # total = ""
            tax = 0
            order_no = ""
            date = ""
            time = ""
            currency = ""
            for i in range(len(lines) - 1):
                line = lines[i].strip()
                if "Order No:" in line:
                    start_index = line.find("Order No:") + len("Order No:")
                    order_no = line[start_index:].strip()

                if "Date/Time Ordered " in line:
                    date_and_time = line.replace("Date/Time Ordered (","").replace(")","")
                    date_and_time = date_and_time.split(" ")
                    # print(date_and_time)
                    date = date_and_time[0]
                    time = date_and_time[1]

                if access and line == "--------------------------------":
                    access = False

                if lines[i - 1].strip() == "Ordered:" and line == "--------------------------------":
                    access = True
                    write = True
                
                # if "Total amount:" in line:
                #     start_index = line.find("Total amount:") + len("Total amount:")
                #     total = line[start_index:].strip()

                if "VAT amount:" in line:
                    start_index = line.find("VAT amount:") + len("VAT amount:")
                    tax_curreny = line[start_index:].strip()
                    if len(tax_curreny.replace("EUR","")) < len(tax_curreny):
                        currency = "EUR"
                    else:
                        currency = "GBP"
                    # tax = tax.replace(" EUR","")
                    # tax = tax.replace(" GBP","")
                    # tax = tax.replace("[mag][bold: off]","")
                
                if access:
                    # print(lines[i])
                    pattern = re.compile(r'\d+ - \w+ // \d+\.\d{2} EUR // VAT: \d+\.\d{2}% \d+\.\d{2} EUR')
                    if pattern.match(line):
                        parts = line.replace(" -","").replace(" //","").replace("VAT: ","").split(" ")
                        # if currency == "":
                        #     currency = parts[3]
                        with open(ItemsFile, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([order_no, parts[1], parts[0], parts[2], parts[5], parts[4], parts[3]])

                        total += int(parts[0]) * float(parts[2])
                        tax += int(parts[0]) * float(parts[5])
            if write:
                with open(transactionsFile, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([order_no, round(total,2), round(tax,2), currency, date, time, file_name])
except FileNotFoundError:
    print(f"The directory {transactions_directory} does not exist.")
except PermissionError:
    print(f"Permission denied to access the directory {transactions_directory}.")