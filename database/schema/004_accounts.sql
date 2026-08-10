-- ============================================================
-- Data & Security Copilot
-- Accounts
-- ============================================================

CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    customer_id UUID NOT NULL,

    account_number VARCHAR(20) NOT NULL UNIQUE,

    account_type VARCHAR(20) NOT NULL,

    currency_code CHAR(3) NOT NULL,

    balance NUMERIC(19, 4) NOT NULL DEFAULT 0.0000,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    opened_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    closed_at TIMESTAMPTZ,

    CONSTRAINT accounts_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),

    CONSTRAINT accounts_currency_fk
        FOREIGN KEY (currency_code)
        REFERENCES currencies (currency_code),

    CONSTRAINT accounts_account_type_check
        CHECK (
            account_type IN (
                'CHECKING',
                'SAVINGS',
                'BUSINESS'
            )
        ),

    CONSTRAINT accounts_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'FROZEN',
                'CLOSED'
            )
        ),

    CONSTRAINT accounts_balance_check
        CHECK (
            balance >= 0
        ),

    CONSTRAINT accounts_closed_at_check
        CHECK (
            closed_at IS NULL
            OR closed_at >= opened_at
        )
);


-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
    ON accounts (customer_id);

CREATE INDEX IF NOT EXISTS idx_accounts_currency_code
    ON accounts (currency_code);

CREATE INDEX IF NOT EXISTS idx_accounts_status
    ON accounts (status);

CREATE INDEX IF NOT EXISTS idx_accounts_customer_status
    ON accounts (customer_id, status);