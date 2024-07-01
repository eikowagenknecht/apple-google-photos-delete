import csv
import requests
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
import logging
import webbrowser
import os

SECRET_FILE = "data/client_secret.json"
INPUT_FILE = "data/03x_photos_to_delete.csv"
OUTPUT_FILE = "data/04x_photos_to_delete.html"

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


def get_photo_infos(creds: google.auth.credentials.Credentials, photos: list) -> list:
    headers = {"Authorization": f"Bearer {creds.token}"}
    url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchGet"
    photo_infos = []

    for photo in photos:
        photo_id = photo["id"]
        response = requests.get(url, headers=headers, params={"mediaItemIds": photo_id})
        if response.status_code == 200:
            data = response.json()
            for mediaItemResult in data["mediaItemResults"]:
                if "mediaItem" in mediaItemResult:
                    photo_url = mediaItemResult["mediaItem"]["baseUrl"]
                    photo_infos.append(
                        {
                            "url": photo_url,
                            "filename": photo["filename"],
                            "creationTime": photo["creationTime"],
                        }
                    )
        else:
            logger.error(f"Failed to fetch photo with ID {photo_id}: {response.json()}")

    return photo_infos


def read_csv(filename: str) -> list:
    photos = []
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            photos.append(row)
    return photos


def generate_html(photo_infos: list, output_filename: str = OUTPUT_FILE):
    html_content = """
    <html>
    <head>
        <title>Photos</title>
        <style>
            .photo-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
            }
            .photo-item {
                text-align: center;
            }
            .photo-item img {
                max-width: 100%;
                height: auto;
            }
            .photo-item caption {
                font-size: small;
                color: gray;
            }
        </style>
    </head>
    <body>
        <h1>Photos that will be deleted</h1>
        <div class="photo-grid">
    """
    for photo in photo_infos:
        html_content += f"""
        <div class="photo-item">
            <img src="{photo["url"]}=w400" alt="Photo">
            <caption><em>{photo["filename"]}</em><br><small>{photo["creationTime"]}</small></caption>
        </div>
        """
    html_content += """
        </div>
    </body>
    </html>
    """

    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    logger.info(f"HTML file generated: {output_filename}")


def main():
    logger.info("Starting the script.")
    creds = authenticate()

    # Read photo IDs from CSV
    photos = read_csv(INPUT_FILE)

    # Fetch photo URLs
    photo_urls = get_photo_infos(creds, photos)

    # Generate HTML to display photos
    generate_html(photo_urls)

    output_url = f"file://{os.path.realpath(OUTPUT_FILE)}"
    # Open the generated HTML file in the default web browser
    logger.info("Opening the generated HTML file in the default web browser:")
    logger.info(f"{output_url}")
    webbrowser.open(output_url)


if __name__ == "__main__":
    main()
