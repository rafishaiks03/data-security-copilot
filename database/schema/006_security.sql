-- ============================================================
-- Data & Security Copilot
-- Security: Devices + Login Events
-- ============================================================


-- ============================================================
-- Devices
-- ============================================================

CREATE TABLE IF NOT EXISTS devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    customer_id UUID NOT NULL,

    device_fingerprint VARCHAR(255) NOT NULL,

    device_type VARCHAR(30) NOT NULL,

    operating_system VARCHAR(50),

    ip_address INET,

    country_code CHAR(2),

    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    is_trusted BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT devices_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),

    CONSTRAINT devices_country_fk
        FOREIGN KEY (country_code)
        REFERENCES countries (country_code),

    CONSTRAINT devices_device_type_check
        CHECK (
            device_type IN (
                'MOBILE',
                'TABLET',
                'DESKTOP',
                'LAPTOP',
                'OTHER'
            )
        ),

    CONSTRAINT devices_last_seen_check
        CHECK (
            last_seen_at >= first_seen_at
        )
);


-- ------------------------------------------------------------
-- Device Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_devices_customer_id
    ON devices (customer_id);

CREATE INDEX IF NOT EXISTS idx_devices_country_code
    ON devices (country_code);

CREATE INDEX IF NOT EXISTS idx_devices_ip_address
    ON devices (ip_address);

CREATE INDEX IF NOT EXISTS idx_devices_last_seen_at
    ON devices (last_seen_at);

CREATE INDEX IF NOT EXISTS idx_devices_customer_trusted
    ON devices (customer_id, is_trusted);


-- ============================================================
-- Login Events
-- ============================================================

CREATE TABLE IF NOT EXISTS login_events (
    login_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    customer_id UUID NOT NULL,

    device_id UUID,

    ip_address INET,

    country_code CHAR(2),

    login_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    success BOOLEAN NOT NULL,

    failure_reason VARCHAR(100),

    session_id UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT login_events_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),

    CONSTRAINT login_events_device_fk
        FOREIGN KEY (device_id)
        REFERENCES devices (device_id),

    CONSTRAINT login_events_country_fk
        FOREIGN KEY (country_code)
        REFERENCES countries (country_code),

    CONSTRAINT login_events_failure_reason_check
        CHECK (
            success = TRUE
            OR failure_reason IS NOT NULL
        )
);


-- ------------------------------------------------------------
-- Login Event Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_login_events_customer_id
    ON login_events (customer_id);

CREATE INDEX IF NOT EXISTS idx_login_events_device_id
    ON login_events (device_id);

CREATE INDEX IF NOT EXISTS idx_login_events_ip_address
    ON login_events (ip_address);

CREATE INDEX IF NOT EXISTS idx_login_events_timestamp
    ON login_events (login_timestamp);

CREATE INDEX IF NOT EXISTS idx_login_events_customer_timestamp
    ON login_events (customer_id, login_timestamp);

CREATE INDEX IF NOT EXISTS idx_login_events_failed_attempts
    ON login_events (customer_id, success, login_timestamp);