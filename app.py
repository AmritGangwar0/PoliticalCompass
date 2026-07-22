from flask import Flask, render_template, request, jsonify
import json
import numpy as np
from scipy.spatial.distance import euclidean
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Flask server
app = Flask(__name__)


# Load party vectors
with open("data/parties.json", "r", encoding="utf-8") as f:
    parties = json.load(f)


# Distance function
# Ignore skipped questions
def distance(user, party):

    u = []
    p = []

    for a, b in zip(user, party):

        if a is not None:
            u.append(a)
            p.append(b)

    if len(u) == 0:
        return float("inf")

    return euclidean(u, p)


# Find top 3 nearest parties
def nearest_parties(user):

    distances = []

    for party, vec in parties.items():

        d = distance(user, vec)

        distances.append((party, d))

    distances.sort(key=lambda x: x[1])

    return distances[:3]


# Replace skipped values for PCA
def fill_missing(user):

    filled = []

    party_matrix = np.array(list(parties.values()))

    for i, x in enumerate(user):

        if x is None:

            mean_value = np.mean(party_matrix[:, i])

            filled.append(mean_value)

        else:

            filled.append(x)

    return filled


# PCA Plot
def create_plot(user):

    user = fill_missing(user)

    X = np.array(list(parties.values()))

    names = list(parties.keys())

    X = np.vstack((X, user))

    pca = PCA(n_components=2)

    Y = pca.fit_transform(X)

    plt.figure(figsize=(9, 9))

    # parties

    for i, name in enumerate(names):

        plt.scatter(Y[i, 0], Y[i, 1], s=100)

        plt.text(
            Y[i, 0],
            Y[i, 1],
            name,
            fontsize=9
        )

    # user

    plt.scatter(
        Y[-1, 0],
        Y[-1, 1],
        s=250,
        c="red"
    )

    plt.text(
        Y[-1, 0],
        Y[-1, 1],
        "YOU",
        fontsize=12
    )

    plt.title("Political Space (PCA Projection)")

    plt.grid()

    plt.tight_layout()

    plt.savefig("static/plots/result.png")

    plt.close()


# Home page
@app.route("/")
def home():

    return render_template("index.html")

# Send questions to frontend
@app.route("/questions")
def questions():

    with open("data/questions.json", "r", encoding="utf-8") as f:

        q = json.load(f)

    return jsonify(q)


# Receive user answers
@app.route("/submit", methods=["POST"])
def submit():

    data = request.get_json()

    user = data["scores"]
    
    create_plot(user)

    closest = nearest_parties(user)

    results = []

    for party, dist in closest:

        similarity = round(100 / (1 + dist), 1)

        results.append({
            "party": party,
            "distance": round(dist, 3),
            "similarity": similarity
        })

    return jsonify({

        "closest": results,

        "plot": "/static/plots/result.png"

    })


# Run server
if __name__ == "__main__":

    app.run(debug=True) 
    
    