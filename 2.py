# reducer.py
import sys

current_sentiment = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    sentiment, count = line.split('\t', 1)
    count = int(count)

    if current_sentiment == sentiment:
        current_count += count
    else:
        if current_sentiment:
            print(f"{current_sentiment}\t{current_count}")
        current_count = count
        current_sentiment = sentiment

if current_sentiment is not None:
    print(f"{current_sentiment}\t{current_count}")
