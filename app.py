import os
from flask import Flask, render_template, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from scraper.web_bvl import WebBVL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/codes.db'
db_code = SQLAlchemy(app)

class TableCode(db_code.Model):
    id = db_code.Column(db_code.Integer, primary_key=True)
    name = db_code.Column(db_code.String(50), nullable=False)
    nemonico = db_code.Column(db_code.String(50), nullable=False)

    def __repr__(self):
        return "Empresa " + self.name + " con el nemónico: " + self.nemonico

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/scrapper', methods=['GET', 'POST'])
def scrapper():

    if request.method == 'POST':
        id_selected = request.form["list_firms"]
        nem_selected = TableCode.query.all()[int(id_selected) - 1].nemonico

        init_date = request.form["init_date"]
        end_date = request.form["end_date"]

        data = WebBVL().get_data_firm(nem_selected, init_date, end_date)
        data.to_csv("downloads/" + nem_selected + ".csv")
        return redirect("/scrapper")

    else:
        files_extracted = os.listdir("downloads")
        codes = TableCode.query.all()
        return render_template('scrapper.html', codes=codes, files=files_extracted)

if __name__ == "__main__":
    app.run(debug=True)