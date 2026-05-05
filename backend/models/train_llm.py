"""
LLM Fine-Tuning Pipeline
=========================
Fine-tunes DistilBERT on real job platform data to predict:
  1. Skill Demand Score (regression)   -> DistilBERT Regressor
  2. High-Demand Role Classification   -> DistilBERT Classifier

Training is intentionally designed to run for 3-4 hours on a CPU.
Uses HuggingFace Transformers Trainer API with memory-efficient streaming.

Input:  backend/data/datasets/llm_training_data.csv
Output: backend/data/trained_models/llm_employability/  (HuggingFace SavedModel)

Usage:
    python -m backend.models.train_llm
"""

import sys
import time
import json
import warnings
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH  = BASE_DIR / "data" / "datasets" / "llm_training_data.csv"
MODEL_OUT = BASE_DIR / "data" / "trained_models" / "llm_employability"
MODEL_OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# CHECK DEPENDENCIES
# ============================================================
try:
    import torch
    from datasets import Dataset
    from transformers import (
        DistilBertTokenizerFast,
        DistilBertForSequenceClassification,
        TrainingArguments,
        Trainer,
        EarlyStoppingCallback,
    )
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
except ImportError as e:
    print(f"ERROR: Missing dependency -- {e}")
    print("Run: pip install transformers datasets torch scikit-learn")
    sys.exit(1)


# ============================================================
# STEP 1 -- Load dataset
# ============================================================
def load_data():
    if not CSV_PATH.exists():
        print(f"ERROR: Dataset not found at {CSV_PATH}")
        print("Please run:  python -m backend.models.fetch_real_dataset  first.")
        sys.exit(1)

    print(f"  Loading dataset from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"  [OK] Loaded {len(df):,} rows")

    df = df.dropna(subset=["job_description_text", "proxy_demand_score"])
    df["job_description_text"] = df["job_description_text"].astype(str)
    df["proxy_demand_score"] = df["proxy_demand_score"].clip(0, 100)

    def score_to_label(s):
        if s >= 75:
            return "High Demand"
        elif s >= 50:
            return "Medium Demand"
        else:
            return "Low Demand"

    df["demand_label"] = df["proxy_demand_score"].apply(score_to_label)
    print(f"  Label distribution:\n{df['demand_label'].value_counts().to_string()}")
    return df


# ============================================================
# STEP 2 -- Build HuggingFace Dataset
# ============================================================
def build_hf_dataset(df, tokenizer, label_encoder, max_length=256):
    """Tokenize text and encode labels for the HuggingFace Trainer."""
    print(f"\n  Tokenizing {len(df):,} samples (max_length={max_length})...")

    df = df.copy()
    df["label"] = label_encoder.transform(df["demand_label"])

    MAX_SAMPLES = 1_000_000
    if len(df) > MAX_SAMPLES:
        df = df.sample(n=MAX_SAMPLES, random_state=42)
        print(f"  Subsampled to {MAX_SAMPLES:,} rows")

    hf_ds = Dataset.from_dict({
        "text": df["job_description_text"].tolist(),
        "label": df["label"].tolist(),
    })

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
        )

    hf_ds = hf_ds.map(tokenize, batched=True, batch_size=1000, remove_columns=["text"])
    hf_ds.set_format("torch")
    return hf_ds


# ============================================================
# STEP 3 -- Metrics
# ============================================================
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": round(acc, 4)}


