from flask import Flask, request, jsonify
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient("mongodb+srv://snnitin14:n1i2t3i4n5@cluster0.3n5freg.mongodb.net/webhook_db?retryWrites=true&w=majority&appName=Cluster0")
db = client['webhook_db']
collection = db['events']


@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    entry = {
        "event_type": event_type,
        "timestamp": datetime.utcnow()
    }

    if event_type == 'push':
        author = data['pusher']['name']
        branch = data['ref'].split('/')[-1]
        entry.update({
            "author": author,
            "branch": branch,
            "message": f'{author} pushed to {branch}'
        })

    elif event_type == 'pull_request':
        action = data['action']
        if action == 'opened':
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            entry.update({
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "message": f'{author} submitted a pull request from {from_branch} to {to_branch}'
            })

    # Save to MongoDB
    collection.insert_one(entry)
    print("Saved to DB:", entry)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
