import sqlite3
con = sqlite3.connect('scores.db')
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS scores
               (id TEXT PRIMARY KEY, name REAL, score REAL)''')
con.commit()
con.close()


def get_score(id):
    if not id:
        return None

    score = None

    con = sqlite3.connect('scores.db')
    cur = con.cursor()

    for s in cur.execute("SELECT score FROM scores WHERE id=:id", {"id": id}):
        score = s[0]

    con.close()
    return score


def set_score(name, id, score):
    if not id:
        return None
    con = sqlite3.connect('scores.db')
    cur = con.cursor()

    cur.execute("INSERT INTO scores VALUES (?, ?, ?)", (id, name, score))

    con.commit()
    con.close()


def all_scores():
    con = sqlite3.connect('scores.db')
    cur = con.cursor()

    scores = []

    for row in cur.execute("SELECT * FROM scores"):
        scores.append({
            "id": row[0],
            "name": row[1],
            "score": row[2]
        })

    con.close()
    return scores
