import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from static import blackjack as bj

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    bj_game = get_blackjack_game()
    if request.method == 'POST':
        req = request.form['action'] 
        if req == "Bet" and bj_game.validateAction(req):
            bj_game.player.hands[bj_game.activeHandIndex].bet = int(request.form['bet'])
        bj_game.action(req)
    
    return render_template('blackjack.html', game=bj_game)

def get_blackjack_game(fresh_game=False):
    if fresh_game:
        bj.reset_db()
    gs = bj.get_current_gamestate()
    return bj.Game(gs)

@app.route('/about')
def about():
    connection = bj.get_db_connection()
    gamestates = connection.execute('SELECT * FROM gamestates ORDER BY id DESC').fetchall()
    connection.close()
    return render_template('about.html', gamestates=gamestates)