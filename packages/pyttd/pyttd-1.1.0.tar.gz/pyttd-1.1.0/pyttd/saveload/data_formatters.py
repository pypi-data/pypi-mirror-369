"""
Data Formatters

Functions for formatting and converting OpenTTD data to sane and human-readable formats.
"""

from typing import Dict, List, Any, Optional, Collection
from .company_names import generate_company_name, generate_president_name, get_color_name

# Expense categories - from economy_type.h
_expense_categories = [
    "Construction",  # EXPENSES_CONSTRUCTION
    "New Vehicles",  # EXPENSES_NEW_VEHICLES
    "Train Running",  # EXPENSES_TRAIN_RUN
    "Road Vehicle Running",  # EXPENSES_ROADVEH_RUN
    "Aircraft Running",  # EXPENSES_AIRCRAFT_RUN
    "Ship Running",  # EXPENSES_SHIP_RUN
    "Property",  # EXPENSES_PROPERTY
    "Train Revenue",  # EXPENSES_TRAIN_REVENUE
    "Road Vehicle Revenue",  # EXPENSES_ROADVEH_REVENUE
    "Aircraft Revenue",  # EXPENSES_AIRCRAFT_REVENUE
    "Ship Revenue",  # EXPENSES_SHIP_REVENUE
    "Loan Interest",  # EXPENSES_LOAN_INTEREST
    "Other",  # EXPENSES_OTHER
]


def convert_date_to_year(date_value: int) -> int:
    """Convert date value to year"""
    # Constants from timer_game_common.h
    ORIGINAL_BASE_YEAR = 1920

    # Calculate DAYS_TILL_ORIGINAL_BASE_YEAR (days from Year 0 to 1920)
    year_as_int = ORIGINAL_BASE_YEAR
    number_of_leap_years = (
        (year_as_int - 1) // 4 - (year_as_int - 1) // 100 + (year_as_int - 1) // 400 + 1
    )
    DAYS_TILL_ORIGINAL_BASE_YEAR = (365 * year_as_int) + number_of_leap_years

    # Convert date to years since base year
    days_since_base_year = date_value - DAYS_TILL_ORIGINAL_BASE_YEAR
    # Leap years (365.25 average)
    years_since_base = days_since_base_year / 365.25

    return int(ORIGINAL_BASE_YEAR + years_since_base)


def convert_date_to_ymd(date_value: int) -> Dict[str, int]:
    """Convert date value to year, month, day"""
    # Constants from OpenTTD source
    ORIGINAL_BASE_YEAR = 1920
    DAYS_TILL_ORIGINAL_BASE_YEAR = 701265  # Pre-calculated

    # Calculate days since base year
    days_since_base = date_value - DAYS_TILL_ORIGINAL_BASE_YEAR

    # Calculate year (accounting for leap years)
    year = ORIGINAL_BASE_YEAR
    remaining_days = days_since_base

    # Handle negative dates (before 1920)
    if remaining_days < 0:
        while remaining_days < 0:
            year -= 1
            days_in_year = 366 if is_leap_year(year) else 365
            remaining_days += days_in_year
    else:
        # Handle positive dates (after 1920)
        while remaining_days >= (366 if is_leap_year(year) else 365):
            days_in_year = 366 if is_leap_year(year) else 365
            remaining_days -= days_in_year
            year += 1

    # Calculate month and day
    days_in_month = [
        31,
        29 if is_leap_year(year) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]

    month = 1
    day_of_year = remaining_days + 1  # 1-based

    for month_days in days_in_month:
        if day_of_year <= month_days:
            day = day_of_year
            break
        day_of_year -= month_days
        month += 1
    else:
        # Shouldn't happen, but why not
        month = 12
        day = 31

    return {
        "year": year,
        "month": month,
        "day": day,
        "date_value": date_value,
        "days_since_base": days_since_base,
    }


def is_leap_year(year: int) -> bool:
    """Check if year is leap year"""
    return (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))


def format_inflation_value(inflation_value: int) -> Dict[str, Any]:
    """Convert inflation to human-readable format"""
    # Inflation uses 16-bit fractional representation
    # Base value is 1 << 16 = 65536 (representing 1.0x multiplier)
    BASE_INFLATION = 65536

    # Calculate multiplier
    multiplier = inflation_value / BASE_INFLATION

    # Calculate percentage change from base
    percentage_change = (multiplier - 1.0) * 100

    return {
        "raw_value": inflation_value,
        "multiplier": round(multiplier, 6),
        "percentage_change": round(percentage_change, 2),
        "description": f"{multiplier:.2f}x multiplier"
        + (
            f" (+{percentage_change:.1f}%)"
            if percentage_change > 0
            else f" ({percentage_change:.1f}%)" if percentage_change < 0 else " (no change)"
        ),
    }


