import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from evaluate import load
from sentence_transformers import SentenceTransformer, util

## To install the required packages, run the following command:
## pip install evaluate bert-score nltk mauve mauve-text faiss-cpu rouge_score absl sentence-transformers

# Settings
input_file = "../outputs/k-shot_test.json"
output_file = "../outputs/metrics/k-shot-eval-results.csv"
metrics = {
    "bertscore": True,
    "rouge": True, # not good for short text
    "bleu": True, # same-ish as above, google bleu might be better
    "google_bleu": True,
    "mauve": False, # suuuuuper slow
    "sbert_cosine": True,
}

# Evaluation metrics
conditional_load = lambda metric: load(metric) if metrics[metric] else None
bertscore = conditional_load("bertscore")
bertscore_model = "microsoft/deberta-xlarge-mnli"  # best according to https://github.com/Tiiiger/bert_score
rouge = conditional_load("rouge")
bleu = conditional_load("bleu")
google_bleu = conditional_load("google_bleu")
mauve = conditional_load("mauve")
sbert_model = (
    SentenceTransformer("all-MiniLM-L6-v2") if metrics["sbert_cosine"] else None
)


# Load outputs JSON file
print(f"Loading {input_file}..")
with open(input_file, "r") as f:
    data = json.load(f)


def filter_groundtruth(obj):
    ground_truth = obj[desc_type]["ground-truth"]
    predictions = [v for k, v in obj[desc_type].items() if k != "ground-truth"]
    return ground_truth, predictions


# TODO: This is only valid for the case with 1 prediction and multiple ground truth
def evaluate_description(ground_truth, prediction):
    results = {}

    # BERTScore
    if metrics["bertscore"]:
        bert_results = bertscore.compute(
            predictions=[prediction[0] for _ in ground_truth],
            references=ground_truth,
            lang="en",
            model_type=bertscore_model,
        )
        results["bertscore"] = bert_results["f1"][0]

    # ROUGE
    if metrics["rouge"]:
        rouge_results = rouge.compute(
            predictions=[prediction[0] for _ in ground_truth], 
            references=ground_truth
        )
        results["rouge1"] = rouge_results["rouge1"]
        results['rouge2'] = rouge_results['rouge2']
        results['rougeL'] = rouge_results['rougeL']

    # BLEU
    if metrics["bleu"]:
        bleu_results = bleu.compute(
            predictions=prediction, references=[ground_truth]
        )
        results["bleu"] = bleu_results["bleu"]

    # Google BLEU
    if metrics["google_bleu"]:
        google_bleu_results = google_bleu.compute(
            predictions=prediction, references=[ground_truth]
        )
        results["google_bleu"] = google_bleu_results["google_bleu"]

    # MAUVE
    if metrics["mauve"]:
        mauve_results = mauve.compute(
            predictions=[prediction[0] for _ in ground_truth], 
            references=ground_truth, 
            verbose=False, 
            device_id=0
        )
        results["mauve"] = mauve_results.mauve

    # SBERT
    if metrics["sbert_cosine"]:
        ground_truth_embedding = sbert_model.encode(
            ground_truth, 
            convert_to_tensor=True
        )
        prediction_embeddings = sbert_model.encode(
            [prediction[0] for _ in ground_truth], 
            convert_to_tensor=True
        )
        cosine_scores = util.pytorch_cos_sim(
            ground_truth_embedding, prediction_embeddings
        )
        results["sbert_cosine"] = cosine_scores.mean().item()

    return results


# Process data file into record-style list
eval_results = []
for sample in (pbar := tqdm(data, desc="Processing samples")):
    for desc_type in ["visual_descriptions", "functional_descriptions"]:
        ground_truth = sample[desc_type]["ground-truth"]
        for model_treatment, prediction in sample[desc_type].items():
            if model_treatment != "ground-truth":
                model, trial = model_treatment.split("_")[:2]
                input_type = "image-and-context" if trial in ["k-1", "k-3", 'k-5'] else trial
                k_shot = "k-0" if trial in ["image-and-context", "image-only", "context-only"] else trial
                results = {
                    "sample_id": sample["id"], 
                    "description_type": desc_type.split("_")[0], 
                    "model": model,
                    "k-shot": k_shot,
                    "input": input_type,
                    "manual": sample["manual"]
                }
                results |= evaluate_description(ground_truth, prediction)
                eval_results.append(results)

# Create DataFrame and save to csv
df = pd.DataFrame(eval_results)
df.to_csv(output_file, index=False)

# Small stats
print("\nSummary Statistics:")
stats = df.groupby(["description_type", "model", "k-shot", "input"]).mean(numeric_only=True)
print(stats)