import os
import csv
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Get current list of categories and compare it to posted category
        categories = db.execute("SELECT * FROM categories")
        categories_list = []

        for i in categories:
            categories_list.append(i["category"])

        category_name = request.form.get("category")

        if category_name not in categories_list:
            db.execute("INSERT INTO categories (category) VALUES(?)", category_name)

        if request.form.get("extend"):
            add_rule(category_name, request.form.get("extend"))
        else:
            # Only update transaction
            transaction = request.form.get("id")
            category_id = db.execute("SELECT id FROM categories WHERE category = ?", category_name)[0]["id"]
            db.execute("UPDATE transactions SET category = ?, status = ? WHERE id = ?", category_id, "catogorised", transaction)

        return redirect("/")

    else:

        apply_rules("inserted")

        # Retrieve all the transactions that do not have categories
        transactions = db.execute("SELECT * FROM transactions WHERE category IS NULL")
        category_names = db.execute("SELECT category FROM categories")

        return render_template("index.html", transactions=transactions, categories=category_names)


@app.route("/overview", methods=["GET", "POST"])
def overview():
    # Get two dictionaries and a list
    # (Column headers)
    months_years= db.execute("SELECT DISTINCT month, year FROM transactions ORDER BY year ASC, month ASC")
    i = 1

    # (Row headers)
    categories = db.execute("SELECT * FROM categories ORDER BY category")

    # (Number of columns)
    columns = []
    for i in range(len(months_years)):
        columns.append(i)

    # Empty dictionary for building the table
    dictionary_of_rows = {}

    # Get table values
    for category in categories:
        row = []

        # Get row
        for month in months_years:
            cell = db.execute("SELECT SUM(amount) as amount, category FROM transactions WHERE month = ? AND year = ? AND category = ? ORDER BY year ASC, month ASC", month["month"], month["year"], category["id"])[0]

            if cell["amount"] == None:
                cell["amount"] = ""
                cell["category"] = category["id"]
            row.append(cell)

        dictionary_of_rows.update({category["category"]:row})

    # Get total expenditure for each category / last column
    total_for_categories = {}

    for category in categories:
        total_for_category = db.execute("SELECT SUM(amount) as amount FROM transactions WHERE category IS NOT NULL AND category = ?", category["id"])[0]["amount"]
        if total_for_category == None:
            total_for_category = 0
        else:
            total_for_category = round(total_for_category, ndigits=2)
        total_for_categories.update({category["category"]: total_for_category})

    # Find total expenditure for each month / last row
    months_total= []

    for month in months_years:
        total = db.execute("SELECT SUM(amount) as amount FROM transactions WHERE month = ? AND year = ?", month["month"], month["year"])[0]["amount"]
        if total == None:
            total = 0
        else:
            total = round(total, ndigits=2)
        months_total.append(total)

    return render_template("overview.html", transactions=dictionary_of_rows, categories=categories, columns=columns, months_years=months_years, months_total=months_total, total_for_categories=total_for_categories)


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
        # Retrieve file and store it into the database
        store_database("static/" + request.form.get("fileSelect"))
        # Redirect in order to deal with categories
        return redirect("/")
    else:
        return render_template("upload.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():

    if request.method == "POST":

        if request.form.get("deregister") == "X":
            # Deregister category
            if request.form.get("category_id"):
                id = request.form.get("category_id")
                db.execute("UPDATE transactions SET category = ? WHERE category = ?", None, id)
                db.execute("DELETE FROM rules WHERE category = ?", id)
                db.execute("DELETE FROM categories WHERE id = ?", id)

            # Deregister transaction
            if request.form.get("transaction_id"):
                id = request.form.get("transaction_id")
                db.execute("DELETE FROM transactions WHERE id = ?", id)

            # Deregister rule
            if request.form.get("rule_id"):
                id = request.form.get("rule_id")
                db.execute("DELETE FROM rules WHERE id = ?", id)

        # Add rule
        if request.form.get("category"):
            add_rule(request.form.get("category"), request.form.get("keyword"))

        return redirect("/edit")

    else:

        apply_rules("inserted")

        transactions = db.execute("SELECT transactions.id, date, memo, amount, categories.category as category_name FROM transactions JOIN categories ON transactions.category = categories.id")
        categories = db.execute("SELECT * FROM categories ORDER BY category")
        rules = db.execute("SELECT rules.rule as rule, categories.category as category_name FROM rules JOIN categories ON rules.category = categories.id")

        return render_template("edit.html", transactions=transactions, categories=categories, rules=rules)


def store_database(fileSelect):
    with open(fileSelect, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Amount"] != "" and row["Amount"] != None:
                # Temporarily store the first row of amount, date and eventualy memo
                amount = -1 * float(row["Amount"])
                day = row["Date"][:-8]
                month = row["Date"][-7:-5]
                year = row["Date"][-4:]
                date = row["Date"]
                # Need to find out wheter payee or memo has useful information and consolidate it
                Payee = row["Payee"]
                Memo = row["Memo"]
                if Payee == "DEBIT":
                    memo = Memo
                elif Memo == "EFTPOS":
                    memo = Payee
                else:
                    memo = Memo + " (" + Payee + ")"

                # Store values that were temporarily stored
                db.execute("INSERT INTO transactions (amount, day, month, year, date, memo, status) VALUES(?, ?, ?, ?, ?, ?, ?)"
                                                    , amount, day, month, year, date, memo, "inserted")


def add_rule(category, rule):
    # Link category/ rule with transactions
    category_id = db.execute("SELECT id FROM categories WHERE category = ?", category)[0]["id"]

    db.execute("INSERT INTO rules (category, rule) VALUES(?, ?)", category_id, rule)


def apply_rules(status):
    rules = db.execute("SELECT * FROM rules")

    for rule in rules:
        transactions = db.execute("SELECT id FROM transactions WHERE memo LIKE ? AND status = ?", rule["rule"], status)
        for transaction in transactions:
            db.execute("UPDATE transactions SET category = ?, status = ? WHERE id = ?", rule["category"], "catogorised", transaction["id"])


