-- ============================================================
-- Data & Security Copilot
-- Customers
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(30),

    date_of_birth DATE,

    country_code CHAR(2) NOT NULL,

    kyc_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    risk_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT customers_country_fk
        FOREIGN KEY (country_code)
        REFERENCES countries (country_code),

    CONSTRAINT customers_kyc_status_check
        CHECK (
            kyc_status IN (
                'PENDING',
                'VERIFIED',
                'REJECTED'
            )
        ),

    CONSTRAINT customers_risk_score_check
        CHECK (
            risk_score BETWEEN 0 AND 100
        )
);


-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_customers_country_code
    ON customers (country_code);

CREATE INDEX IF NOT EXISTS idx_customers_kyc_status
    ON customers (kyc_status);

CREATE INDEX IF NOT EXISTS idx_customers_risk_score
    ON customers (risk_score);

CREATE INDEX IF NOT EXISTS idx_customers_created_at
    ON customers (created_at);