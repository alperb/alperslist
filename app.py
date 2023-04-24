from flask import Flask, render_template, request

from mysql.connector import connect

app = Flask(__name__)

db = connect(
    host="db",
    user="root",
    password="root123",
    database="alperslist"
)


@app.route("/", methods=["GET"])
def index():
    page = request.args.get("page", 1, type=int)
    limit = 10
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ads WHERE valid = 1 LIMIT %s OFFSET %s", (limit, (page - 1) * limit))
    ads = cursor.fetchall()
    return render_template("index.html", ads=ads, current_page=page)


@app.route("/search", methods=["POST"])
def search():
    page = request.args.get("page", 1, type=int)
    limit = 10
    cursor = db.cursor()
    query = f"SELECT * FROM ads WHERE title LIKE '{request.form['search']}' LIMIT {limit} OFFSET {(page - 1) * limit}"
    cursor.execute(query)
    ads = cursor.fetchall()
    return render_template("index.html", ads=ads, current_page=page)


@app.route("/download/<pid>", methods=["POST"])
def download(pid):
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM purchases WHERE 
                   purchase_ad = {pid} AND 
                   purchase_key = '{request.form['purchase_key']}'""")
    ad = cursor.fetchone()
    if ad:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM ads WHERE id = {pid}")
        ad_row = cursor.fetchone()
        f = open(f"uploaded/{ad_row[3]}", "r")
        contents = f.read()
        return render_template("download.html", ad=ad, contents=contents)
    return render_template("download.html", ad=ad)

@app.route("/purchased", methods=["GET"])
def purchased():
    cursor = db.cursor()
    search = request.args.get("search")

    if not search:
        cursor.execute(f"SELECT * FROM purchases")
        ads = cursor.fetchall()
        ad_ids = [ad[1] for ad in ads]
        ads = []
        for idx in range(len(ad_ids)):
            cursor.execute(f"SELECT * FROM ads LEFT JOIN purchases ON purchases.purchase_ad = ads.id  WHERE ads.id = {ad_ids[idx]} ORDER BY purchases.date DESC")
            ad = cursor.fetchall()
            for a in ad:
                print(a)
                ads.append(a)
    else:
        # check here
        cursor.execute(f"SELECT * FROM ads WHERE title LIKE '%{search}%' OR description LIKE '%{search}%'")
        ads = cursor.fetchall()
        ad_ids = [ad[0] for ad in ads]
        cursor.execute(f"SELECT * FROM purchases WHERE purchase_ad IN {tuple(ad_ids)}")
        ads = cursor.fetchall()
        ad_ids = [ad[0] for ad in ads]
        cursor.execute(f"SELECT * FROM ads WHERE id IN {tuple(ad_ids)}")
        ads = cursor.fetchall()

    return render_template("purchased.html", ads=ads)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
