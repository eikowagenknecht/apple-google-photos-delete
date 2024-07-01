import csv
from datetime import datetime, timezone
import os

INPUT_IPHONE_FILE = "data/01x_iphone_photos.csv"
INPUT_GOOGLE_FILE = "data/02x_google_photos.csv"
OUTPUT_FILE = "data/03x_photos_to_delete.csv"

# Set of allowed image file extensions
ALLOWED_EXTENSIONS = {".jpeg", ".jpg", ".heic", ".png"}


def read_csv(file_path: str) -> list:
    with open(file_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        _ = next(csvreader)  # Skip header
        return [tuple(row) for row in csvreader]


def standardize_datetime(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str)
    dt_utc = dt.astimezone(timezone.utc).replace(microsecond=0)
    return dt_utc.isoformat()


def get_base_filename(file_path: str) -> str:
    return os.path.splitext(file_path)[0].lower()


def find_unique_rows(iphone_file: str, google_file: str) -> list:
    iphone_rows = read_csv(iphone_file)
    google_rows = read_csv(google_file)

    # Convert creationTime to datetime for comparison and lowercasing all entries
    iphone_base_filenames = [
        (get_base_filename(row[0]), standardize_datetime(row[1])) for row in iphone_rows
    ]
    google_rows_standardized = [
        (row[0], get_base_filename(row[0]), standardize_datetime(row[1]), row[2])
        for row in google_rows
        if os.path.splitext(row[0].lower())[1] in ALLOWED_EXTENSIONS
    ]

    iphone_dates = [datetime.fromisoformat(row[1]) for row in iphone_base_filenames]
    oldest_iphone_date = min(iphone_dates)

    unique_rows = [
        (orig_filename, creation_time, row_id)
        for orig_filename, base_filename, creation_time, row_id in google_rows_standardized
        if datetime.fromisoformat(creation_time) >= oldest_iphone_date
        and (base_filename, creation_time) not in iphone_base_filenames
    ]

    # Sort the unique rows by creationTime
    unique_rows.sort(key=lambda row: datetime.fromisoformat(row[1]))

    return unique_rows


def write_csv(output_file: str, data: list) -> None:
    with open(output_file, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["filename", "creationTime", "id"])
        for row in data:
            csvwriter.writerow(row)


def main():
    unique_rows = find_unique_rows(INPUT_IPHONE_FILE, INPUT_GOOGLE_FILE)
    write_csv(OUTPUT_FILE, unique_rows)


if __name__ == "__main__":
    main()
