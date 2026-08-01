from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Secret key for session
app.secret_key = "farmer_secret_key"


# ---------------- MONGODB CONNECTION ----------------

client = MongoClient("mongodb+srv://71382502164sowmiya_db_user:sowmiya2008@cluster0.6jpmchn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
try:
    client.admin.command("ping")
    print("MongoDB Connected Successfully")
except Exception as e:
    print("MongoDB Connection Failed:", e)


db = client["Farmer_Database"]

farmers_collection = db["farmers"]
subsidy_collection = db["subsidy"]


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- FARMER REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        farmers_collection.insert_one({

            "name": request.form.get("name"),
            "aadhaar": request.form.get("aadhaar"),
            "phone": request.form.get("phone"),
            "village": request.form.get("village"),
            "land": request.form.get("land"),
            "username": request.form.get("username"),
            "password": request.form.get("password")

        })

        return "Registration Successful"

    return render_template("register.html")



# ---------------- FARMER LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")


        farmer = farmers_collection.find_one({

            "username": username,
            "password": password

        })


        if farmer:

            session["farmer"] = farmer["name"]

            return redirect("/dashboard")

        else:

            return "Invalid Username or Password"


    return render_template("login.html")



# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "farmer" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["farmer"]
    )



# ---------------- APPLY SUBSIDY ----------------

@app.route("/apply", methods=["GET", "POST"])
def apply():

    if "farmer" not in session:
        return redirect("/login")


    if request.method == "POST":


        subsidy_collection.insert_one({

            "name": request.form.get("name"),

            "subsidy_type": request.form.get("subsidy_type"),

            "amount": request.form.get("amount"),

            "reason": request.form.get("reason"),

            "status": "Pending"

        })


        return redirect("/status")


    return render_template("apply.html")



# ---------------- VIEW STATUS ----------------

@app.route("/status")
def status():


    data = list(
        subsidy_collection.find()
    )


    return render_template(
        "status.html",
        data=data
    )



# ---------------- ADMIN LOGIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin():


    if request.method == "POST":


        username = request.form.get("username")

        password = request.form.get("password")


        if username == "admin" and password == "admin123":


            session["admin"] = True

            return redirect("/admin_dashboard")


        else:

            return "Invalid Admin Username or Password"



    return render_template("admin_login.html")



# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin_dashboard")
def admin_dashboard():


    if "admin" not in session:
        return redirect("/admin")


    data = list(
        subsidy_collection.find()
    )


    return render_template(
        "admin_dashboard.html",
        data=data
    )



# ---------------- APPROVE SUBSIDY ----------------

@app.route("/approve/<id>")
def approve(id):


    subsidy_collection.update_one(

        {
            "_id": ObjectId(id)
        },

        {
            "$set":
            {
                "status": "Approved"
            }
        }

    )


    return redirect("/admin_dashboard")



# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



# ---------------- RUN ----------------

if __name__ == "__main__":

    app.run(debug=True)