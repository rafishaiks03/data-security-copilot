"""
Data & Security Copilot
Synthetic Banking + Security Data Generator

This script generates realistic synthetic data for:

- Customers
- Accounts
- Devices
- Login events
- Transactions

A controlled percentage of transactions and login events are
generated as suspicious/fraudulent so that the ML pipeline
has labeled data to learn from.

The generator is designed to be SAFE TO RUN MULTIPLE TIMES.

Important behavior:

- Existing database data is preserved.
- New customer emails are guaranteed to be unique.
- Account numbers continue from the current maximum.
- UUID-based records remain unique.
- Each execution adds a new batch of data.
- A failed generation is rolled back by PostgreSQL.
"""

from __future__ import annotations

import argparse
import os
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import psycopg
from dotenv import load_dotenv
from faker import Faker
from psycopg.rows import dict_row

# ============================================================
# Load Environment Variables
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

ENV_FILE = os.path.join(
    PROJECT_ROOT,
    ".env",
)

load_dotenv(ENV_FILE)


# ============================================================
# Configuration
# ============================================================

DEFAULT_CUSTOMERS = 100
DEFAULT_FRAUD_RATE = 0.05
DEFAULT_SEED = 42

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
# Fake Data Configuration
# ============================================================

fake = Faker()

SUPPORTED_COUNTRIES = [
    ("US", "United States"),
    ("GB", "United Kingdom"),
    ("CA", "Canada"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("AU", "Australia"),
    ("IN", "India"),
    ("SG", "Singapore"),
]

COUNTRY_CURRENCIES = {
    "US": "USD",
    "GB": "GBP",
    "CA": "CAD",
    "DE": "EUR",
    "FR": "EUR",
    "AU": "AUD",
    "IN": "INR",
    "SG": "SGD",
}

ACCOUNT_TYPES = [
    "CHECKING",
    "SAVINGS",
]

DEVICE_TYPES = [
    "MOBILE",
    "TABLET",
    "DESKTOP",
    "LAPTOP",
]

OPERATING_SYSTEMS = {
    "MOBILE": [
        "iOS",
        "Android",
    ],
    "TABLET": [
        "iOS",
        "Android",
    ],
    "DESKTOP": [
        "Windows",
        "macOS",
        "Linux",
    ],
    "LAPTOP": [
        "Windows",
        "macOS",
        "Linux",
    ],
}

LOGIN_FAILURE_REASONS = [
    "INVALID_PASSWORD",
    "INVALID_OTP",
    "UNKNOWN_DEVICE",
    "ACCOUNT_LOCKED",
]


# ============================================================
# Data Classes
# ============================================================


@dataclass
class CustomerRecord:
    customer_id: uuid.UUID
    country_code: str


@dataclass
class AccountRecord:
    account_id: uuid.UUID
    customer_id: uuid.UUID
    currency_code: str
    country_code: str


@dataclass
class DeviceRecord:
    device_id: uuid.UUID
    customer_id: uuid.UUID
    country_code: str
    ip_address: str
    is_trusted: bool


# ============================================================
# Database Connection
# ============================================================


def get_database_connection() -> psycopg.Connection:
    """
    Create a connection to PostgreSQL.

    PostgreSQL is running inside Docker while this Python
    script is running on the Mac host.
    """

    if not DATABASE_PASSWORD:
        raise RuntimeError(
            "POSTGRES_PASSWORD is not configured. " f"Expected it in: {ENV_FILE}"
        )

    print(f"Connecting to PostgreSQL at " f"{DATABASE_HOST}:{DATABASE_PORT}...")

    return psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        row_factory=dict_row,
    )


# ============================================================
# Utility Functions
# ============================================================


def random_date(
    start: datetime,
    end: datetime,
) -> datetime:
    """
    Return a random UTC datetime between start and end.
    """

    delta = end - start

    random_seconds = random.randint(
        0,
        int(delta.total_seconds()),
    )

    return start + timedelta(
        seconds=random_seconds,
    )


