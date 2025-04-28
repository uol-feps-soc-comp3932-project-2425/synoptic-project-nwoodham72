import json
from summarizer import Summarizer
from evaluate import load

# Load model and ROUGE metric
summariser = Summarizer(model="distilbert-base-uncased")
rouge = load("rouge")

# Load test data
with open("description_summaries.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

# Run evaluation
scores = []
for idx, item in enumerate(test_data):
    generated = summariser(item["description"], ratio=0.3)
    result = rouge.compute(predictions=[generated], references=[item["reference"]])
    print(f"\nTicket #{idx+1} ROUGE scores: {result}")
    scores.append(result)

# Calculate average ROUGE scores
avg_scores = {
    metric: sum(score[metric] for score in scores) / len(scores)
    for metric in scores[0]
}
print("\nAverage ROUGE scores across all 10 tickets:")
print(avg_scores)
