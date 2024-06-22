"""
Functions for querying languages-word types packs for the Scribe-Data CLI.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
"""

import csv
import json
from pathlib import Path
from typing import Optional

from .cli_utils import language_map

DATA_DIR = Path("scribe_data_json_export")


def query_data(
    language: str = None,
    word_type: str = None,
    output_dir: Optional[str] = None,
    overwrite: bool = False,
    output_type: Optional[str] = None,
) -> None:
    if not (language or word_type):
        raise ValueError(
            "You must provide either a --language (-l) or --word-type (-wt) option."
        )

    if output_dir:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if output_type == "json" or output_type is None:
            export_json(language, word_type, output_dir, overwrite)

        elif output_type in ["csv", "tsv"]:
            export_csv_or_tsv(language, word_type, output_dir, overwrite, output_type)

        else:
            raise ValueError(
                "Unsupported output type. Please use 'json', 'csv', or 'tsv'."
            )

    else:
        raise ValueError("Please specify an output directory using --output-dir (-od).")


def export_json(
    language: str, word_type: str, output_dir: Path, overwrite: bool
) -> None:
    normalized_language = language_map.get(language.lower())
    language_capitalized = language.capitalize()
    if not normalized_language:
        raise ValueError(f"Language '{language_capitalized}' is not recognized.")

    data_file = (
        DATA_DIR / normalized_language["language"].capitalize() / f"{word_type}.json"
    )

    if not data_file.exists():
        print(
            f"No data found for language '{normalized_language['language']}' and word type '{word_type}'."
        )
        return

    try:
        with data_file.open("r") as file:
            data = json.load(file)

    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading '{data_file}': {e}")
        return

    # Adjust the output directory for JSON exports.
    json_output_dir = (
        output_dir
        / "scribe_data_json_export"
        / normalized_language["language"].capitalize()
    )
    json_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = json_output_dir / f"{word_type}.json"
    if output_file.exists() and not overwrite:
        user_input = input(f"File '{output_file}' already exists. Overwrite? (y/n): ")
        if user_input.lower() != "y":
            print(f"Skipping {normalized_language['language']} - {word_type}")
            return

    try:
        with output_file.open("w") as file:
            json.dump(data, file, indent=2)
    except IOError as e:
        raise IOError(f"Error writing to '{output_file}': {e}") from e

    print(
        f"Data for language '{normalized_language['language']}' and word type '{word_type}' written to '{output_file}'"
    )


def export_csv_or_tsv(
    language: str, word_type: str, output_dir: Path, overwrite: bool, output_type: str
) -> None:
    normalized_language = language_map.get(language.lower())
    if not normalized_language:
        print(f"Language '{language}' is not recognized.")
        return

    data_file = (
        DATA_DIR / normalized_language["language"].capitalize() / f"{word_type}.json"
    )
    if not data_file.exists():
        print(
            f"No data found for language '{normalized_language['language']}' and word type '{word_type}'."
        )
        return

    try:
        with data_file.open("r") as file:
            data = json.load(file)

    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading '{data_file}': {e}")
        return

    if output_type == "csv":
        delimiter = ","
        file_extension = "csv"

    elif output_type == "tsv":
        delimiter = "\t"
        file_extension = "tsv"

    else:
        print(f"Unsupported output type '{output_type}'.")
        return

    # Adjust the output directory for CSV exports.
    csv_output_dir = (
        output_dir
        / "scribe_data_csv_export"
        / normalized_language["language"].capitalize()
    )
    csv_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = csv_output_dir / f"{word_type}.{file_extension}"
    if output_file.exists() and not overwrite:
        user_input = input(f"File '{output_file}' already exists. Overwrite? (y/n): ")
        if user_input.lower() != "y":
            print(f"Skipping {normalized_language['language']} - {word_type}")
            return

    try:
        with output_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=delimiter)
            if isinstance(data, dict):
                for key, value in data.items():
                    writer.writerow([key, value])

            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        writer.writerow(item.values())

                    else:
                        writer.writerow([item])

            else:
                print(f"Unsupported data format for {output_type} export.")

    except IOError as e:
        print(f"Error writing to '{output_file}': {e}")
        return

    print(
        f"Data for language '{normalized_language['language']}' and word type '{word_type}' written to '{output_file}'"
    )