def random_amount(
    minimum: float = 5,
    maximum: float = 5000,
) -> Decimal:
    """
    Generate a realistic monetary amount.
    """

    amount = round(
        random.uniform(
            minimum,
            maximum,
        ),
        2,
    )

    return Decimal(str(amount))


def generate_ip_address() -> str:
    """
    Generate a documentation/example IPv4 address.

    We intentionally use TEST-NET ranges rather than real
    public IP addresses.
    """

    networks = [
        "192.0.2",
        "198.51.100",
        "203.0.113",
    ]

    network = random.choice(networks)

    return f"{network}." f"{random.randint(1, 254)}"


def choose_country() -> str:
    """
    Select a synthetic customer's home country.
    """

    country, _ = random.choice(SUPPORTED_COUNTRIES)

    return country


def choose_currency(
    country_code: str,
) -> str:
    """
    Return the primary currency for a country.
    """

    return COUNTRY_CURRENCIES[country_code]


# ============================================================
# Customer Helpers
# ============================================================


def load_existing_customer_emails(
    cursor,
) -> set[str]:
    """
    Load existing customer emails.

    We use this set to guarantee that a newly generated
    customer never collides with an existing customer.
    """

    cursor.execute("""
        SELECT email
        FROM customers
        """)

    rows = cursor.fetchall()

    return {row["email"].lower() for row in rows if row["email"]}


def generate_unique_email(
    existing_emails: set[str],
) -> str:
    """
    Generate an email address that does not already exist.

    Faker remains deterministic for the rest of the generated
    dataset, but uniqueness is checked against PostgreSQL.
    """

    while True:

        first_name = fake.first_name()

        last_name = fake.last_name()

        random_suffix = random.randint(
            1000,
            999999999,
        )

        email = (
            f"{first_name.lower()}."
            f"{last_name.lower()}."
            f"{random_suffix}"
            "@example.com"
        )

        normalized_email = email.lower()

        if normalized_email not in existing_emails:

            existing_emails.add(normalized_email)

            return email


# ============================================================
# Customer Generation
# ============================================================


