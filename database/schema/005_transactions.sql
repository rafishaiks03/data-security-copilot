-- ============================================================
-- Data & Security Copilot
-- Transactions
-- ============================================================

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    sender_account_id UUID,

    receiver_account_id UUID,

    transaction_type_code VARCHAR(30) NOT NULL,

    amount NUMERIC(19, 4) NOT NULL,

    currency_code CHAR(3) NOT NULL,

    transaction_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    device_id UUID,

    ip_address INET,

    country_code CHAR(2),

    status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',

    description VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT transactions_sender_account_fk
        FOREIGN KEY (sender_account_id)
        REFERENCES accounts (account_id),

    CONSTRAINT transactions_receiver_account_fk
        FOREIGN KEY (receiver_account_id)
        REFERENCES accounts (account_id),

    CONSTRAINT transactions_type_fk
        FOREIGN KEY (transaction_type_code)
        REFERENCES transaction_types (transaction_type_code),

    CONSTRAINT transactions_currency_fk
        FOREIGN KEY (currency_code)
        REFERENCES currencies (currency_code),

    CONSTRAINT transactions_country_fk
        FOREIGN KEY (country_code)
        REFERENCES countries (country_code),

    CONSTRAINT transactions_amount_check
        CHECK (amount > 0),

    CONSTRAINT transactions_status_check
        CHECK (
            status IN (
                'PENDING',
                'COMPLETED',
                'FAILED',
                'REVERSED',
                'CANCELLED'
            )
        ),

    CONSTRAINT transactions_accounts_different_check
        CHECK (
            sender_account_id IS NULL
            OR receiver_account_id IS NULL
            OR sender_account_id <> receiver_account_id
        )
);


-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_transactions_sender_account
    ON transactions (sender_account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_receiver_account
    ON transactions (receiver_account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
    ON transactions (transaction_timestamp);

CREATE INDEX IF NOT EXISTS idx_transactions_type
    ON transactions (transaction_type_code);

CREATE INDEX IF NOT EXISTS idx_transactions_status
    ON transactions (status);

CREATE INDEX IF NOT EXISTS idx_transactions_country
    ON transactions (country_code);

CREATE INDEX IF NOT EXISTS idx_transactions_currency
    ON transactions (currency_code);

CREATE INDEX IF NOT EXISTS idx_transactions_sender_timestamp
    ON transactions (sender_account_id, transaction_timestamp);

CREATE INDEX IF NOT EXISTS idx_transactions_receiver_timestamp
    ON transactions (receiver_account_id, transaction_timestamp);