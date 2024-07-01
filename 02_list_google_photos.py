import requests
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
import logging
import csv

SECRET_FILE = "data/client_secret.json"
OUTPUT_FILE = "data/02x_google_photos.csv"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authenticate() -> google.auth.credentials.Credentials:
    SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
    flow = InstalledAppFlow.from_client_secrets_file(SECRET_FILE, SCOPES)
    logger.info("Opening web browser for authentication...")
    creds = flow.run_local_server(port=0)
    logger.info("Authentication successful.")
    return creds


def get_photos(creds: google.auth.credentials.Credentials, pageSize: int = 100) -> list:
    headers = {"Authorization": f"Bearer {creds.token}"}
    url = f"https://photoslibrary.googleapis.com/v1/mediaItems?pageSize={pageSize}"
    photos = []
    total_photos_fetched = 0
    page_number = 1

    while url:
        # logger.info(f"URL: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            raise Exception(
                "Access forbidden: Ensure the API is enabled, you are a test user, and you have the necessary permissions."
            )
        elif response.status_code != 200:
            raise Exception("Error fetching photos: ", response.json())
        data = response.json()

        new_photos = data.get("mediaItems", [])
        photos.extend(new_photos)
        total_photos_fetched += len(new_photos)
        logger.info(
            f"Fetched {total_photos_fetched} photos so far from {page_number} page(s)."
        )
        url = data.get("nextPageToken", None)
        if url:
            url = f"https://photoslibrary.googleapis.com/v1/mediaItems?pageToken={url}&pageSize={pageSize}"
            page_number += 1
    logger.info("Finished fetching photos.")
    return photos


def save_to_csv(photo_info: list, filename: str = OUTPUT_FILE):
    logger.info(f"Saving data to {filename}.")
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["filename", "creationTime", "id"])
        writer.writeheader()
        for photo in photo_info:
            writer.writerow(photo)
    logger.info(f"Data successfully saved to {filename}.")


def main():
    logger.info("Starting the script.")
    creds = authenticate()
    photos = get_photos(creds)

    # Extract filenames and creation dates
    logger.info("Extracting filenames, creation dates and ids.")
    photo_info = [
        {
            "filename": photo["filename"],
            "creationTime": photo["mediaMetadata"]["creationTime"],
            "id": photo["id"],
        }
        for photo in photos
    ]

    # Sort by creation date
    logger.info("Sorting photos by creation date.")
    photo_info.sort(key=lambda x: x["creationTime"])

    # Save sorted filenames to CSV
    save_to_csv(photo_info)
    logger.info("Script finished successfully.")


if __name__ == "__main__":
    main()
