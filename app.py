
from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mysecretkey123"

MENU = {
    "Espresso": {"price": 3.00, "stock": 20},
    "Latte": {"price": 4.50, "stock": 15},
    "Cappuccino": {"price": 4.00, "stock": 12},
    "Tea": {"price": 2.50, "stock": 25},
    "Muffin": {"price": 2.75, "stock": 12},
}

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "server": {"password": "server123", "role": "server"}
}

sales_history = []

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in USERS and USERS[u]["password"] == p:
            session["user"] = u
            session["role"] = USERS[u]["role"]
            return redirect("/admin" if session["role"] == "admin" else "/server")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/server")
def server_home():
    if session.get("role") != "server":
        return redirect("/")
    return render_template("server_home.html", menu=MENU)

@app.route("/admin")
def admin_home():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin_home.html")

@app.route("/order", methods=["GET","POST"])
def order():
    if session.get("role") != "server":
        return redirect("/")
    if request.method == "POST":
        order_items = {}
        for item in MENU:
            qty = int(request.form.get(item, 0))
            if qty > 0:
                order_items[item] = qty
                MENU[item]["stock"] -= qty

        subtotal = sum(MENU[i]["price"] * q for i, q in order_items.items())
        tax = subtotal * 0.07
        total = subtotal + tax

        sales_history.append({
            "items": order_items,
            "total": total,
            "time": datetime.now()
        })

        return render_template("receipt.html",
                               order=order_items,
                               menu=MENU,
                               subtotal=subtotal,
                               tax=tax,
                               total=total)

    return render_template("order.html", menu=MENU)

@app.route("/inventory", methods=["GET","POST"])
def inventory():
    if session.get("role") != "admin":
        return redirect("/")
    if request.method == "POST":
        item = request.form["item"]
        amt = int(request.form["amount"])
        MENU[item]["stock"] += amt
    return render_template("inventory.html", menu=MENU)

@app.route("/reports")
def reports():
    if session.get("role") != "admin":
        return redirect("/")
    total_revenue = sum(s["total"] for s in sales_history)

    item_totals = {}
    for sale in sales_history:
        for item, qty in sale["items"].items():
            item_totals[item] = item_totals.get(item, 0) + qty

    return render_template("reports.html",
                           sales=sales_history,
                           item_totals=item_totals,
                           total_revenue=total_revenue)

@app.route("/orders")
def orders():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("orders.html", sales=sales_history)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
