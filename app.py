from flask import Flask, render_template, request, redirect
import ml

app = Flask(__name__)

@app.route('/')
def display_data():
    return render_template('main.html')

@app.route('/result')
def result():
    return render_template('Result.html', suggestions = suggestions)

@app.route('/enregistrer', methods=['POST', 'GET'])
def enregistrer():
    global titre_stocke, auteur_stocke
    titre = request.form['texte1']
    auteur = request.form['texte2']
    titre_stocke = titre
    auteur_stocke = auteur
    analyse()
    return redirect('/result')

def analyse():
    global suggestions
    titre = request.form['texte1']
    auteur = request.form['texte2']
    suggestions = ml.analyse(titre, auteur)
    return redirect('/result')