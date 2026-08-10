-- ============================================================
-- Data & Security Copilot
-- Reference Tables
-- ============================================================

-- ------------------------------------------------------------
-- Countries
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS countries (
    country_code CHAR(2) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);


-- ------------------------------------------------------------
-- Currencies
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS currencies (
    currency_code CHAR(3) PRIMARY KEY,
    currency_name VARCHAR(100) NOT NULL UNIQUE,
    symbol VARCHAR(10),
    decimal_places SMALLINT NOT NULL DEFAULT 2,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT currencies_decimal_places_check
        CHECK (decimal_places BETWEEN 0 AND 4)
);


-- ------------------------------------------------------------
-- Transaction Types
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS transaction_types (
    transaction_type_code VARCHAR(30) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);


-- ------------------------------------------------------------
-- Seed Reference Data
-- ------------------------------------------------------------

INSERT INTO countries (
    country_code,
    country_name
)
VALUES
    ('US', 'United States'),
    ('CA', 'Canada'),
    ('GB', 'United Kingdom'),
    ('IN', 'India'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('SG', 'Singapore'),
    ('AU', 'Australia'),
    ('JP', 'Japan'),
    ('BR', 'Brazil')
ON CONFLICT (country_code) DO NOTHING;


INSERT INTO currencies (
    currency_code,
    currency_name,
    symbol,
    decimal_places
)
VALUES
    ('USD', 'United States Dollar', '$', 2),
    ('CAD', 'Canadian Dollar', 'C$', 2),
    ('GBP', 'British Pound', '£', 2),
    ('INR', 'Indian Rupee', '₹', 2),
    ('EUR', 'Euro', '€', 2),
    ('SGD', 'Singapore Dollar', 'S$', 2),
    ('AUD', 'Australian Dollar', 'A$', 2),
    ('JPY', 'Japanese Yen', '¥', 0),
    ('BRL', 'Brazilian Real', 'R$', 2)
ON CONFLICT (currency_code) DO NOTHING;


INSERT INTO transaction_types (
    transaction_type_code,
    description
)
VALUES
    ('TRANSFER', 'Transfer between bank accounts'),
    ('DEPOSIT', 'Deposit into a bank account'),
    ('WITHDRAWAL', 'Withdrawal from a bank account'),
    ('PAYMENT', 'Payment to a merchant or service'),
    ('REFUND', 'Refund from a merchant or service'),
    ('FEE', 'Banking fee charged to an account'),
    ('ATM', 'ATM cash transaction')
ON CONFLICT (transaction_type_code) DO NOTHING;