from sklearn.feature_extraction.text import TfidfVectorizer
from flask import app, jsonify, send_file
from mlflow.tracking import MlflowClient
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import matplotlib.dates as mdates
import mlflow, joblib, io, re, os, requests
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import pickle

load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def preprocess_comment(comment):
    """Apply preprocessing transformations to a comment."""
    try:
        # Convert to lowercase
        comment = comment.lower()

        # Remove trailing and leading whitespaces
        comment = comment.strip()

        # Remove newline characters
        comment = re.sub(r'\n', ' ', comment)

        # Remove non-alphanumeric characters, except punctuation
        comment = re.sub(r'[^A-Za-z0-9\s!?.,]', '', comment)

        # Remove stopwords but retain important ones for sentiment analysis
        stop_words = set(stopwords.words('english')) - {'not', 'but', 'however', 'no', 'yet'}
        comment = ' '.join([word for word in comment.split() if word not in stop_words])

        # Lemmatize the words
        lemmatizer = WordNetLemmatizer()
        comment = ' '.join([lemmatizer.lemmatize(word) for word in comment.split()])

        return comment
    except Exception as e:
        print(f"Error in preprocessing comment: {e}")
        return comment

def load_vectorizer(vectorizer_path: str) -> TfidfVectorizer:
    """Load the saved TF-IDF vectorizer."""
    try:
        with open(vectorizer_path, 'rb') as file:
            vectorizer = joblib.load(file)
        return vectorizer
    except Exception as e:
        print(f'Error loading vectorizer from {vectorizer_path}: {e}')
        raise

def load_model(model_name: str, model_version: str):
    # Set MLflow tracking URI to your server
    mlflow.set_tracking_uri(satya_mlflow_ec2_uri)  # Replace with your MLflow tracking URI
    client = MlflowClient()

    model_uri = f"models:/{model_name}/{model_version}"
    # f"models:/satya/staging"        or            f"runs:/{run_id}/{artifact_path}" 
    model = mlflow.pyfunc.load_model(model_uri) # to load the model from s3 using mlflow.
    return model

def load_local_model(model_path: str):
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        print(f'Error loading model from {model_path}: {e}')
        raise

model = load_local_model("./models/lgbm_model.pkl")
vectorizer = load_vectorizer("./models/tfidf_vectorizer.pkl")

def analyze_youtube_video(video_id):
    """
    Fetches comments for a video_id, predicts sentiment, and returns formatted data.
    """
    comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    comments_data = []
    page_token = ""
    max_comments = 500
    slice_limit = 100  # YouTube API max results per request
    

    # 1. Fetch Comments from YouTube (Max 500)
    try:
        while len(comments_data) < max_comments:
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': slice_limit,
                'key': YOUTUBE_API_KEY,
                'pageToken': page_token,
                'textFormat': 'plainText'
            }
            response = requests.get(comments_url, params=params)
            data = response.json()
            
            # Check for API Errors (Like Comments Disabled)
            if 'error' in data:
                errors = data['error'].get('errors', [])
                if errors:
                    reason = errors[0].get('reason')
                    if reason == 'commentsDisabled':
                        return {"error": "Comments are disabled for this video."}
                    if reason == 'videoNotFound':
                        return {"error": "Video not found."}
                    if reason == 'quotaExceeded':
                        return {"error": "API Quota exceeded. Please try again later."}

            for item in data['items']:
                comment_snippet = item['snippet']['topLevelComment']['snippet']
                comments_data.append({
                    'text': comment_snippet['textOriginal'],
                    'timestamp': comment_snippet['publishedAt'],
                    'authorId': comment_snippet.get('authorChannelId', {}).get('value', 'Unknown')
                })
            
            page_token = data.get('nextPageToken')
            if not page_token:
                break
                
    except Exception as e:
        print(f"Error fetching YouTube comments: {e}")
        return {"error": str(e)}

    if not comments_data:
        return {"error": "No comments found for the provided video ID."}


    # 2. ML Prediction Logic
    try:
        
        # Preprocess
        preprocessed_comments = [preprocess_comment(comment['text']) for comment in comments_data]
        
        # Vectorize
        feature_names = vectorizer.get_feature_names_out()
        transformed_comments = vectorizer.transform(preprocessed_comments)
        transformed_comments = pd.DataFrame(transformed_comments.toarray(), columns=feature_names)

        # Predict Class
        predictions = model.predict(transformed_comments)
        
        # Predict Confidence (Probability) Note: If your model supports predict_proba, use it. Otherwise default to 1.0
        try:
            probs = model.predict_proba(transformed_comments) # why not .tolist() here
            confidence_scores = np.max(probs, axis=1).tolist()
        except AttributeError:
            confidence_scores = [1.0] * len(predictions)


        # 3. Format Response
        formatted_response = []
        for i, (comment_obj, pred, conf) in enumerate(zip(comments_data, predictions, confidence_scores)):
            formatted_response.append({
                "Original_Comment": comment_obj['text'], # sting
                "Processed_Comment": preprocessed_comments[i], # sting
                "confidence": round(float(conf), 2),
                "sentiment": int(pred),
                "timestamp": comment_obj['timestamp'], # sting
                "AuthorID": comment_obj['authorId'] # sting
            })
            
        return formatted_response

    except Exception as e:
        print(f"Error in analysis: {e}")
        return {"error": f"Prediction failed: {str(e)}"}