def generate_customers(
    cursor,
    customer_count: int,
) -> list[CustomerRecord]:
    """
    Generate customers and insert them into PostgreSQL.

    Existing customers are preserved.
    """

    customers: list[CustomerRecord] = []

    existing_emails = load_existing_customer_emails(cursor)

    for _ in range(customer_count):

        customer_id = uuid.uuid4()

        country_code = choose_country()

        first_name = fake.first_name()

        last_name = fake.last_name()

        email = generate_unique_email(existing_emails)

        date_of_birth = fake.date_of_birth(
            minimum_age=18,
            maximum_age=80,
        )

        kyc_status = random.choices(
            [
                "PENDING",
                "VERIFIED",
                "REJECTED",
            ],
            weights=[
                5,
                90,
                5,
            ],
            k=1,
        )[0]

        risk_score = Decimal(
            str(
                round(
                    random.uniform(
                        0.01,
                        0.80,
                    ),
                    4,
                )
            )
        )

        cursor.execute(
            """
            INSERT INTO customers (
                customer_id,
                first_name,
                last_name,
                email,
                date_of_birth,
                country_code,
                kyc_status,
                risk_score
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                customer_id,
                first_name,
                last_name,
                email,
                date_of_birth,
                country_code,
                kyc_status,
                risk_score,
            ),
        )

        customers.append(
            CustomerRecord(
                customer_id=customer_id,
                country_code=country_code,
            )
        )

    return customers


# ============================================================
# Account Generation
# ============================================================


def get_next_account_number(
    cursor,
) -> int:
    """
    Ask PostgreSQL for the current highest account number.

    Existing account numbers are preserved.

    Example:

        Existing:
            100000000001
            100000000002

        Next generated account:
            100000000003
    """

    cursor.execute("""
        SELECT COALESCE(
            MAX(account_number::BIGINT),
            100000000000
        ) AS max_account_number
        FROM accounts
        """)

    result = cursor.fetchone()

    if result is None:
        return 100000000001

    max_account_number = result["max_account_number"]

    return int(max_account_number) + 1


def generate_accounts(
    cursor,
    customers: list[CustomerRecord],
) -> list[AccountRecord]:
    """
    Generate one or two accounts for each customer.

    Account numbers start after the current highest
    account number in PostgreSQL.
    """

    accounts: list[AccountRecord] = []

    next_account_number = get_next_account_number(cursor)

    print(f"  Starting account number: " f"{next_account_number}")

    for customer in customers:

        account_count = random.choices(
            [1, 2],
            weights=[70, 30],
            k=1,
        )[0]

        for _ in range(account_count):

            account_id = uuid.uuid4()

            account_type = random.choice(ACCOUNT_TYPES)

            currency_code = choose_currency(customer.country_code)

            account_number = str(next_account_number)

            next_account_number += 1

            initial_balance = Decimal(
                str(
                    round(
                        random.uniform(
                            500,
                            25000,
                        ),
                        2,
                    )
                )
            )

            cursor.execute(
                """
                INSERT INTO accounts (
                    account_id,
                    customer_id,
                    account_number,
                    account_type,
                    currency_code,
                    balance,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'ACTIVE'
                )
                """,
                (
                    account_id,
                    customer.customer_id,
                    account_number,
                    account_type,
                    currency_code,
                    initial_balance,
                ),
            )

            accounts.append(
                AccountRecord(
                    account_id=account_id,
                    customer_id=customer.customer_id,
                    currency_code=currency_code,
                    country_code=customer.country_code,
                )
            )

    return accounts


# ============================================================
# Device Generation
# ============================================================


def generate_devices(
    cursor,
    customers: list[CustomerRecord],
) -> list[DeviceRecord]:
    """
    Generate one to three devices for each customer.
    """

    devices: list[DeviceRecord] = []

    now = datetime.now(timezone.utc)

    for customer in customers:

        device_count = random.randint(
            1,
            3,
        )

        for device_index in range(device_count):

            device_id = uuid.uuid4()

            device_type = random.choice(DEVICE_TYPES)

            operating_system = random.choice(OPERATING_SYSTEMS[device_type])

            ip_address = generate_ip_address()

            fingerprint = f"device-" f"{uuid.uuid4().hex}"

            is_trusted = device_index == 0

            first_seen = random_date(
                now - timedelta(days=365),
                now - timedelta(days=30),
            )

            last_seen = random_date(
                first_seen,
                now,
            )

            cursor.execute(
                """
                INSERT INTO devices (
                    device_id,
                    customer_id,
                    device_fingerprint,
                    device_type,
                    operating_system,
                    ip_address,
                    country_code,
                    first_seen_at,
                    last_seen_at,
                    is_trusted
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
                    %s,
                    %s
                )
                """,
                (
                    device_id,
                    customer.customer_id,
                    fingerprint,
                    device_type,
                    operating_system,
                    ip_address,
                    customer.country_code,
                    first_seen,
                    last_seen,
                    is_trusted,
                ),
            )

            devices.append(
                DeviceRecord(
                    device_id=device_id,
                    customer_id=customer.customer_id,
                    country_code=customer.country_code,
                    ip_address=ip_address,
                    is_trusted=is_trusted,
                )
            )

    return devices


# ============================================================
# Login Event Generation
# ============================================================


def generate_login_events(
    cursor,
    customers: list[CustomerRecord],
    devices: list[DeviceRecord],
    start_date: datetime,
    end_date: datetime,
    fraud_rate: float,
) -> int:
    """
    Generate normal and suspicious login activity.
    """

    devices_by_customer: dict[
        uuid.UUID,
        list[DeviceRecord],
    ] = {}

    for device in devices:

        devices_by_customer.setdefault(
            device.customer_id,
            [],
        ).append(device)

    login_count = 0

    for customer in customers:

        customer_devices = devices_by_customer.get(
            customer.customer_id,
            [],
        )

        if not customer_devices:
            continue

        normal_login_count = random.randint(
            3,
            12,
        )

        for _ in range(normal_login_count):

            device = random.choice(customer_devices)

            login_timestamp = random_date(
                start_date,
                end_date,
            )

            cursor.execute(
                """
                INSERT INTO login_events (
                    customer_id,
                    device_id,
                    ip_address,
                    country_code,
                    login_timestamp,
                    success,
                    failure_reason,
                    session_id
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE,
                    NULL,
                    %s
                )
                """,
                (
                    customer.customer_id,
                    device.device_id,
                    device.ip_address,
                    customer.country_code,
                    login_timestamp,
                    uuid.uuid4(),
                ),
            )

            login_count += 1

        if random.random() < fraud_rate:

            failed_attempts = random.randint(
                3,
                8,
            )

            for _ in range(failed_attempts):

                suspicious_ip = generate_ip_address()

                suspicious_country = random.choice(
                    [
                        country
                        for country, _ in SUPPORTED_COUNTRIES
                        if country != customer.country_code
                    ]
                )

                login_timestamp = random_date(
                    start_date,
                    end_date,
                )

                cursor.execute(
                    """
                    INSERT INTO login_events (
                        customer_id,
                        device_id,
                        ip_address,
                        country_code,
                        login_timestamp,
                        success,
                        failure_reason,
                        session_id
                    )
                    VALUES (
                        %s,
                        NULL,
                        %s,
                        %s,
                        %s,
                        FALSE,
                        %s,
                        NULL
                    )
                    """,
                    (
                        customer.customer_id,
                        suspicious_ip,
                        suspicious_country,
                        login_timestamp,
                        random.choice(LOGIN_FAILURE_REASONS),
                    ),
                )

                login_count += 1

    return login_count


# ============================================================
# Transaction Generation
# ============================================================


def generate_transactions(
    cursor,
    accounts: list[AccountRecord],
    devices: list[DeviceRecord],
    transaction_count: int,
    fraud_rate: float,
    start_date: datetime,
    end_date: datetime,
) -> int:
    """
    Generate normal and suspicious transactions.
    """

    if len(accounts) < 2:

        raise RuntimeError(
            "At least two accounts are required " "to generate transactions."
        )

    devices_by_customer: dict[
        uuid.UUID,
        list[DeviceRecord],
    ] = {}

    for device in devices:

        devices_by_customer.setdefault(
            device.customer_id,
            [],
        ).append(device)

    transaction_count_inserted = 0

    for _ in range(transaction_count):

        sender = random.choice(accounts)

        possible_receivers = [
            account
            for account in accounts
            if (
                account.account_id != sender.account_id
                and account.currency_code == sender.currency_code
            )
        ]

        if not possible_receivers:
            continue

        receiver = random.choice(possible_receivers)

        is_fraud = random.random() < fraud_rate

        if is_fraud:

            amount = random_amount(
                minimum=5000,
                maximum=25000,
            )

            transaction_country = random.choice(
                [
                    country
                    for country, _ in SUPPORTED_COUNTRIES
                    if country != sender.country_code
                ]
            )

            device_id = None

            transaction_hour = random.choice(
                [
                    1,
                    2,
                    3,
                    4,
                    23,
                ]
            )

            transaction_timestamp = random_date(
                start_date,
                end_date,
            ).replace(
                hour=transaction_hour,
                minute=random.randint(
                    0,
                    59,
                ),
                second=random.randint(
                    0,
                    59,
                ),
            )

            description = (
                "SYNTHETIC_FRAUD " "large_amount " "unusual_country " "untrusted_device"
            )

        else:

            amount = random_amount(
                minimum=5,
                maximum=1500,
            )

            transaction_country = sender.country_code

            customer_devices = devices_by_customer.get(
                sender.customer_id,
                [],
            )

            device_id = (
                random.choice(customer_devices).device_id if customer_devices else None
            )

            transaction_timestamp = random_date(
                start_date,
                end_date,
            )

            description = "SYNTHETIC_NORMAL_TRANSACTION"

        cursor.execute(
            """
            INSERT INTO transactions (
                sender_account_id,
                receiver_account_id,
                transaction_type_code,
                amount,
                currency_code,
                country_code,
                device_id,
                transaction_timestamp,
                status,
                description
            )
            VALUES (
                %s,
                %s,
                'TRANSFER',
                %s,
                %s,
                %s,
                %s,
                %s,
                'COMPLETED',
                %s
            )
            """,
            (
                sender.account_id,
                receiver.account_id,
                amount,
                sender.currency_code,
                transaction_country,
                device_id,
                transaction_timestamp,
                description,
            ),
        )

        transaction_count_inserted += 1

    return transaction_count_inserted


# ============================================================
# Main Generation Pipeline
# ============================================================


def generate_data(
    customer_count: int,
    fraud_rate: float,
    seed: int,
    transactions_per_customer: int,
) -> None:
    """
    Execute the complete synthetic data generation pipeline.

    The transaction volume is explicitly configurable.

    Example:

        1000 customers
        20 transactions/customer

        => approximately 20,000 transactions
    """

    random.seed(seed)

    Faker.seed(seed)

    fake.seed_instance(seed)

    print()

    print("=" * 60)

    print("Data & Security Copilot")

    print("Synthetic Data Generator")

    print("=" * 60)

    print()

    print(f"Customers requested : " f"{customer_count}")

    print(f"Fraud rate          : " f"{fraud_rate:.2%}")

    print(f"Transactions/customer: " f"{transactions_per_customer}")

    print(f"Random seed         : " f"{seed}")

    print()

    start_date = datetime.now(timezone.utc) - timedelta(days=90)

    end_date = datetime.now(timezone.utc)

    transaction_count = customer_count * transactions_per_customer

    try:

        with get_database_connection() as connection:

            with connection.cursor() as cursor:

                print("Generating customers...")

                customers = generate_customers(
                    cursor,
                    customer_count,
                )

                print(f"  Created " f"{len(customers)} customers")

                print("Generating accounts...")

                accounts = generate_accounts(
                    cursor,
                    customers,
                )

                print(f"  Created " f"{len(accounts)} accounts")

                print("Generating devices...")

                devices = generate_devices(
                    cursor,
                    customers,
                )

                print(f"  Created " f"{len(devices)} devices")

                print("Generating login events...")

                login_count = generate_login_events(
                    cursor,
                    customers,
                    devices,
                    start_date,
                    end_date,
                    fraud_rate,
                )

                print(f"  Created " f"{login_count} login events")

                print("Generating transactions...")

                print(f"  Target transaction count: " f"{transaction_count}")

                transactions = generate_transactions(
                    cursor,
                    accounts,
                    devices,
                    transaction_count,
                    fraud_rate,
                    start_date,
                    end_date,
                )

                print(f"  Created " f"{transactions} transactions")

            connection.commit()

        print()

        print("=" * 60)

        print("Synthetic data generation " "completed successfully.")

        print("=" * 60)

        print()

    except Exception as exc:

        print()

        print("=" * 60)

        print("ERROR: Synthetic data generation failed.")

        print("=" * 60)

        print()

        print(str(exc))

        print()

        raise


# ============================================================
# Command Line Interface
# ============================================================


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Generate synthetic banking "
            "and security data for "
            "Data & Security Copilot."
        )
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=DEFAULT_CUSTOMERS,
        help=("Number of NEW synthetic " "customers to generate."),
    )

    parser.add_argument(
        "--fraud-rate",
        type=float,
        default=DEFAULT_FRAUD_RATE,
        help=(
            "Fraction of generated " "transactions and suspicious " "login activity."
        ),
    )

    parser.add_argument(
        "--transactions-per-customer",
        type=int,
        default=20,
        help=("Number of transactions to " "generate per NEW customer."),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=("Random seed used for " "reproducible synthetic data."),
    )

    return parser.parse_args()


def main() -> None:
    """
    Application entry point.
    """

    args = parse_arguments()

    if args.customers <= 0:

        raise ValueError("--customers must be greater than zero.")

    if not 0 <= args.fraud_rate <= 1:

        raise ValueError("--fraud-rate must be between 0 and 1.")

    if args.transactions_per_customer <= 0:

        raise ValueError("--transactions-per-customer " "must be greater than zero.")

    generate_data(
        customer_count=args.customers,
        fraud_rate=args.fraud_rate,
        seed=args.seed,
        transactions_per_customer=(args.transactions_per_customer),
    )


if __name__ == "__main__":
    main()
