import sqlite3
from flask import Flask, render_template, g, request, jsonify

app = Flask(__name__)
app.config['DATABASE'] = 'Leaderboard.db'

# --- Database Connection Management ---

def get_db():
    """Opens a new database connection if there is none yet for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Web Page Route ---

@app.route('/')
def show_leaderboard():
    """Displays the leaderboard on a web page."""
    db = get_db()
    scores = db.execute(
        'SELECT Username, Score FROM Leaderboard ORDER BY Score DESC LIMIT 10'
    ).fetchall()
    return render_template('leaderboard.html', scores=scores)

# --- API Endpoint for the Game ---

@app.route('/api/add_score', methods=['POST'])
def add_score():
    """API endpoint for the game to submit a score."""
    # Check if the request contains JSON data
    if not request.json or 'username' not in request.json or 'score' not in request.json:
        return jsonify({'status': 'error', 'message': 'Invalid request format'}), 400

    username = request.json['username']
    score = request.json['score']

    try:
        score = int(score)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Score must be an integer'}), 400

    db = get_db()
    db.execute(
        'INSERT INTO Leaderboard (Username, Score) VALUES (?, ?)',
        (username, score)
    )
    db.commit()

    return jsonify({'status': 'success', 'message': 'Score added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)