def generate_chart(request):

    try:
        data = request.get_json()
        sentiment_counts = data.get('sentiment_counts')
        
        if not sentiment_counts:
            return jsonify({"error": "No sentiment counts provided"}), 400

        # Prepare data for the pie chart
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [
            int(sentiment_counts.get('1', 0)),
            int(sentiment_counts.get('0', 0)),
            int(sentiment_counts.get('-1', 0))
        ]
        if sum(sizes) == 0:
            raise ValueError("Sentiment counts sum to zero")
        
        colors = ['#36A2EB', '#C9CBCF', '#FF6384']  # Blue, Gray, Red

        # Generate the pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'color': 'w'}
        )
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Save the chart to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='PNG', transparent=True)
        img_io.seek(0)
        plt.close()

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /generate_chart: {e}")
        return jsonify({"error": f"Chart generation failed: {str(e)}"}), 500

def generate_wordcloud(request):
    
    try:
        data = request.get_json()
        comments = data.get('comments')

        if not comments:
            return jsonify({"error": "No comments provided"}), 400

        # Preprocess comments
        preprocessed_comments = [preprocess_comment(comment) for comment in comments]

        # Combine all comments into a single string
        text = ' '.join(preprocessed_comments)

        # Generate the word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='black',
            colormap='Blues',
            stopwords=set(stopwords.words('english')),
            collocations=False
        ).generate(text)

        # Save the word cloud to a BytesIO object
        img_io = io.BytesIO()
        wordcloud.to_image().save(img_io, format='PNG')
        img_io.seek(0)

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /generate_wordcloud: {e}")
        return jsonify({"error": f"Word cloud generation failed: {str(e)}"}), 500

def generate_trend_graph(request):

    try:
        data = request.get_json()
        sentiment_data = data.get('sentiment_data')

        if not sentiment_data:
            return jsonify({"error": "No sentiment data provided"}), 400

        # Convert sentiment_data to DataFrame
        df = pd.DataFrame(sentiment_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Set the timestamp as the index
        df.set_index('timestamp', inplace=True)

        # Ensure the 'sentiment' column is numeric
        df['sentiment'] = df['sentiment'].astype(int)

        # Map sentiment values to labels
        sentiment_labels = {-1: 'Negative', 0: 'Neutral', 1: 'Positive'}

        # Resample the data over monthly intervals and count sentiments
        monthly_counts = df.resample('ME')['sentiment'].value_counts().unstack(fill_value=0)

        # Calculate total counts per month
        monthly_totals = monthly_counts.sum(axis=1)

        # Calculate percentages
        monthly_percentages = (monthly_counts.T / monthly_totals).T * 100

        # Ensure all sentiment columns are present
        for sentiment_value in [-1, 0, 1]:
            if sentiment_value not in monthly_percentages.columns:
                monthly_percentages[sentiment_value] = 0

        # Sort columns by sentiment value
        monthly_percentages = monthly_percentages[[-1, 0, 1]]

        # Plotting
        plt.figure(figsize=(12, 6))

        colors = {
            -1: 'red',     # Negative sentiment
            0: 'gray',     # Neutral sentiment
            1: 'green'     # Positive sentiment
        }

        for sentiment_value in [-1, 0, 1]:
            plt.plot(
                monthly_percentages.index,
                monthly_percentages[sentiment_value],
                marker='o',
                linestyle='-',
                label=sentiment_labels[sentiment_value],
                color=colors[sentiment_value]
            )

        plt.title('Monthly Sentiment Percentage Over Time')
        plt.xlabel('Month')
        plt.ylabel('Percentage of Comments (%)')
        plt.grid(True)
        plt.xticks(rotation=45)

        # Format the x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=12))

        plt.legend()
        plt.tight_layout()

        # Save the trend graph to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='PNG')
        img_io.seek(0)
        plt.close()

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /generate_trend_graph: {e}")
        return jsonify({"error": f"Trend graph generation failed: {str(e)}"}), 500