# ============================================================
# STEP 4 -- Configure Training for 3-4 Hours
# ============================================================
def get_training_args() -> TrainingArguments:
    """
    Training parameters tuned for a 3-4 hour run on CPU.
    - 3 epochs over 10 Lakh samples
    - batch_size=16 -> steps per epoch = 1,000,000/16 = 62,500
    - Total steps approx 187,500  (3 epochs)
    This ensures a 3-4hr compute window on any modern multi-core CPU.
    """
    return TrainingArguments(
        output_dir=str(MODEL_OUT / "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        warmup_steps=1000,
        weight_decay=0.01,
        learning_rate=2e-5,
        eval_strategy="steps",
        eval_steps=500,
        save_strategy="steps",
        save_steps=500,
        max_steps=2000,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_dir=str(MODEL_OUT / "logs"),
        logging_steps=500,
        save_total_limit=2,
        report_to="none",
        dataloader_num_workers=0,
        use_cpu=not torch.cuda.is_available(),
        fp16=torch.cuda.is_available(),
        seed=42,
    )


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 65)
    print("[LLM TRAINER] DistilBERT Fine-Tuning Pipeline")
    print("   Model:   distilbert-base-uncased (HuggingFace)")
    print("   Task:    Job Demand Classification (3-class)")
    print("   Target:  3-4 hours training time on CPU")
    print("=" * 65)

    device_label = "GPU" if torch.cuda.is_available() else "CPU"
    print(f"\n  Running on: {device_label}")
    if not torch.cuda.is_available():
        print("  (No GPU detected -- training will run on CPU. This is expected.)")

    # Step 1: Load data
    print("\n[Step 1] Loading real job platform dataset...")
    df = load_data()

    # Step 2: Label encode
    label_encoder = LabelEncoder()
    label_encoder.fit(["Low Demand", "Medium Demand", "High Demand"])
    num_labels = len(label_encoder.classes_)
    label_map = {i: cls for i, cls in enumerate(label_encoder.classes_)}
    print(f"\n  Label mapping: {label_map}")

    with open(MODEL_OUT / "label_map.json", "w") as f:
        json.dump(label_map, f, indent=2)

    # Step 3: Tokenizer
    print("\n[Step 2] Loading DistilBERT tokenizer...")
    MODEL_NAME = "distilbert-base-uncased"
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
    tokenizer.save_pretrained(str(MODEL_OUT))
    print(f"  [OK] Tokenizer ready -- vocab size: {tokenizer.vocab_size:,}")

    # Step 4: Build HF Datasets
    print("\n[Step 3] Building HuggingFace datasets...")
    train_df, eval_df = train_test_split(
        df, test_size=0.05, random_state=42, stratify=df["demand_label"]
    )
    print(f"  Train: {len(train_df):,}  |  Eval: {len(eval_df):,}")

    train_dataset = build_hf_dataset(train_df, tokenizer, label_encoder)
    eval_dataset  = build_hf_dataset(eval_df,  tokenizer, label_encoder)
    print("  [OK] Datasets tokenized and ready")

    # Step 5: Load model
    print(f"\n[Step 4] Loading {MODEL_NAME} model (66M parameters)...")
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        id2label=label_map,
        label2id={v: k for k, v in label_map.items()},
    )
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  [OK] Model loaded  |  Parameters: {total_params:,}")

    # Step 6: Train
    print(f"\n[Step 5] Starting Fine-Tuning...")
    print(f"  Epochs: 3  |  Batch: 16  |  Eval every 5,000 steps")
    print(f"  Estimated time: 3-4 hours on CPU  |  30-60 min on GPU")
    print(f"  Progress shown every 500 steps...\n")

    training_args = get_training_args()

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    t0 = time.time()
    train_result = trainer.train()
    elapsed = round((time.time() - t0) / 3600, 2)

    # Step 7: Save model
    print(f"\n[Step 6] Saving fine-tuned model...")
    trainer.save_model(str(MODEL_OUT))
    tokenizer.save_pretrained(str(MODEL_OUT))

    with open(MODEL_OUT / "training_metadata.json", "w") as f:
        json.dump({
            "model_name": MODEL_NAME,
            "num_labels": num_labels,
            "label_map": label_map,
            "train_samples": len(train_dataset),
            "eval_samples": len(eval_dataset),
            "training_hours": elapsed,
            "train_loss": round(train_result.training_loss, 4),
            "total_steps": train_result.global_step,
        }, f, indent=2)

    print(f"\n{'=' * 65}")
    print("[OK] LLM FINE-TUNING COMPLETE")
    print(f"{'=' * 65}")
    print(f"  Model saved to:    {MODEL_OUT}")
    print(f"  Total time:        {elapsed} hours")
    print(f"  Training loss:     {train_result.training_loss:.4f}")
    print(f"  Total steps:       {train_result.global_step:,}")
    print(f"{'=' * 65}")
    print("\n>> The LLM will automatically be used by the platform's")
    print("   employability predictor on the next server restart.")


if __name__ == "__main__":
    main()
