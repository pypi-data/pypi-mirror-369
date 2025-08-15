# dated_money.rates
# Copyright 2022 Juan Reyero
# SPDX-License-Identifier: MIT

import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Optional, Union

import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from dated_money.currency import Currency
from dated_money.logger import logger

if TYPE_CHECKING:
    from supabase import Client

load_dotenv()


def parse_date(dt: Union[date, str]) -> date:
    if isinstance(dt, str):
        try:
            return datetime.strptime(dt, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format: '{dt}'. Expected YYYY-MM-DD format.") from e
    if isinstance(dt, date):
        return dt
    raise TypeError(f"Expected date or str, got {type(dt).__name__}")


def parse_optional_date(
    dt: Union[str, date, None], defaults_to: Optional[Union[str, date]] = None
) -> Union[date, None]:
    if dt is None:
        return parse_date(defaults_to) if defaults_to is not None else None
    return parse_date(dt)


def format_date(dt: Union[date, str]) -> str:
    # It should fail if a string is not in the yyyy-mm-dd format.
    as_date = parse_date(dt) if isinstance(dt, str) else dt
    return as_date.strftime("%Y-%m-%d")


class ConnectionPool:
    _instance = None
    _lock = threading.Lock()
    _db_file: ClassVar[str] = ""
    _ref_count: ClassVar[int] = 0
    _connection = None

    def __new__(cls, db_file: str):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._db_file = db_file
        return cls._instance

    @classmethod
    def get_connection(cls):
        with cls._lock:
            if cls._connection is None:
                cls._connection = sqlite3.connect(cls._db_file)
                cls._connection.row_factory = sqlite3.Row
            cls._ref_count += 1
            return cls._connection

    @classmethod
    def release_connection(cls):
        with cls._lock:
            cls._ref_count -= 1
            if cls._ref_count == 0 and cls._connection is not None:
                cls._connection.close()
                cls._connection = None


CONNECTION_POOL = None


@contextmanager
def get_db_connection(database_dir: Optional[str] = None):
    global CONNECTION_POOL
    if CONNECTION_POOL is None:
        if database_dir:
            ddir = Path(database_dir)
        elif "DMON_RATES_CACHE" in os.environ:
            ddir = Path(os.environ["DMON_RATES_CACHE"])
        else:
            # Use standard cache directory based on platform
            if sys.platform == "darwin":
                # macOS: ~/Library/Caches/dated_money
                ddir = Path.home() / "Library" / "Caches" / "dated_money"
            elif sys.platform == "win32":
                # Windows: %LOCALAPPDATA%\dated_money\cache
                ddir = (
                    Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
                    / "dated_money"
                    / "cache"
                )
            else:
                # Linux/Unix: ~/.cache/dated_money
                cache_home = os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
                ddir = Path(cache_home) / "dated_money"

        ddir.mkdir(parents=True, exist_ok=True)
        CONNECTION_POOL = ConnectionPool(str(ddir / "exchange-rates.db"))

    connection = CONNECTION_POOL.get_connection()
    try:
        yield connection
    finally:
        CONNECTION_POOL.release_connection()


def maybe_create_cache_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        columns = ", ".join(f'"{currency.value}" TEXT' for currency in Currency)
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS rates (
                       date TEXT PRIMARY KEY, {columns}
                )
            """
        )
        conn.commit()


def cache_day_rates(dt: Union[date, str], rates: dict[str, float]):
    maybe_create_cache_table()
    with get_db_connection() as conn:
        valid_currencies = {currency.value for currency in Currency}
        filtered_rates = {
            currency: str(rate)
            for currency, rate in rates.items()
            if currency.lower() in valid_currencies
        }

        columns = ", ".join(f'"{currency.lower()}"' for currency in filtered_rates)
        placeholders = ", ".join("?" * len(filtered_rates))
        values = tuple(filtered_rates.values())

        cursor = conn.cursor()
        cursor.execute(
            f"INSERT OR REPLACE INTO rates (date, {columns}) VALUES (?, {placeholders})",
            (format_date(dt), *values),
        )
        conn.commit()


def fill_cache_db():
    maybe_create_cache_table()
    repo_dir = os.environ.get("DMON_RATES_REPO")
    if repo_dir is None:
        raise ValueError("DMON_RATES_REPO environment variable is not set")

    repo_path = Path(repo_dir)
    money_dir = repo_path / "money"
    for file_path in money_dir.glob("*-rates.json"):
        with open(file_path) as file:
            data = json.load(file)
            rates = data["conversion_rates"]
            date_str = file_path.stem.replace("-rates", "")
            cache_day_rates(date_str, rates)


def get_day_rates_from_repo(on_date: Union[date, str]) -> Optional[dict[str, float]]:
    """Fetches exchange rates from a local git repository for a given
    date. It looks for the repository in the environment variable
    DMON_RATES_REPO, and the rates file in
    money/yyyy-mm-dd-rates.json.

    The rates file is a json that contains a dictionary like:

    {
     "conversion_rates":{
      "USD":1,
      "AED":3.6725,
      "AFN":71.3141,
    ...}
    }

    Arguments:

    - on_date: The date for which to fetch the exchange rates. If it
               is a string it should be in 'YYYY-MM-DD' format.

    Returns the exchange rates as a dictionary, or None if the rates
    cannot be found for the specified date.

    Environment variables:

    - DMON_RATES_REPO: directory containing a git repository with the
                       rates files in the money subdirectory.

    """
    repo_dir = os.environ.get("DMON_RATES_REPO", None)
    if repo_dir is None:
        return None

    repo_path = Path(repo_dir)
    if not repo_path.exists():
        return None

    logger.debug(f"Attempting to get rates from repo for {on_date}")
    rates_file_path = repo_path / "money" / f"{format_date(on_date)}-rates.json"

    if not rates_file_path.exists():
        # Attempt to update the local repository
        try:
            subprocess.run(
                ["git", "-C", repo_dir, "pull"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            return None

    if rates_file_path.exists():
        with open(rates_file_path, encoding="utf-8") as file:
            rates = json.load(file)
            return rates["conversion_rates"]

    return None


def fetch_rates_from_exchangerate_api(on_date: Union[date, str]) -> Optional[dict[str, float]]:
    """Fetches currency exchange rates from exchangerate_api.com.

    Arguments:

    - on_date: The date for which to fetch the exchange rates, either
               as a date or as a string in the 'YYYY-MM-DD' format.

    Returns a dictionary mapping `Currency` enum members to their
    exchange rate against a base currency (usually USD) for the
    specified date. Returns None if the rates cannot be fetched.


    Environment variables:

    - DMON_EXCHANGERATE_API_KEY: API key for https://exchangerate-api.com.

    The external API used for downloading rates
    (https://exchangerate-api.com) may require a paid plan for
    accessing historical data.

    """

    api_environment = "DMON_EXCHANGERATE_API_KEY"
    api_key = os.environ.get(api_environment, "")
    if not api_key:
        raise RuntimeError(
            "Need an api key for https://www.exchangerate-api.com "
            f"in the environment variable {api_environment}"
        )

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    if parse_date(on_date) != date.today():
        # Requires a paid plan
        # https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/history/USD/" + format_date(
            on_date
        ).replace("-", "/")

    response = requests.get(url)

    if response.status_code == 200:  # Checks if the request was successful
        rates = response.json()
        # Checks if 'conversion_rates' is in the response and returns it, otherwise returns None
        return rates.get("conversion_rates")
    else:
        # Log or handle unsuccessful request appropriately
        logger.warning(f"Failed to fetch rates for {on_date}: HTTP {response.status_code}")
        return None


def get_supabase_client() -> Optional["Client"]:
    """Get a Supabase client if credentials are available"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")  # This should be the anon key, not service role

    if not url or not key:
        return None

    from supabase import create_client

    return create_client(url, key)


def get_day_rates_from_supabase(on_date: Union[date, str]) -> Optional[dict[str, float]]:
    """Fetches exchange rates from Supabase for a given date.

    Arguments:
    - on_date: The date for which to fetch the exchange rates. If it
               is a string it should be in 'YYYY-MM-DD' format.

    Returns the exchange rates as a dictionary, or None if the rates
    cannot be found for the specified date.

    Environment variables:
    - SUPABASE_URL: Supabase project URL
    - SUPABASE_KEY: Supabase anon key
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        logger.debug("Trying to get rates from supabase")
        response = client.rpc(
            "get_rates_for_date", {"target_date": format_date(on_date)}
        ).execute()

        if response.data:
            return response.data["conversion_rates"]
    except Exception as e:
        logger.error(f"Error fetching rates from Supabase: {e}")

    return None


def find_rates_for_date(
    on_date: Union[date, str],
) -> tuple[Optional[dict[str, float]], Optional[date]]:
    """Attempts to find rates for a given date, falling back to previous dates if needed.

    Arguments:
    - on_date: The target date to find rates for

    Returns:
    - Tuple of (rates_dict, actual_date) if found, or (None, None) if no rates found
    """
    current_date = parse_date(on_date)
    max_days_back = 10  # Limit how far back we look to avoid infinite loops
    days_checked = 0

    while days_checked < max_days_back:
        # Try getting rates for current date
        rates = get_day_rates_from_repo(current_date)
        if rates:
            return rates, current_date

        rates = get_day_rates_from_supabase(current_date)
        if rates:
            return rates, current_date

        # Only try exchangerate API for the actual requested date
        if days_checked == 0:
            rates = fetch_rates_from_exchangerate_api(current_date)
            if rates:
                return rates, current_date

        # Move to previous day
        current_date = current_date - relativedelta(days=1)
        days_checked += 1

    return None, None


def get_rates(
    on_date: Union[date, str], *currencies: Currency
) -> Optional[dict[Currency, Optional[Decimal]]]:
    """Retrieves the exchange rates for the specified currencies on a given date.

    **Rate Fallback Behavior:**
    If rates are not available for the specified date, the function will
    automatically search for rates from previous dates, going back up to 10 days.
    This ensures that currency conversions can still be performed even when
    rates for the exact date are missing (e.g., weekends, holidays).
    When fallback rates are used, a log message will indicate which date's
    rates were actually used.

    **Data Sources (tried in order):**
    1. Local SQLite cache
    2. Local git repository (if DMON_RATES_REPO is set)
    3. Supabase (if SUPABASE_URL and SUPABASE_KEY are set)
    4. exchangerate-api.com (if DMON_EXCHANGERATE_API_KEY is set)

    Once fetched from any source, rates are cached locally for future use.

    Args:
        on_date: The date for which to fetch exchange rates (date object or 'YYYY-MM-DD' string)
        *currencies: Variable length argument list of Currency enum members

    Returns:
        Dictionary mapping each requested currency to its exchange rate as Decimal.
        Returns None if no rates could be fetched from any source.
        Individual currency rates may be None if not available.

    Environment variables:
        - DMON_RATES_CACHE: Directory for SQLite cache (default: current directory)
        - DMON_RATES_REPO: Git repository containing rates JSON files
        - SUPABASE_URL: Supabase project URL
        - SUPABASE_KEY: Supabase anon key
        - DMON_EXCHANGERATE_API_KEY: API key for exchangerate-api.com

    Example:
        >>> # This would return rates if data is available:
        >>> # rates = get_rates("2024-01-15", Currency.USD, Currency.EUR)
        >>> # print(rates[Currency.EUR])  # EUR rate on 2024-01-15
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ", ".join(f'"{currency.value}"' for currency in currencies)
        if not placeholders:
            placeholders = "*"

        try:
            cursor.execute(
                f"SELECT {placeholders} FROM rates WHERE date = ?", (format_date(on_date),)
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.warning(f"Database error when fetching rates: {e}")
            row = None

        out = None
        if row:
            out = {currency: row[i] for i, currency in enumerate(currencies)}
        else:
            # If not in cache, try to find rates from the requested date or earlier
            rates, found_date = find_rates_for_date(on_date)

            if rates:

                if found_date:
                    cache_day_rates(found_date, rates)

                if found_date != parse_date(on_date):
                    logger.info(f"Using rates from {found_date} for {on_date}")

                out = {currency: rates.get(currency.value.upper()) for currency in currencies}

        if out:
            return {c: Decimal(v) if v is not None else None for c, v in out.items()}

        return None


def get_rate(on_date: Union[date, str], currency: Currency) -> Optional[Decimal]:
    rate = get_rates(on_date, currency)
    if rate is not None:
        return rate[currency]

    return None


def fetch_period_rates(from_date: Union[date, str], to_date: Union[date, str]) -> None:
    """Builds a rates cache by querying the rates for each day in a
    period. If you don't have a repository with the conversion rates
    json files, it will attempt to download them from
    exchangerate_api.com.

    You will need a paid API key for this.

    Arguments:

    - from_date: First date to add to the cache, as a date object or a
                 string in yyyy-mm-dd format.

    - to_date: Last date to add to the cache, as a date object or a
               string in yyyy-mm-dd format.

    """
    logger.info(f"Downloading rates from {from_date} to {to_date}")
    dt = parse_date(from_date)
    to_dt = parse_date(to_date)
    while dt <= to_dt:
        get_rates(str(dt))
        time.sleep(0.5)
        dt = dt + relativedelta(days=1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Currency Conversion Cache Management")
    parser.add_argument(
        "-C",
        "--update-cache",
        action="store_true",
        help="Update the currency rates cache database",
    )
    parser.add_argument(
        "--create-table",
        action="store_true",
        help="Create the currency rates cache table",
    )
    parser.add_argument(
        "-r",
        "--rate-on",
        help="Retrieve the exchange rate[s] on date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "-c", "--currency", help="Optional: Currency for which to retrieve the exchange rate"
    )
    parser.add_argument(
        "--fetch-rates",
        help="Retrieve the exchange rates of all the days in a period. Format YYYY-MM-DD:YYYY-MM-DD",
    )

    args = parser.parse_args()

    if args.create_table:
        logger.info("Updating currency conversion cache database...")
        maybe_create_cache_table()
        logger.info("Cache database updated successfully.")

    if args.update_cache:
        logger.info("Updating currency conversion cache database...")
        fill_cache_db()
        logger.info("Cache database updated successfully.")

    if args.fetch_rates:
        from_dt, to_dt = args.fetch_rates.split(":")
        fetch_period_rates(from_dt, to_dt)

    rate_on_date = args.rate_on
    currency = args.currency

    if rate_on_date:
        if currency:
            currency = Currency(currency.lower())
            rate = get_rate(rate_on_date, currency)
            if rate is not None:
                print(f"Exchange rate for {currency} on {rate_on_date}: {repr(rate)}")
            else:
                print(f"Exchange rate not found for {currency} on {rate_on_date}")
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM rates WHERE date = ?", (rate_on_date,))
                row = cursor.fetchone()
                if row:
                    rates = {Currency(k.lower()): v for k, v in zip(row.keys()[1:], row[1:])}
                    print(f"Exchange rates on {rate_on_date}:")
                    for currency, rate in rates.items():
                        print(f"{currency}: {repr(rate)}")
                else:
                    print(f"Exchange rates not found for {rate_on_date}")


if __name__ == "__main__":
    main()
