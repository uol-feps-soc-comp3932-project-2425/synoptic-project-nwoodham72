import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import pandas as pd
import ast
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report, f1_score, hamming_loss, accuracy_score
from bert.assigner import tag_bug
import matplotlib.pyplot as plt
import seaborn as sns

# Load test data
file_path = "C:\\Users\\User\\Desktop\\YEAR 4\\COMP3932 - Synoptic Project\\Datasets\\To Use\\customer-it-support\\classifications_clean_tagged.csv"
df = pd.read_csv(file_path)
df["tags"] = df["tags"].apply(ast.literal_eval)

# True tags
true_tags = df["tags"].tolist()

# Fill missing values with empty strings
df["subject"] = df["subject"].fillna("")
df["body"] = df["body"].fillna("")

# Format input like production (title + description)
predicted_tags = df.apply(
    lambda row: tag_bug(f"{row['subject'].strip()}.\n{row['body'].strip()}", threshold=0.6),
    axis=1
).tolist()


# Fit a MultiLabelBinarizer on all tags
mlb = MultiLabelBinarizer()
y_true = mlb.fit_transform(true_tags)
y_pred = mlb.transform(predicted_tags)  # uses same classes

# Core metrics
micro_f1 = f1_score(y_true, y_pred, average='micro')
macro_f1 = f1_score(y_true, y_pred, average='macro')
hamming = hamming_loss(y_true, y_pred)
subset_acc = accuracy_score(y_true, y_pred)

print(f"Micro F1-score:  {micro_f1:.4f}")
print(f"Macro F1-score:  {macro_f1:.4f}")
print(f"Hamming Loss:    {hamming:.4f}")
print(f"Subset Accuracy: {subset_acc:.4f}")

# Detailed report
print("\nPer-label classification report:")
report = classification_report(y_true, y_pred, target_names=mlb.classes_)
print(report)

# Optional: Plot top 15 F1-scores per tag
report_dict = classification_report(y_true, y_pred, target_names=mlb.classes_, output_dict=True)
f1_scores = {label: scores["f1-score"] for label, scores in report_dict.items() if label in mlb.classes_}
top_f1 = sorted(f1_scores.items(), key=lambda x: x[1], reverse=True)[:15]

labels, scores = zip(*top_f1)
plt.figure(figsize=(10, 6))
sns.barplot(x=scores, y=labels, palette="viridis")
plt.title("Top 15 Tags by F1 Score")
plt.xlabel("F1 Score")
plt.ylabel("Tag")
plt.tight_layout()
plt.show()
