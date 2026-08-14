"""
Data & Security Copilot
Fraud Alert Persistence

Scores recent transactions using the trained fraud model and
persists MEDIUM and HIGH risk transactions into PostgreSQL.

Pipeline:

    PostgreSQL
        |
        v
    fraud_transaction_features
        |
        v
    trained fraud model
        |
        v
    fraud probability
        |
        v
    risk classification
        |
        +------------------+
        |                  |
       LOW            MEDIUM / HIGH
        |                  |
        |                  v
        |            fraud_alerts
        |                  |
        +------------------+

LOW-risk transactions are intentionally not persisted as alerts.

The script is idempotent:
running it multiple times will not create duplicate alerts
for the same transaction.
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

ALERT_THRESHOLD = LOW_RISK_THRESHOLD


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
    Load the trained fraud model artifact.

    The .joblib file contains a dictionary with the trained
    Pipeline under the 'model' key.
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
                "The fraud model artifact does not "
                "contain a 'model' key.\n\n"
                f"Available keys: "
                f"{list(artifact.keys())}"
            )

        model = artifact["model"]

    else:

        print("Model artifact type: direct model")

        model = artifact

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
    Load recent transactions and their fraud features.
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
# Validate features
# ============================================================


def validate_features(
    dataframe: pd.DataFrame,
) -> None:
    """
    Verify that all model features are available.
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
    Convert fraud probability into a risk level.
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
    Generate fraud probabilities and risk levels.
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
# Check existing alert
# ============================================================


