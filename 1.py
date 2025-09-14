# mapper.py
import sys
from nltk.sentiment import SentimentIntensityAnalyzer

def main():
    sia = SentimentIntensityAnalyzer()

    for line in sys.stdin:
        line = line.strip()
        if line:  
            score = sia.polarity_scores(line)['compound']
            
            if score > 0.05:
                sentiment = 'positive'
            elif score < -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            print(f"{sentiment}\t1")

if __name__ == "__main__":
    main()
