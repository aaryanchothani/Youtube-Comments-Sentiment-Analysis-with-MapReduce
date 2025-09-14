# YouTube Comments Sentiment Analysis with MapReduce

## 📖 Project Overview
This project applies sentiment analysis to YouTube comments using a MapReduce-style pipeline in Python and having its frontend with Streamlit. The aim is to efficiently process large sets of comments and categorize them (positive, negative, neutral), helping understand audience sentiment in bulk.

---

## 🔧 What the Code Does
- Reads comments from `comments.txt`.  
- Processes them through several scripts (`1.py`, `2.py`, `stream.py`) that simulate stages of MapReduce (mapping, shuffling/aggregation, etc.).  
- The main script `youtube_sentiment.py` ties everything together.  
- Outputs the sentiment distribution (counts or summary) after analyzing all comments.

---

## 📂 Project Structure

```text
.gitignore                  # Specifies files/folders to ignore (e.g. __pycache__)
1.py                       # First stage script in pipeline (Map)
2.py                       # Second stage (Reduce)
comments.txt               
stream.py                  # For streaming / continual processing
tree.txt                   # intermediate or output structure
youtube.png                # Visualization or preview image
youtube_sentiment.py       # Main driver script
__pycache__/               

```
---
