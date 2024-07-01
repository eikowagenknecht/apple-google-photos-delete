import csv
import time
import webbrowser
import requests
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
import logging

SECRET_FILE = "data/client_secret.json"
INPUT_FILE = "data/03x_photos_to_delete.csv"

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


def read_csv(filename: str) -> list:
    photos = []
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            photos.append(row)
    return photos


def get_photo_urls(creds: google.auth.credentials.Credentials, photos: list) -> list:
    headers = {"Authorization": f"Bearer {creds.token}"}
    url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchGet"
    photo_urls = []

    for photo in photos:
        photo_id = photo["id"]
        response = requests.get(url, headers=headers, params={"mediaItemIds": photo_id})
        if response.status_code == 200:
            data = response.json()
            for mediaItemResult in data["mediaItemResults"]:
                if "mediaItem" in mediaItemResult:
                    photo_url = mediaItemResult["mediaItem"]["productUrl"]
                    photo_urls.append(
                        {
                            "id": photo_id,
                            "url": photo_url,
                            "filename": photo["filename"],
                            "creationTime": photo["creationTime"],
                        }
                    )
        else:
            logger.error(f"Failed to fetch photo with ID {photo_id}: {response.json()}")

    return photo_urls


def photo_exists(creds: google.auth.credentials.Credentials, photo_id: str) -> bool:
    headers = {"Authorization": f"Bearer {creds.token}"}
    url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{photo_id}"
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def open_photo_and_wait_for_deletion(creds: google.auth.credentials.Credentials, photo):
    customURL = f"{photo['url']}#delete={photo['id']}"
    logger.info(
        f"Opening photo: {photo['filename']} in browser with URL fragment ({customURL})"
    )

    webbrowser.open(customURL)
    while True:
        time.sleep(1)  # Wait for 1 second
        if not photo_exists(creds, photo["id"]):
            logger.info(f"Photo {photo['filename']} has been deleted.")
            break
        else:
            logger.info(
                f"Photo {photo['filename']} still exists. Please delete it to continue..."
            )


def open_photos_in_browser(photo_urls: list):
    for photo in photo_urls:
        logger.info(f"Opening photo: {photo['filename']} in browser.")
        webbrowser.open(photo["url"])


def display_photos_for_deletion(photos: list):
    logger.info("The following photos will be deleted:")
    for photo in photos:
        print(
            f"ID: {photo['id']}, Filename: {photo['filename']}, Creation Time: {photo['creationTime']}"
        )
    confirm = input("Do you want to continue with the deletion? (yes/no): ")
    if confirm.lower() != "yes":
        logger.info("Deletion aborted by the user.")
        exit()


def main():
    logger.info("Starting the script.")
    creds = authenticate()

    # Read photo IDs from CSV
    photos = read_csv(INPUT_FILE)
    display_photos_for_deletion(photos)

    # Fetch photo URLs
    photo_urls = get_photo_urls(creds, photos)

    # Open photos one by one in browser and wait for deletion
    for photo in photo_urls:
        open_photo_and_wait_for_deletion(creds, photo)

    logger.info("Script finished successfully.")


if __name__ == "__main__":
    main()
