import streamlit as st
import subprocess
import time
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import re
from youtube_sentiment import analyze_youtube_video 
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer

col1, col2, col3 = st.columns([4, 3, 1]) 

with col2:
    st.image('youtube.png', width=50)

st.markdown("<h2 style='vertical-align: top;'>YouTube Video Analysis</h2>", unsafe_allow_html=True)

video_url = st.text_input("Enter YouTube Video URL:", "https://www.youtube.com/watch?v=5bId3N7QZec")

if st.button("Analyze"):
    if video_url:
        with st.spinner("Processing..."):
            results = analyze_youtube_video(video_url)

        sentiment_counts_normal = results["normal_analysis"]["sentiment_counts"]
        time_normal = results["normal_analysis"]["time_taken"]

        sentiment_counts_map_reduce = results["map_reduce_analysis"]["sentiment_counts"]
        time_map_reduce = results["map_reduce_analysis"]["time_taken"]
        
        video_title = results["video_metadata"]["title"]
        channel_title = results["video_metadata"]["channel_title"]
        upload_date = results["video_metadata"]["published_at"]

        upload_date_obj = datetime.strptime(upload_date, "%Y-%m-%dT%H:%M:%SZ")

        formatted_upload_date = upload_date_obj.strftime("%B %d, %Y")

        st.markdown(f"""
            <div style='background-color: rgb(38 39 48); padding: 8px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                <h2 style='color: rgb(150 150 150); margin-bottom: 5px;'>{video_title}</h2>
                <h4 style='color: rgb(78 78 78);'>by {channel_title}</h4>
                <p style='font-size: 16px; color: #6c757d;'>Uploaded on {formatted_upload_date}</p>
            </div>
            """, unsafe_allow_html=True)

        engagement_data = {
            "Metric": ["Views", "Likes", "Dislikes", "Comments"],
            "Count": [
                results["video_metadata"]["view_count"],
                results["video_metadata"]["like_count"],
                results["video_metadata"]["dislike_count"],
                results["video_metadata"]["comment_count"]
            ]
        }
        df_engagement = pd.DataFrame(engagement_data)
        st.bar_chart(df_engagement.set_index("Metric"))

        
        video_description = results["video_metadata"]["description"]

        # Sentiment Analysis
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(video_description)

        # Extracting keywords (simple frequency analysis)
        words = re.findall(r'\w+', video_description.lower())
        most_common_words = Counter(words).most_common(10)
        common_words_df = pd.DataFrame(most_common_words, columns=['Word', 'Frequency'])

        # Generate Word Cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(video_description)

        # Display Results in Streamlit
        st.write("### Video Description Analysis")
        st.write("#### Sentiment Analysis")
        st.write("Positive:", sentiment_scores['pos'])
        st.write("Negative:", sentiment_scores['neg'])
        st.write("Neutral:", sentiment_scores['neu'])
        
        # Display Word Cloud
        st.write("### Word Cloud of Description")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)


        st.write("### Comment Analysis")
        # Display Normal Sentiment Analysis Results
        st.write("### Normal Sentiment Analysis")
        st.write("Positive:", sentiment_counts_normal['positive'])
        st.write("Negative:", sentiment_counts_normal['negative'])
        st.write("Neutral:", sentiment_counts_normal['neutral'])
        st.write("Time Taken:", time_normal, "seconds")

        # Display MapReduce Sentiment Analysis Results
        st.write("### MapReduce Sentiment Analysis")
        st.write("Positive:", sentiment_counts_map_reduce['positive'])
        st.write("Negative:", sentiment_counts_map_reduce['negative'])
        st.write("Neutral:", sentiment_counts_map_reduce['neutral'])
        st.write("Time Taken:", time_map_reduce, "seconds")

        # Display a chart comparing the time taken for both analyses
        time_data = {
            "Method": ["Normal Analysis", "MapReduce Analysis"],
            "Time Taken (seconds)": [time_normal, time_map_reduce]
        }


        df_time = pd.DataFrame(time_data)

        col1, col2 = st.columns(2)

        with col1:
            # Use bar chart to display time taken
            st.write("### Time Taken Comparison")
            st.bar_chart(df_time.set_index("Method"))

        with col2:
            # Create and display a pie chart for sentiment distribution
            sentiment_counts = [
                sentiment_counts_normal['positive'],
                sentiment_counts_normal['negative'],
                sentiment_counts_normal['neutral']
            ]
            sentiment_labels = ['Positive', 'Negative', 'Neutral']

            fig, ax = plt.subplots()
            ax.pie(sentiment_counts, labels=sentiment_labels, autopct='%1.1f%%', startangle=90,
                   colors=['#66c2a5', '#fc8d62', '#8da0cb'])
            ax.axis('equal')  
            plt.title("Sentiment Distribution (Normal Analysis)")

            st.pyplot(fig)

       # Create Word Cloud
        try:
            with open("comments.txt", "r", encoding="utf-8") as f:
                comments_text = f.read()  

            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(comments_text)

            # Display Word Cloud
            st.write("### Word Cloud of Comments")
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)

            # Count most common words
            words = re.findall(r'\w+', comments_text.lower())  
            most_common_words = Counter(words).most_common(10) 
            common_words_df = pd.DataFrame(most_common_words, columns=['Word', 'Frequency'])

            # Plot most common words
            st.write("### Most Common Words")
            fig, ax = plt.subplots()
            ax.barh(common_words_df['Word'], common_words_df['Frequency'], color='skyblue')
            plt.xlabel('Frequency')
            plt.title('Most Common Words in Comments')
            st.pyplot(fig)

           # Calculate lengths of individual comments
            comment_lines = comments_text.splitlines()
            comment_lengths = [len(comment) for comment in comment_lines if comment.strip()]  

            # Histogram of comment lengths
            plt.figure(figsize=(10, 5))
            plt.hist(comment_lengths, bins=20, color='blue', alpha=0.7)
            plt.title('Distribution of Comment Lengths')
            plt.xlabel('Comment Length (Characters)')
            plt.ylabel('Number of Comments')
            st.pyplot(plt)

            
        except FileNotFoundError:
            st.error("Comments file not found. Please ensure comments.txt exists.")
        except Exception as e:
            st.error(f"An error occurred while reading comments: {str(e)}")

    

    else:
        st.error("Please enter a valid YouTube URL.")
