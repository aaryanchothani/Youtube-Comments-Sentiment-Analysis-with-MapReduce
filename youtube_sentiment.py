import os
import time
from googleapiclient.discovery import build
from nltk.sentiment import SentimentIntensityAnalyzer
import subprocess

API_KEY = ''  

def get_youtube_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    comments = []
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=5000,
        pageToken=None
    )
    
    while request:
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        
        request = youtube.commentThreads().list_next(request, response)

    return comments

def get_video_metadata(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    )
    response = request.execute()

    if response['items']:
        video_info = response['items'][0]
        title = video_info['snippet']['title']
        description = video_info['snippet']['description']
        channel_title = video_info['snippet']['channelTitle']
        published_at = video_info['snippet']['publishedAt']
        view_count = video_info['statistics'].get('viewCount', 0)
        like_count = video_info['statistics'].get('likeCount', 0)
        dislike_count = video_info['statistics'].get('dislikeCount', 0)  # Note: Dislike count is now deprecated in some cases.
        comment_count = video_info['statistics'].get('commentCount', 0)

        return {
            "title": title,
            "description": description,
            "channel_title": channel_title,
            "published_at": published_at,
            "view_count": view_count,
            "like_count": like_count,
            "dislike_count": dislike_count,
            "comment_count": comment_count
        }
    return None

def write_comments_to_file(comments, filename='comments.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for comment in comments:
            f.write(comment + '\n')
    
    
sentiment_counts_normal = {'positive': 0, 'negative': 0, 'neutral': 0}

def simple_sentiment_analysis(comment):
    sia = SentimentIntensityAnalyzer()

    comment = comment[1].strip()

    if comment:  
        score = sia.polarity_scores(comment)['compound']
        if score > 0.05:
            sentiment = 'positive'
        elif score < -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        sentiment_counts_normal[sentiment] += 1

def run_map_reduce(comments):
    try:
        start_time = time.time()

        mapper_output = subprocess.run(
            ['python', '1.py'],
            input='\n'.join(comments).encode('utf-8'),  # Encode input to utf-8
            text=False,
            capture_output=True,
            check=True
        )
        
        # Sort the mapper output
        sorted_output = sorted(mapper_output.stdout.decode('utf-8').splitlines())

        # Run the reducer
        reducer_output = subprocess.run(
            ['python', '2.py'],
            input='\n'.join(sorted_output).encode('utf-8'),
            text=False,
            capture_output=True,
            check=True
        )
        end_time = time.time()

        elapsed_time = end_time - start_time
        sentiment_counts = parse_sentiment_counts(reducer_output.stdout.decode('utf-8'))

        return sentiment_counts, elapsed_time
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr.decode('utf-8')}")
        return None, None

def parse_sentiment_counts(output):
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for line in output.splitlines():
        if line.strip(): 
            sentiment, count = line.split('\t')
            count = int(count.strip()) 

            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] = count
            else:
                print(f"Unexpected sentiment found: {sentiment}")
    
    return sentiment_counts


def analyze_youtube_video(video_url):
    video_id = video_url.split('v=')[-1]  

    comments = get_youtube_comments(video_id)
    write_comments_to_file(comments)
    
    start_time = time.time()  

    with open('comments.txt', 'r', encoding='utf-8') as f:
        comments = f.readlines()
    
    for comment in enumerate(comments):
        simple_sentiment_analysis(comment)
    
    elapsed_time_normal = time.time() - start_time

    # Run MapReduce sentiment analysis
    sentiment_counts_map_reduce, elapsed_time_map_reduce = run_map_reduce(comments)

    video_metadata = get_video_metadata(video_id) 

    return {
        "video_metadata": video_metadata,
        "normal_analysis": {
            "sentiment_counts": sentiment_counts_normal,
            "time_taken": elapsed_time_normal
        },
        "map_reduce_analysis": {
            "sentiment_counts": sentiment_counts_map_reduce,
            "time_taken": elapsed_time_map_reduce
        }
    }

if __name__ == '__main__':
    video_url = input("Enter YouTube Video URL: ")
    results = analyze_youtube_video(video_url)
    print(results)
