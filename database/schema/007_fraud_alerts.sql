-- ============================================================
-- Data & Security Copilot
-- Fraud Alerts
-- ============================================================

CREATE TABLE IF NOT EXISTS fraud_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_id UUID,

    customer_id UUID,

    alert_type VARCHAR(50) NOT NULL DEFAULT 'FRAUD',

    risk_score NUMERIC(6, 5) NOT NULL,

    risk_level VARCHAR(20) NOT NULL,

    model_name VARCHAR(100),

    model_version VARCHAR(50),

    reason TEXT,

    features JSONB,

    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',

    reviewed_by VARCHAR(100),

    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fraud_alerts_transaction_fk
        FOREIGN KEY (transaction_id)
        REFERENCES transactions (transaction_id),

    CONSTRAINT fraud_alerts_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),

    CONSTRAINT fraud_alerts_risk_score_check
        CHECK (
            risk_score >= 0
            AND risk_score <= 1
        ),

    CONSTRAINT fraud_alerts_risk_level_check
        CHECK (
            risk_level IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    CONSTRAINT fraud_alerts_status_check
        CHECK (
            status IN (
                'OPEN',
                'INVESTIGATING',
                'CONFIRMED',
                'FALSE_POSITIVE',
                'RESOLVED'
            )
        ),

    CONSTRAINT fraud_alerts_reviewed_at_check
        CHECK (
            reviewed_at IS NULL
            OR reviewed_at >= created_at
        )
);


-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_transaction_id
    ON fraud_alerts (transaction_id);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_customer_id
    ON fraud_alerts (customer_id);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_risk_level
    ON fraud_alerts (risk_level);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_status
    ON fraud_alerts (status);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_created_at
    ON fraud_alerts (created_at);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_customer_created
    ON fraud_alerts (customer_id, created_at);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_open
    ON fraud_alerts (status, risk_level)
    WHERE status IN (
        'OPEN',
        'INVESTIGATING'
    );


-- ============================================================
-- JSONB Index
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_features
    ON fraud_alerts
    USING GIN (features);