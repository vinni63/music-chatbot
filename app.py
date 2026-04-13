import os
from googleapiclient.discovery import build
YOUTUBE_API_KEY = "AIzaSyDg7EeWdJ4HYQT-HWv0lTznE3Dn41HM3aE"

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
from flask import Flask, render_template, request, jsonify
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
nltk.download('punkt')

training_sentences = [
    "I am happy", "feeling great", "awesome mood",
    "I am sad", "feeling down", "very depressed",
    "I love someone", "romantic mood", "in love"
]

labels = [
    "happy", "happy", "happy",
    "sad", "sad", "sad",
    "love", "love", "love"
]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(training_sentences)

model = MultinomialNB()
model.fit(X, labels)

def predict_mood(text):
    text_vec = vectorizer.transform([text])
    return model.predict(text_vec)[0]
def get_recommendations(user_input):
    mood = predict_mood(user_input)

    if mood == "happy":
        query = "happy songs"
    elif mood == "sad":
        query = "sad songs"
    elif mood == "love":
        query = "romantic songs"
    else:
        query = "top songs"

    request = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=5,
        type="video"
    )
    response = request.execute()

    songs = []

    for item in response['items']:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        url = f"https://www.youtube.com/watch?v={video_id}"

        songs.append(f'<a href="{url}" target="_blank">{title}</a>')

    return songs
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    response = get_recommendations(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)