def alert_exists(
    cursor,
    transaction_id,
) -> bool:
    """
    Check whether an alert already exists for a transaction.

    This prevents duplicate alerts if this script is run
    multiple times.
    """

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM fraud_alerts
            WHERE transaction_id = %s
        )
        """,
        (transaction_id,),
    )

    result = cursor.fetchone()

    return bool(result[0])


# ============================================================
# Determine alert severity
# ============================================================


def determine_severity(
    probability: float,
) -> str:
    """
    Convert model probability into fraud alert severity.

    HIGH probability:
        HIGH

    MEDIUM probability:
        MEDIUM
    """

    if probability >= HIGH_RISK_THRESHOLD:

        return "HIGH"

    return "MEDIUM"


# ============================================================
# Generate alert description
# ============================================================


def generate_alert_description(
    row: pd.Series,
) -> str:
    """
    Generate a concise explanation for why a transaction
    was flagged.

    This is deliberately deterministic for now.

    Later, the Data & Security Copilot can use an LLM to
    generate richer explanations.
    """

    reasons = []

    amount = float(row["amount"])

    if amount >= 10000:

        reasons.append("very large transaction")

    elif amount >= 5000:

        reasons.append("large transaction")

    if int(row["is_night"]) == 1:

        reasons.append("transaction occurred during unusual hours")

    if int(row["transactions_last_24h"]) >= 5:

        reasons.append("high transaction frequency in the previous 24 hours")

    if float(row["amount_last_24h"]) >= 10000:

        reasons.append("high cumulative transaction amount in the previous 24 hours")

    if int(row["distinct_devices_last_30d"]) >= 3:

        reasons.append("multiple devices associated with recent activity")

    if int(row["missing_device"]) == 1:

        reasons.append("transaction has no associated device")

    if not reasons:

        reasons.append(
            "machine-learning model detected suspicious transaction behavior"
        )

    probability = float(row["fraud_probability"])

    reason_text = "; ".join(reasons)

    return (
        f"Fraud probability " f"{probability:.2%}. " f"Indicators: " f"{reason_text}."
    )


# ============================================================
# Persist alerts
# ============================================================


def persist_alerts(
    connection,
    dataframe: pd.DataFrame,
) -> tuple[int, int]:
    """
    Insert MEDIUM and HIGH risk transactions into fraud_alerts.

    Returns:

        (inserted_count, skipped_existing_count)
    """

    candidates = dataframe[dataframe["fraud_probability"] >= ALERT_THRESHOLD].copy()

    inserted_count = 0
    skipped_existing_count = 0

    with connection.cursor() as cursor:

        for _, row in candidates.iterrows():

            transaction_id = row["transaction_id"]

            if alert_exists(
                cursor,
                transaction_id,
            ):
                skipped_existing_count += 1
                continue

            probability = float(row["fraud_probability"])

            risk_level = classify_risk(probability)

            description = generate_alert_description(row)

            # Get the customer associated with the
            # sender account.
            cursor.execute(
                """
                SELECT customer_id
                FROM accounts
                WHERE account_id = %s
                """,
                (row["sender_account_id"],),
            )

            customer_result = cursor.fetchone()

            customer_id = customer_result[0] if customer_result else None

            # Store the important ML features as JSONB.
            features = {
                "amount": float(row["amount"]),
                "transaction_hour": int(row["transaction_hour"]),
                "transaction_day_of_week": int(row["transaction_day_of_week"]),
                "is_night": int(row["is_night"]),
                "is_large_transaction": int(row["is_large_transaction"]),
                "is_very_large_transaction": int(row["is_very_large_transaction"]),
                "transactions_last_24h": int(row["transactions_last_24h"]),
                "amount_last_24h": float(row["amount_last_24h"]),
                "distinct_devices_last_30d": int(row["distinct_devices_last_30d"]),
                "missing_device": int(row["missing_device"]),
            }

            import json

            cursor.execute(
                """
                INSERT INTO fraud_alerts (
                    transaction_id,
                    customer_id,
                    alert_type,
                    risk_score,
                    risk_level,
                    model_name,
                    model_version,
                    reason,
                    features,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s::jsonb,
                    %s
                )
                """,
                (
                    transaction_id,
                    customer_id,
                    "FRAUD",
                    probability,
                    risk_level,
                    "fraud_baseline",
                    "1.0",
                    description,
                    json.dumps(features),
                    "OPEN",
                ),
            )

            inserted_count += 1

    connection.commit()

    return (
        inserted_count,
        skipped_existing_count,
    )


# ============================================================
# Print summary
# ============================================================


def print_summary(
    dataframe: pd.DataFrame,
    inserted_count: int,
    skipped_existing_count: int,
) -> None:
    """
    Print persistence results.
    """

    candidates = dataframe[dataframe["fraud_probability"] >= ALERT_THRESHOLD]

    print()

    print("=" * 70)

    print("Fraud Alert Persistence Summary")

    print("=" * 70)

    print(f"Transactions scored : " f"{len(dataframe)}")

    print(f"Alert candidates    : " f"{len(candidates)}")

    print(f"Alerts inserted     : " f"{inserted_count}")

    print(f"Already existed     : " f"{skipped_existing_count}")

    print()

    risk_counts = (
        candidates["risk_level"]
        .value_counts()
        .reindex(
            [
                "HIGH",
                "MEDIUM",
            ],
            fill_value=0,
        )
    )

    print("New/candidate alert distribution:")

    print(f"  HIGH   : " f"{risk_counts['HIGH']}")

    print(f"  MEDIUM : " f"{risk_counts['MEDIUM']}")

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

    print("Fraud Alert Persistence")

    print("=" * 70)

    print()

    print(f"Database : " f"{DATABASE_HOST}:{DATABASE_PORT}/" f"{DATABASE_NAME}")

    print(f"Processing latest " f"{limit} transactions.")

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

        scored_dataframe = score_transactions(
            model,
            dataframe,
        )

        inserted_count, skipped_existing_count = persist_alerts(
            connection,
            scored_dataframe,
        )

    print_summary(
        scored_dataframe,
        inserted_count,
        skipped_existing_count,
    )

    print("Fraud alert persistence completed.")

    print()


if __name__ == "__main__":
    main()