def format_money(money: int, money_fraction: int = 0) -> int:
    """Format money as integer"""
    # OpenTTD money_fraction is additional cents/pence etc beyond the base money
    total_cents = money * 100 + money_fraction
    return round(total_cents / 100)


def format_coordinate(coord: int, map_size_x: int = 256) -> Optional[Dict[str, int]]:
    """Convert coordinate to x,y pair"""
    if coord == 0xFFFFFFFF:  # Invalid coordinate
        return None
    x = coord % map_size_x
    y = coord // map_size_x
    return {"x": x, "y": y}


def format_yearly_expenses(expenses: List[int], current_year: int = 1960) -> Dict[str, Any]:
    """Format yearly expenses array with category labels."""
    if len(expenses) != 39:
        return {"raw_data": expenses, "note": f"Unexpected length {len(expenses)}, expected 39"}

    years: List[Dict[str, Any]] = []
    totals_by_category: Dict[str, int] = {}

    # Process 3 years of data
    for year_idx in range(3):
        year_data: Dict[str, int] = {}
        year_start = year_idx * 13
        actual_year = current_year - year_idx

        for cat_idx, category in enumerate(_expense_categories):
            value = expenses[year_start + cat_idx]
            year_data[category] = format_money(value)

            if category not in totals_by_category:
                totals_by_category[category] = 0
            totals_by_category[category] += value

        years.append({"year": actual_year, "expenses": year_data})

    # Format totals
    for category, total in totals_by_category.items():
        totals_by_category[category] = format_money(total)

    return {"years": years, "totals_by_category": totals_by_category}


def format_company_data(
    companies: List[Dict[str, Any]],
    map_size_x: int = 256,
    current_year: int = 1950,
    global_max_loan: int = 300000,
) -> List[Dict[str, Any]]:
    """Format company data with clean field names and values"""
    formatted_companies = []

    for company in companies:
        formatted = {
            "id": company.get("index", 0),
            "name": company.get("name", "").strip(),
            "president_name": company.get("president_name", "").strip(),
            "inaugurated_year": company.get("inaugurated_year", 1950),
            "is_ai": bool(company.get("is_ai", 0)),
        }

        # Generate company name if custom name is empty
        if not formatted["name"]:
            name_1 = company.get("name_1", 0)
            name_2 = company.get("name_2", 0)
            formatted["name"] = generate_company_name(name_1, name_2)

        # Generate president name if custom president name is empty
        if not formatted["president_name"]:
            president_name_1 = company.get("president_name_1", 0)
            president_name_2 = company.get("president_name_2", 0)
            if president_name_1 and president_name_2:
                formatted["president_name"] = generate_president_name(president_name_2)

        # Financial data - all as numeric values
        money = company.get("money", 0)
        money_fraction = company.get("money_fraction", 0)
        current_loan = company.get("current_loan", 0)
        max_loan = company.get("max_loan", 0)

        formatted["money"] = format_money(money, money_fraction)
        formatted["current_loan"] = format_money(current_loan)

        if max_loan == -9223372036854775808:  # COMPANY_MAX_LOAN_DEFAULT
            formatted["max_loan"] = global_max_loan  # Use actual value from save file
        else:
            formatted["max_loan"] = format_money(max_loan)

        formatted["net_worth"] = format_money(money - current_loan)

        # Company properties
        color = company.get("colour", 0)
        formatted["color"] = {"index": color, "name": get_color_name(color)}

        # Coordinates as x,y pairs
        location_of_HQ = company.get("location_of_HQ", 0)
        formatted["headquarters"] = format_coordinate(location_of_HQ, map_size_x)

        last_build_coordinate = company.get("last_build_coordinate", 0)
        formatted["last_build"] = format_coordinate(last_build_coordinate, map_size_x)

        # Bankruptcy info
        months_bankruptcy = company.get("months_of_bankruptcy", 0)
        if months_bankruptcy > 0:
            formatted["bankruptcy_months"] = months_bankruptcy

        # Format yearly expenses with categories
        yearly_expenses = company.get("yearly_expenses", [])
        if yearly_expenses:
            formatted["expenses"] = format_yearly_expenses(yearly_expenses, current_year)

        formatted_companies.append(formatted)

    return formatted_companies
