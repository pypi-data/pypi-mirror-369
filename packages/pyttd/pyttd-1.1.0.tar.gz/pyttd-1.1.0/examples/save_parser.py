#!/usr/bin/env python3
"""
OpenTTD Save File Parser Example
===============================

This example demonstrates how to utilize pyttd for extracting data from OpenTTD save files.

Features:
- Loading and decompressing .sav files
- Company information
- Game metadata
- JSON output

Usage:
    python examples/save_file_parser.py [path/to/savefile.sav] [--output-dir OUTPUT_DIR]
"""

import os
import json
import argparse
from pathlib import Path

from pyttd import load_save_file


def parse_save_file_example(save_file_path: str, output_dir: str = ".", verbose: bool = False):
    """
    Parse a save file and optionally display the extracted data

    Args:
        save_file_path: Path to the save file
        output_dir: Directory to save JSON output
        verbose: Whether to print debug information
    """
    if verbose:
        print(f"Parsing save file: {save_file_path}")
        print()

    try:
        # Load and parse the save file
        game_data = load_save_file(save_file_path, silent=not verbose)

        if not game_data:
            if verbose:
                print("Failed to parse save file")
            return False

        if verbose:
            print("Save file loaded successfully!")
            print()

            # Display metadata
            display_metadata(game_data.get("meta", {}))

            # Display game information
            display_game_info(game_data.get("game", {}))

            # Display map information
            display_map_info(game_data.get("map", {}))

            # Display company information
            display_companies(game_data.get("companies", []))

        # Save to JSON file for inspection
        save_to_json(game_data, save_file_path, output_dir)

        return True

    except Exception as e:
        if verbose:
            print(f"Error parsing save file: {e}")
        return False


def display_metadata(meta: dict):
    """Display save file metadata"""
    print("METADATA")
    print("-" * 40)
    print(f"Filename: {meta.get('filename', 'Unknown')}")
    print(f"Save Version: {meta.get('save_version', 'Unknown')}")
    print(f"OpenTTD Version: {meta.get('openttd_version', 'Unknown')}")
    print(f"Current Date: {meta.get('current_date', 'Unknown')}")
    print(f"Current Year: {meta.get('current_year', 'Unknown')}")
    print()


def display_game_info(game: dict):
    """Display game information"""
    print("GAME")
    print("-" * 40)

    # Date
    date_data = game.get("date", {})
    if date_data:
        print(f"Calendar Date: {date_data.get('date', 'Unknown')}")
        print(f"Date Fraction: {date_data.get('date_fract', 'Unknown')}")
        print(f"Tick Counter: {date_data.get('tick_counter', 'Unknown'):,}")
        print(f"Economy Date: {date_data.get('economy_date', 'Unknown')}")

    # Economy
    economy_data = game.get("economy", {})
    if economy_data:
        print(f"Interest Rate: {economy_data.get('interest_rate', 'Unknown')}%")
        print(f"Inflation Prices: {economy_data.get('inflation_prices', 'Unknown')}")
        print(f"Inflation Payment: {economy_data.get('inflation_payment', 'Unknown')}")

    # Settings
    settings = game.get("settings", {})
    if settings:
        max_loan = settings.get("max_loan", "Unknown")
        if isinstance(max_loan, (int, float)):
            print(f"Max Loan: £{max_loan:,}")
        else:
            print(f"Max Loan: {max_loan}")

    print()


def display_map_info(map_data: dict):
    """Display map information"""
    print("MAP")
    print("-" * 40)

    width = map_data.get("dim_x", "Unknown")
    height = map_data.get("dim_y", "Unknown")

    print(f"Map Size: {width}x{height}")

    if isinstance(width, int) and isinstance(height, int):
        total_tiles = width * height
        print(f"Total Tiles: {total_tiles:,}")

    print()


def display_companies(companies: list):
    """Display company information"""
    print("COMPANY")
    print("-" * 40)

    if not companies:
        print("No companies found in save file")
        print()
        return

    print(f"Total Companies: {len(companies)}")
    print()

    for company in companies:
        display_single_company(company)


def display_single_company(company: dict):
    """Display information for a single company"""
    company_id = company.get("id", "?")
    name = company.get("name", "Unknown Company")
    president = company.get("president_name", "Unknown")

    print(f"Company {company_id}: {name}")
    print(f"   President: {president}")
    print(f"   Founded: {company.get('inaugurated_year', 'Unknown')}")
    print(f"   Type: {'AI' if company.get('is_ai', False) else 'Human'}")

    # Financials
    money = company.get("money", 0)
    loan = company.get("current_loan", 0)
    max_loan = company.get("max_loan", 0)
    net_worth = company.get("net_worth", 0)

    print(f"   Money: £{money:,}")
    print(f"   Current Loan: £{loan:,} / £{max_loan:,}")
    print(f"   Net Worth: £{net_worth:,}")

    # Colors
    color = company.get("color", {})
    if color:
        print(f"   Color: {color.get('name', 'Unknown')} (#{color.get('index', '?')})")

    # Locations
    headquarters = company.get("headquarters")
    if headquarters:
        print(f"   Headquarters: ({headquarters.get('x', '?')}, {headquarters.get('y', '?')})")
    else:
        print(f"   Headquarters: None")

    last_build = company.get("last_build", {})
    print(f"   Last Build: ({last_build.get('x', '?')}, {last_build.get('y', '?')})")

    # Expenses
    expenses = company.get("expenses", {})
    if expenses and "years" in expenses:
        years_data = expenses["years"]
        if years_data:
            current_year_expenses = years_data[0]["expenses"]
            total_expense = sum(v for v in current_year_expenses.values() if v > 0)
            total_revenue = abs(sum(v for v in current_year_expenses.values() if v < 0))
            profit = total_revenue - total_expense

            print(f"   Current Year Expenses: £{total_expense:,}")
            print(f"   Current Year Revenue: £{total_revenue:,}")
            print(f"   Current Year Profit: £{profit:,}")

    print()


def save_to_json(data: dict, original_path: str, output_dir: str = "."):
    """Save parsed data to JSON file"""
    # Create output filename
    input_path = Path(original_path)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_path = output_dir_path / f"{input_path.stem}.json"

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"JSON saved to: {output_path}")

    except Exception as e:
        print(f"Failed to save JSON file: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Parse OpenTTD save files and extract game data to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("save_file", nargs="?", help="Path to OpenTTD save file (.sav)")

    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Output directory for JSON file (default: current directory)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Print debug information")

    args = parser.parse_args()

    # Get save file path from args
    if args.save_file:
        save_file_path = args.save_file
    else:
        print("No save file specified.")
        print("Usage: python save_file_parser.py [path/to/savefile.sav] [--output-dir OUTPUT_DIR]")
        return 1

    # Check if file exists
    if not os.path.exists(save_file_path):
        print(f"Save file not found: {save_file_path}")
        return 1

    # Parse the save file
    success = parse_save_file_example(save_file_path, args.output_dir, args.verbose)

    if args.verbose:
        if success:
            print("Save file parsing completed successfully!")
        else:
            print("Save file parsing failed!")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
