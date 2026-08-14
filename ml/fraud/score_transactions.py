"""
Data & Security Copilot
Fraud Transaction Scoring

Loads the trained fraud detection artifact and scores transactions
from PostgreSQL.

The training pipeline stores more than just the model inside the
.joblib file, so this script extracts the actual model artifact
before running inference.

Pipeline:

    PostgreSQL
        |
        v
    fraud_transaction_features
        |
        v
    trained model artifact
        |
        v
    fraud probability
        |
        v
    LOW / MEDIUM / HIGH risk
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
import psycopg
from dotenv import load_dotenv

# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

MODEL_FILE = PROJECT_ROOT / "ml" / "fraud" / "models" / "fraud_baseline.joblib"


# ============================================================
# Environment configuration
# ============================================================

load_dotenv(ENV_FILE)


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
# ML features
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


# ============================================================
# Risk thresholds
# ============================================================

LOW_RISK_THRESHOLD = 0.30

HIGH_RISK_THRESHOLD = 0.70


# ============================================================
# Database connection
# ============================================================


def get_database_connection():
    """
    Create a PostgreSQL connection.
    """

    if not DATABASE_PASSWORD:
        raise RuntimeError(
            "POSTGRES_PASSWORD is not configured. " f"Expected it in: {ENV_FILE}"
        )

    return psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )


# ============================================================
# Model loading
# ============================================================


def load_model():
    """
    Load the trained fraud detection artifact.

    The training script may save the model inside a dictionary,
    for example:

        {
            "model": trained_model,
            "feature_columns": [...],
            "metrics": {...}
        }

    This function handles that structure and also supports a
    plain scikit-learn model for future compatibility.
    """

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Fraud model was not found:\n"
            f"{MODEL_FILE}\n\n"
            "Run this first:\n"
            "python ml/fraud/train_model.py"
        )

    print("Loading fraud model:")

    print(MODEL_FILE)

    artifact = joblib.load(MODEL_FILE)

    # --------------------------------------------------------
    # Case 1:
    # Training script saved a dictionary containing the model.
    # --------------------------------------------------------

    if isinstance(
        artifact,
        dict,
    ):

        print("Model artifact type: dictionary")

        print("Artifact keys:")

        for key in artifact.keys():

            print(f"  - {key}")

        if "model" not in artifact:

            raise RuntimeError(
                "The fraud model artifact is a dictionary, "
                "but it does not contain a 'model' key.\n\n"
                f"Available keys: "
                f"{list(artifact.keys())}"
            )

        model = artifact["model"]

    # --------------------------------------------------------
    # Case 2:
    # The file itself is the trained model.
    # --------------------------------------------------------

    else:

        print("Model artifact type: direct model")

        model = artifact

    # --------------------------------------------------------
    # Validate the loaded model.
    # --------------------------------------------------------

    if not hasattr(
        model,
        "predict_proba",
    ):

        raise RuntimeError(
            "The loaded fraud model does not provide "
            "'predict_proba'.\n\n"
            f"Loaded object type: "
            f"{type(model).__name__}"
        )

    print(f"Loaded model type: " f"{type(model).__name__}")

    return model


# ============================================================
# Load transactions
# ============================================================


def load_transactions(
    connection,
    limit: int,
) -> pd.DataFrame:
    """
    Load transactions and ML features from PostgreSQL.
    """

    query = """
        SELECT
            transaction_id,
            sender_account_id,
            receiver_account_id,
            amount,
            currency_code,
            country_code,
            device_id,
            transaction_timestamp,
            status,

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

        ORDER BY transaction_timestamp DESC

        LIMIT %s
    """

    dataframe = pd.read_sql_query(
        query,
        connection,
        params=(limit,),
    )

    return dataframe


# ============================================================
# Feature validation
# ============================================================


def validate_features(
    dataframe: pd.DataFrame,
) -> None:
    """
    Make sure the database provides every feature expected
    by the trained model.
    """

    missing_columns = [
        column for column in FEATURE_COLUMNS if column not in dataframe.columns
    ]

    if missing_columns:

        raise RuntimeError(
            "The following ML features are missing "
            "from fraud_transaction_features:\n"
            + "\n".join(f"  - {column}" for column in missing_columns)
        )

    if dataframe.empty:

        raise RuntimeError(
            "No transactions were returned from " "fraud_transaction_features."
        )


# ============================================================
# Risk classification
# ============================================================


def classify_risk(
    probability: float,
) -> str:
    """
    Convert fraud probability into a human-readable risk level.

    LOW:
        probability < 0.30

    MEDIUM:
        0.30 <= probability < 0.70

    HIGH:
        probability >= 0.70
    """

    if probability >= HIGH_RISK_THRESHOLD:

        return "HIGH"

    if probability >= LOW_RISK_THRESHOLD:

        return "MEDIUM"

    return "LOW"


# ============================================================
# Score transactions
# ============================================================


def score_transactions(
    model,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run model inference against transaction features.
    """

    validate_features(dataframe)

    features = dataframe[FEATURE_COLUMNS].copy()

    probabilities = model.predict_proba(features)[:, 1]

    predictions = (probabilities >= 0.50).astype(int)

    dataframe = dataframe.copy()

    dataframe["fraud_probability"] = probabilities

    dataframe["fraud_prediction"] = predictions

    dataframe["risk_level"] = [
        classify_risk(probability) for probability in probabilities
    ]

    return dataframe


