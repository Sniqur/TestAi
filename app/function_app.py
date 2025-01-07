import os
import logging
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.fileshare import ShareFileClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.fileshare import ShareDirectoryClient
import requests
from os.path import basename
# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Environment Variables
STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
SHARE_NAME = os.getenv("SHARE_NAME")
TODO_CONTAINER = "to-do"  # Blob Container for new files
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")  # Blob Container for processed files
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Azure Clients
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
document_analysis_client = DocumentAnalysisClient(
    endpoint=FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(FORM_RECOGNIZER_KEY),
)

# Utility Functions
def sanitize_blob_name(blob_name):
    """Returns the original file name unchanged"""
    logging.info(f"Using original blob name: {blob_name}")
    return blob_name

################################ Send Notifications ##############################

def send_discord_notification(file_name):
    """Send a Discord notification."""
    try:
        message = {"content": f"🎉 JSON file added to Done container: `{file_name}`"}
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        if response.status_code == 204:
            logging.info(f"Discord notification sent for {file_name}")
        else:
            logging.error(f"Failed to send Discord notification: {response.status_code}")
    except Exception as e:
        logging.error("Error sending Discord notification", exc_info=True)


def send_telegram_notification(file_name):
    """Send a Telegram notification."""
    try:
        message = f"🎉 JSON file added to Done container: `{file_name}`"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Telegram notification sent for {file_name}")
        else:
            logging.error(f"Failed to send Telegram notification: {response.status_code}")
    except Exception as e:
        logging.error("Error sending Telegram notification", exc_info=True)

################################ Process PDF to JSON ##############################

def process_pdf_to_json(pdf_content):
    """Convert PDF content to JSON."""
    try:
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
        result = poller.result()
        extracted_data = [
            {"page_number": page.page_number, "lines": [line.content for line in page.lines]}
            for page in result.pages
        ]
        logging.info("PDF processed successfully")
        return json.dumps(extracted_data)
    except Exception as e:
        logging.error("Error processing PDF to JSON", exc_info=True)
        return None


app = func.FunctionApp()

@app.function_name(name="blobTriggerFunctionOCR")
@app.blob_trigger(arg_name="myblob", path=f"{TODO_CONTAINER}/{{name}}", connection="AzureWebJobsStorage")
def main(myblob: func.InputStream):
    """Blob Trigger Function to process files in `to-do`."""
    try:
        file_name = myblob.name
        logging.info(f"Processing file: {file_name}")

        # Access PDF
        blob_client = BlobClient.from_connection_string(
            STORAGE_CONNECTION_STRING, container_name=TODO_CONTAINER, blob_name=basename(file_name)
        )
        pdf_content = blob_client.download_blob().readall()

        # Process PDF with Azure Form Recognizer
        json_result = process_pdf_to_json(pdf_content)
        if not json_result:
            logging.error(f"Failed to process PDF: {file_name}")
            return

        # Upload JSON to Blob Storage
        json_file_name = f"{os.path.splitext(file_name)[0]}.json"
        json_blob_client = BlobClient.from_connection_string(
            STORAGE_CONNECTION_STRING, container_name=BLOB_CONTAINER_NAME, blob_name=basename(json_file_name)
        )
        json_blob_client.upload_blob(json_result, overwrite=True)


        logging.info(f"Successfully processed {file_name} and uploaded JSON result")
    except Exception as e:
        logging.error(f"Error processing file {file_name}", exc_info=True)





@app.function_name(name="blobTriggerFunctionAlert")
@app.blob_trigger(arg_name="myblob", path=f"{BLOB_CONTAINER_NAME}/{{name}}", connection="AzureWebJobsStorage")
def main(myblob: func.InputStream):
    """Blob Trigger Function to process files in `to-do`."""
    try:
        file_name = myblob.name
        logging.info(f"Processing file: {file_name}")


        json_file = f"{os.path.splitext(file_name)[0]}.json"
        json_file_name = basename(json_file)

        send_discord_notification(json_file_name)
        send_telegram_notification(json_file_name)
        logging.info(f"Successfully sent notification  {file_name}")
    except Exception as e:
        logging.error(f"Error processing file {file_name}", exc_info=True)
