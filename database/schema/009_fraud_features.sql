-- ============================================================
-- Data & Security Copilot
-- 009_fraud_features.sql
--
-- Purpose:
-- Create a feature view for the fraud detection engine.
--
-- This does NOT modify the original transaction data.
-- It creates derived features that the ML layer can consume.
-- ============================================================

DROP VIEW IF EXISTS fraud_transaction_features;

CREATE VIEW fraud_transaction_features AS

WITH transaction_base AS (

    SELECT
        t.transaction_id,
        t.sender_account_id,
        t.receiver_account_id,
        t.amount,
        t.currency_code,
        t.country_code,
        t.device_id,
        t.transaction_timestamp,
        t.status,
        t.description,

        a.customer_id AS sender_customer_id,

        EXTRACT(
            HOUR FROM t.transaction_timestamp
        )::INTEGER AS transaction_hour,

        EXTRACT(
            DOW FROM t.transaction_timestamp
        )::INTEGER AS transaction_day_of_week

    FROM transactions t

    JOIN accounts a
        ON a.account_id = t.sender_account_id
),

transaction_history AS (

    SELECT
        current_tx.transaction_id,

        COUNT(previous_tx.transaction_id)
            AS transactions_last_24h,

        COALESCE(
            SUM(previous_tx.amount),
            0
        ) AS amount_last_24h

    FROM transactions current_tx

    LEFT JOIN transactions previous_tx

        ON previous_tx.sender_account_id =
           current_tx.sender_account_id

        AND previous_tx.transaction_timestamp
            < current_tx.transaction_timestamp

        AND previous_tx.transaction_timestamp
            >= current_tx.transaction_timestamp
               - INTERVAL '24 hours'

    GROUP BY
        current_tx.transaction_id
),

customer_history AS (

    SELECT
        tb.transaction_id,

        COUNT(DISTINCT previous.device_id)
            AS distinct_devices_last_30d

    FROM transaction_base tb

    LEFT JOIN transactions previous

        ON previous.sender_account_id =
           tb.sender_account_id

        AND previous.transaction_timestamp
            < tb.transaction_timestamp

        AND previous.transaction_timestamp
            >= tb.transaction_timestamp
               - INTERVAL '30 days'

    GROUP BY
        tb.transaction_id
)

SELECT

    tb.transaction_id,

    tb.sender_account_id,

    tb.receiver_account_id,

    tb.sender_customer_id,

    tb.amount,

    tb.currency_code,

    tb.country_code,

    tb.device_id,

    tb.transaction_timestamp,

    tb.status,

    -- ========================================================
    -- Time Features
    -- ========================================================

    tb.transaction_hour,

    tb.transaction_day_of_week,

    CASE
        WHEN tb.transaction_hour < 6
            THEN 1
        WHEN tb.transaction_hour >= 23
            THEN 1
        ELSE 0
    END AS is_night,

    -- ========================================================
    -- Transaction Amount Features
    -- ========================================================

    CASE
        WHEN tb.amount >= 5000
            THEN 1
        ELSE 0
    END AS is_large_transaction,

    CASE
        WHEN tb.amount >= 10000
            THEN 1
        ELSE 0
    END AS is_very_large_transaction,

    -- ========================================================
    -- Transaction Velocity
    -- ========================================================

    COALESCE(
        th.transactions_last_24h,
        0
    ) AS transactions_last_24h,

    COALESCE(
        th.amount_last_24h,
        0
    ) AS amount_last_24h,

    -- ========================================================
    -- Device Behaviour
    -- ========================================================

    COALESCE(
        ch.distinct_devices_last_30d,
        0
    ) AS distinct_devices_last_30d,

    CASE
        WHEN tb.device_id IS NULL
            THEN 1
        ELSE 0
    END AS missing_device,

    -- ========================================================
    -- Temporary Synthetic Ground Truth
    --
    -- Our generated dataset marks known synthetic fraud
    -- using the transaction description.
    --
    -- This is ONLY for model development/testing.
    -- ========================================================

    CASE
        WHEN tb.description LIKE 'SYNTHETIC_FRAUD%'
            THEN 1
        ELSE 0
    END AS known_fraud_label

FROM transaction_base tb

LEFT JOIN transaction_history th
    ON th.transaction_id =
       tb.transaction_id

LEFT JOIN customer_history ch
    ON ch.transaction_id =
       tb.transaction_id;