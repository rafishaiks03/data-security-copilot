-- ============================================================
-- Data & Security Copilot
-- Stored Procedures / Database Business Logic
-- ============================================================


-- ============================================================
-- 1. Transfer Funds
-- ============================================================

CREATE OR REPLACE FUNCTION sp_transfer_funds(
    p_sender_account_id UUID,
    p_receiver_account_id UUID,
    p_amount NUMERIC(19, 4),
    p_currency_code CHAR(3),
    p_country_code CHAR(2),
    p_description VARCHAR(255) DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_sender_balance NUMERIC(19, 4);
    v_sender_currency CHAR(3);
    v_sender_status VARCHAR(20);

    v_receiver_currency CHAR(3);
    v_receiver_status VARCHAR(20);

    v_transaction_id UUID;
BEGIN

    -- --------------------------------------------------------
    -- Validate amount
    -- --------------------------------------------------------

    IF p_amount <= 0 THEN
        RAISE EXCEPTION
            'Transfer amount must be greater than zero';
    END IF;


    -- --------------------------------------------------------
    -- Prevent sender and receiver from being identical
    -- --------------------------------------------------------

    IF p_sender_account_id = p_receiver_account_id THEN
        RAISE EXCEPTION
            'Sender and receiver accounts must be different';
    END IF;


    -- --------------------------------------------------------
    -- Lock sender account
    --
    -- FOR UPDATE prevents another transaction from modifying
    -- the same account balance simultaneously.
    -- --------------------------------------------------------

    SELECT
        balance,
        currency_code,
        status
    INTO
        v_sender_balance,
        v_sender_currency,
        v_sender_status
    FROM accounts
    WHERE account_id = p_sender_account_id
    FOR UPDATE;


    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Sender account does not exist: %',
            p_sender_account_id;
    END IF;


    -- --------------------------------------------------------
    -- Validate sender account status
    -- --------------------------------------------------------

    IF v_sender_status <> 'ACTIVE' THEN
        RAISE EXCEPTION
            'Sender account is not active. Current status: %',
            v_sender_status;
    END IF;


    -- --------------------------------------------------------
    -- Validate sender currency
    -- --------------------------------------------------------

    IF v_sender_currency <> p_currency_code THEN
        RAISE EXCEPTION
            'Sender account currency (%) does not match transaction currency (%)',
            v_sender_currency,
            p_currency_code;
    END IF;


    -- --------------------------------------------------------
    -- Check sender balance
    -- --------------------------------------------------------

    IF v_sender_balance < p_amount THEN
        RAISE EXCEPTION
            'Insufficient funds. Available: %, Requested: %',
            v_sender_balance,
            p_amount;
    END IF;


    -- --------------------------------------------------------
    -- Lock receiver account
    -- --------------------------------------------------------

    SELECT
        currency_code,
        status
    INTO
        v_receiver_currency,
        v_receiver_status
    FROM accounts
    WHERE account_id = p_receiver_account_id
    FOR UPDATE;


    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Receiver account does not exist: %',
            p_receiver_account_id;
    END IF;


    -- --------------------------------------------------------
    -- Validate receiver account status
    -- --------------------------------------------------------

    IF v_receiver_status <> 'ACTIVE' THEN
        RAISE EXCEPTION
            'Receiver account is not active. Current status: %',
            v_receiver_status;
    END IF;


    -- --------------------------------------------------------
    -- Validate receiver currency
    --
    -- Currency conversion is intentionally not supported yet.
    -- --------------------------------------------------------

    IF v_receiver_currency <> p_currency_code THEN
        RAISE EXCEPTION
            'Receiver account currency (%) does not match transaction currency (%)',
            v_receiver_currency,
            p_currency_code;
    END IF;


    -- --------------------------------------------------------
    -- Debit sender
    -- --------------------------------------------------------

    UPDATE accounts
    SET
        balance = balance - p_amount
    WHERE account_id = p_sender_account_id;


    -- --------------------------------------------------------
    -- Credit receiver
    -- --------------------------------------------------------

    UPDATE accounts
    SET
        balance = balance + p_amount
    WHERE account_id = p_receiver_account_id;


    -- --------------------------------------------------------
    -- Create transaction record
    -- --------------------------------------------------------

    INSERT INTO transactions (
        sender_account_id,
        receiver_account_id,
        transaction_type_code,
        amount,
        currency_code,
        country_code,
        status,
        description
    )
    VALUES (
        p_sender_account_id,
        p_receiver_account_id,
        'TRANSFER',
        p_amount,
        p_currency_code,
        p_country_code,
        'COMPLETED',
        p_description
    )
    RETURNING transaction_id
    INTO v_transaction_id;


    -- --------------------------------------------------------
    -- Return transaction ID
    -- --------------------------------------------------------

    RETURN v_transaction_id;

END;
$$;


-- ============================================================
-- 2. Freeze Account
-- ============================================================

CREATE OR REPLACE FUNCTION sp_freeze_account(
    p_account_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE accounts
    SET
        status = 'FROZEN'
    WHERE account_id = p_account_id
      AND status = 'ACTIVE';

    IF FOUND THEN
        RETURN TRUE;
    END IF;

    RETURN FALSE;

END;
$$;


-- ============================================================
-- 3. Unfreeze Account
-- ============================================================

CREATE OR REPLACE FUNCTION sp_unfreeze_account(
    p_account_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE accounts
    SET
        status = 'ACTIVE'
    WHERE account_id = p_account_id
      AND status = 'FROZEN';

    IF FOUND THEN
        RETURN TRUE;
    END IF;

    RETURN FALSE;

END;
$$;


-- ============================================================
-- 4. Close Account
-- ============================================================

CREATE OR REPLACE FUNCTION sp_close_account(
    p_account_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance NUMERIC(19, 4);
    v_status VARCHAR(20);
BEGIN

    SELECT
        balance,
        status
    INTO
        v_balance,
        v_status
    FROM accounts
    WHERE account_id = p_account_id
    FOR UPDATE;


    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Account does not exist: %',
            p_account_id;
    END IF;


    IF v_status = 'CLOSED' THEN
        RETURN FALSE;
    END IF;


    IF v_balance <> 0 THEN
        RAISE EXCEPTION
            'Account cannot be closed because balance is %',
            v_balance;
    END IF;


    UPDATE accounts
    SET
        status = 'CLOSED',
        closed_at = CURRENT_TIMESTAMP
    WHERE account_id = p_account_id;


    RETURN TRUE;

END;
$$;


-- ============================================================
-- 5. Get Account Summary
-- ============================================================

CREATE OR REPLACE FUNCTION sp_get_account_summary(
    p_account_id UUID
)
RETURNS TABLE (
    account_id UUID,
    account_number VARCHAR(20),
    account_type VARCHAR(20),
    currency_code CHAR(3),
    balance NUMERIC(19, 4),
    status VARCHAR(20),
    customer_id UUID,
    customer_name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
        a.account_id,
        a.account_number,
        a.account_type,
        a.currency_code,
        a.balance,
        a.status,
        c.customer_id,
        c.first_name || ' ' || c.last_name
    FROM accounts a
    JOIN customers c
        ON c.customer_id = a.customer_id
    WHERE a.account_id = p_account_id;

END;
$$;