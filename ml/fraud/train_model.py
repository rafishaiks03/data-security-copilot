"""
Data & Security Copilot
Fraud Detection - Baseline ML Training

This script trains the first fraud detection model for the
Data & Security Copilot project.

Pipeline:

    PostgreSQL
        |
        v
    fraud_transaction_features
        |
        v
    pandas DataFrame
        |
        v
    train/test split
        |
        v
    Logistic Regression
        |
        v
    Model evaluation
        |
        v
    Saved .joblib model

This is our baseline model.

We will later compare this model against stronger approaches
such as Random Forest, Isolation Forest, and XGBoost.
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
import psycopg
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

MODEL_DIRECTORY = PROJECT_ROOT / "ml" / "fraud" / "models"

MODEL_FILE = MODEL_DIRECTORY / "fraud_baseline.joblib"


# ============================================================
# Environment
# ============================================================

load_dotenv(ENV_FILE)


# ============================================================
# PostgreSQL Configuration
# ============================================================

DATABASE_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost",
)

DATABASE_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432",
    )
)

DATABASE_NAME = os.getenv(
    "POSTGRES_DB",
    "banking",
)

DATABASE_USER = os.getenv(
    "POSTGRES_USER",
    "postgres",
)

DATABASE_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
)


# ============================================================
# ML Configuration
# ============================================================

FEATURE_COLUMNS = [
    "amount",
    "transaction_hour",
    "transaction_day_of_week",
    "is_night",
    "is_large_transaction",
    "is_very_large_transaction",
    "transactions_last_24h",
    "amount_last_24h",
    "distinct_devices_last_30d",
    "missing_device",
]

TARGET_COLUMN = "known_fraud_label"


# ============================================================
# Database Connection
# ============================================================


def get_database_connection() -> psycopg.Connection:
    """
    Create a connection to PostgreSQL.
    """

    if not DATABASE_PASSWORD:
        raise RuntimeError("POSTGRES_PASSWORD is not configured " f"in {ENV_FILE}")

    print("Connecting to PostgreSQL...")

    return psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )


# ============================================================
# Load Dataset
# ============================================================


def load_training_data() -> pd.DataFrame:
    """
    Load the fraud feature dataset from PostgreSQL.
    """

    query = """
        SELECT
            amount,
            transaction_hour,
            transaction_day_of_week,
            is_night,
            is_large_transaction,
            is_very_large_transaction,
            transactions_last_24h,
            amount_last_24h,
            distinct_devices_last_30d,
            missing_device,
            known_fraud_label
        FROM fraud_transaction_features
        ORDER BY transaction_timestamp;
    """

    with get_database_connection() as connection:

        dataframe = pd.read_sql_query(
            query,
            connection,
        )

    return dataframe


# ============================================================
# Validate Dataset
# ============================================================


def validate_dataset(
    dataframe: pd.DataFrame,
) -> None:
    """
    Validate that the dataset is suitable for training.
    """

    if dataframe.empty:
        raise RuntimeError("The fraud_transaction_features view " "returned no rows.")

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        column for column in required_columns if column not in dataframe.columns
    ]

    if missing_columns:
        raise RuntimeError(
            "The following required columns are missing: " + ", ".join(missing_columns)
        )

    missing_values = dataframe[required_columns].isnull().sum()

    columns_with_missing_values = missing_values[missing_values > 0]

    if not columns_with_missing_values.empty:

        print("\nWARNING: Missing values detected:")

        print(columns_with_missing_values)

    class_counts = dataframe[TARGET_COLUMN].value_counts()

    if len(class_counts) < 2:
        raise RuntimeError(
            "The dataset must contain both " "normal and fraudulent transactions."
        )

    print()

    print("Dataset validation successful.")

    print(f"Total rows : {len(dataframe):,}")

    print(f"Normal     : " f"{class_counts.get(0, 0):,}")

    print(f"Fraud      : " f"{class_counts.get(1, 0):,}")

    fraud_percentage = class_counts.get(1, 0) / len(dataframe) * 100

    print(f"Fraud rate : " f"{fraud_percentage:.2f}%")


# ============================================================
# Build Model
# ============================================================


def build_model() -> Pipeline:
    """
    Build the baseline Logistic Regression pipeline.

    StandardScaler:
        Puts numerical features on comparable scales.

    LogisticRegression:
        Produces a probability that a transaction is fraudulent.

    class_weight="balanced":
        Gives additional importance to the minority fraud class.
    """

    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


# ============================================================
# Train / Test Split
# ============================================================


def split_dataset(
    dataframe: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
]:
    """
    Separate features and labels and create a train/test split.
    """

    X = dataframe[FEATURE_COLUMNS].copy()

    y = dataframe[TARGET_COLUMN].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    print()

    print("Train/test split:")

    print(f"Training rows: " f"{len(X_train):,}")

    print(f"Testing rows : " f"{len(X_test):,}")

    return (
        X_train,
        X_test,
        y_train,
        y_test,
    )


# ============================================================
# Training
# ============================================================


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> Pipeline:
    """
    Train the baseline model.
    """

    model = build_model()

    print()

    print("Training Logistic Regression...")

    model.fit(
        X_train,
        y_train,
    )

    print("Training complete.")

    return model


# ============================================================
# Evaluation
# ============================================================


def evaluate_model(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> None:
    """
    Evaluate the model using several classification metrics.
    """

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    print()

    print("=" * 60)

    print("MODEL EVALUATION")

    print("=" * 60)

    print()

    print("Confusion Matrix:")

    print(matrix)

    print()

    print("Classification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Normal",
                "Fraud",
            ],
            zero_division=0,
        )
    )

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    print(f"ROC-AUC: {auc:.4f}")

    print()

    print("Interpretation:")

    print(
        "  Precision = Of transactions "
        "flagged as fraud, how many were actually fraud?"
    )

    print("  Recall    = Of all actual fraud, " "how much did the model catch?")

    print("  F1        = Balance between precision " "and recall.")

    print("  ROC-AUC   = Overall ranking quality " "of fraud probabilities.")

    print()


# ============================================================
# Save Model
# ============================================================


def save_model(
    model: Pipeline,
) -> None:
    """
    Save the trained model and metadata.
    """

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_package = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
    }

    joblib.dump(
        model_package,
        MODEL_FILE,
    )

    print("Model saved:")

    print(MODEL_FILE)


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Execute the complete training pipeline.
    """

    print()

    print("=" * 60)

    print("Data & Security Copilot")

    print("Fraud Detection ML Training")

    print("Baseline: Logistic Regression")

    print("=" * 60)

    print()

    dataframe = load_training_data()

    validate_dataset(dataframe)

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = split_dataset(dataframe)

    model = train_model(
        X_train,
        y_train,
    )

    evaluate_model(
        model,
        X_test,
        y_test,
    )

    save_model(model)

    print()

    print("=" * 60)

    print("Fraud model training completed successfully.")

    print("=" * 60)

    print()


if __name__ == "__main__":
    main()
