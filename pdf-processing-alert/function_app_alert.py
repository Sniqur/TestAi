import os
import logging
import requests
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
from azure.functions import FunctionApp

# Azure Function App Initialization
app = FunctionApp()

# Environment Variables
STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
SHARE_NAME = os.getenv("SHARE_NAME")
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Initialize Clients
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
document_analysis_client = DocumentAnalysisClient(
    endpoint=FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(FORM_RECOGNIZER_KEY),
)

def process_pdf_to_json(pdf_content):
    """Analyze PDF using Azure Form Recognizer and return JSON."""
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
    result = poller.result()
    extracted_data = []

    for page in result.pages:
        extracted_data.append({
            "page_number": page.page_number,
            "lines": [line.content for line in page.lines],
        })

    return json.dumps(extracted_data)

def send_discord_notification(message):
    """Send a notification to Discord."""
    if not DISCORD_WEBHOOK_URL:
        logging.error("Discord Webhook URL is not set.")
        return

    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info("Notification sent to Discord successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Discord notification: {e}")

@app.schedule(schedule="*/1 * * * *", arg_name="timer")
def process_files_timer_trigger(timer: func.TimerRequest) -> None:
    """Timer trigger to process PDF files and send notifications."""
    logging.info("Timer trigger function executed. Checking for files in Azure File Share.")

    try:
        # List files in Azure File Share
        share_client = ShareDirectoryClient.from_connection_string(
            conn_str=STORAGE_CONNECTION_STRING,
            share_name=SHARE_NAME,
            directory_path=""
        )
        files = [file.name for file in share_client.list_directories_and_files()]

        for file_name in files:
            if file_name.endswith(".pdf"):
                logging.info(f"Processing file: {file_name}")

                # Download PDF file
                file_client = ShareFileClient.from_connection_string(
                    conn_str=STORAGE_CONNECTION_STRING, share_name=SHARE_NAME, file_path=file_name
                )
                pdf_content = file_client.download_file().readall()

                # Process PDF to JSON
                json_result = process_pdf_to_json(pdf_content)

                # Upload JSON to Blob Storage
                blob_client = blob_service_client.get_blob_client(
                    container=BLOB_CONTAINER_NAME, blob=f"{os.path.splitext(file_name)[0]}.json"
                )
                blob_client.upload_blob(json_result, overwrite=True)

                logging.info(f"Successfully processed {file_name} and uploaded JSON result.")

                # Send Discord notification
                blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{os.path.splitext(file_name)[0]}.json"
                message = f"Processed file `{file_name}`. JSON uploaded to Blob Storage: {blob_url}"
                send_discord_notification(message)

    except Exception as e:
        logging.error(f"Error processing files: {e}")



# import os
# import logging
# import requests
# from azure.functions import FunctionApp
# import json
# import azure.functions as func

# app = FunctionApp()

# DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# def send_discord_notification(message):
#     payload = {"content": message}
#     response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
#     response.raise_for_status()

# def send_telegram_notification(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
#     response = requests.post(url, json=payload)
#     response.raise_for_status()

# @app.event_grid_trigger(arg_name="event")

# def notify_on_json_upload(event: func.EventGridEvent):
#     data = event.get_json()
#     blob_url = data.get("url", "")
#     if blob_url:
#         message = f"A new JSON file has been uploaded: {blob_url}"
#         try:
#             send_discord_notification(message)
#            # send_telegram_notification(message)
#             logging.info("Notifications sent successfully.")
#         except Exception as e:
#             logging.error(f"Failed to send notifications: {e}")