# ============================================================
# Print summary
# ============================================================


def print_summary(
    dataframe: pd.DataFrame,
) -> None:
    """
    Print a concise scoring summary.
    """

    print()

    print("=" * 70)

    print("Fraud Scoring Summary")

    print("=" * 70)

    print(f"Transactions scored : " f"{len(dataframe)}")

    print()

    risk_counts = (
        dataframe["risk_level"]
        .value_counts()
        .reindex(
            [
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
            fill_value=0,
        )
    )

    print("Risk distribution:")

    print(f"  HIGH   : " f"{risk_counts['HIGH']}")

    print(f"  MEDIUM : " f"{risk_counts['MEDIUM']}")

    print(f"  LOW    : " f"{risk_counts['LOW']}")

    print()

    predicted_fraud_count = int(dataframe["fraud_prediction"].sum())

    actual_fraud_count = int(dataframe["known_fraud_label"].sum())

    print(f"Model predicted fraud : " f"{predicted_fraud_count}")

    print(f"Known fraud labels    : " f"{actual_fraud_count}")

    print()


# ============================================================
# Print highest-risk transactions
# ============================================================


def print_top_risk_transactions(
    dataframe: pd.DataFrame,
    count: int = 10,
) -> None:
    """
    Print the highest-risk transactions.
    """

    highest_risk = dataframe.sort_values(
        "fraud_probability",
        ascending=False,
    ).head(count)

    print("=" * 70)

    print(f"Top {count} Highest-Risk Transactions")

    print("=" * 70)

    display_columns = [
        "transaction_id",
        "amount",
        "currency_code",
        "country_code",
        "transaction_timestamp",
        "transactions_last_24h",
        "amount_last_24h",
        "distinct_devices_last_30d",
        "fraud_probability",
        "fraud_prediction",
        "risk_level",
        "known_fraud_label",
    ]

    display_dataframe = highest_risk[display_columns].copy()

    display_dataframe["fraud_probability"] = display_dataframe["fraud_probability"].map(
        lambda value: f"{value:.4f}"
    )

    print(display_dataframe.to_string(index=False))

    print()


# ============================================================
# Main
# ============================================================


def main() -> None:
    """
    Application entry point.
    """

    limit = 100

    print()

    print("=" * 70)

    print("Data & Security Copilot")

    print("Fraud Transaction Scoring")

    print("=" * 70)

    print()

    print(f"Database : " f"{DATABASE_HOST}:{DATABASE_PORT}/" f"{DATABASE_NAME}")

    print(f"Scoring latest " f"{limit} transactions.")

    print()

    model = load_model()

    print()

    print("Connecting to PostgreSQL...")

    with get_database_connection() as connection:

        dataframe = load_transactions(
            connection,
            limit,
        )

    print(f"Loaded " f"{len(dataframe)} transactions.")

    print()

    scored_dataframe = score_transactions(
        model,
        dataframe,
    )

    print_summary(scored_dataframe)

    print_top_risk_transactions(
        scored_dataframe,
        count=10,
    )


if __name__ == "__main__":
    main()
