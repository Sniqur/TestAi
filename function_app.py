import os
import logging
import azure.functions as func
import json
from azure.storage.blob import BlobServiceClient
from azure.storage.fileshare import ShareFileClient
from azure.storage.fileshare import ShareDirectoryClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.functions import FunctionApp
import requests

# if we can see this we can bypass compress stage 
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

def send_discord_notification(file_name):
    """
    Sends a notification to a Discord channel via webhook when a JSON file is added to Blob Storage.
    """
    try:
        message = {
            "content": f"🎉 A new JSON file has been added to Blob Storage: `{file_name}`"
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)

        if response.status_code == 204:
            logging.info(f"Successfully sent Discord notification for {file_name}.")
        else:
            logging.error(f"Failed to send Discord notification. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Error sending Discord notification: {e}")



def process_pdf_to_json(pdf_content):
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
    result = poller.result()
    extracted_data = []

    for page in result.pages:
        extracted_data.append({
            "page_number": page.page_number,
            "lines": [line.content for line in page.lines],
        })

    return json.dumps(extracted_data)



@app.schedule(schedule="*/1 * * * *", arg_name="timer")
def process_files_timer_trigger(timer: func.TimerRequest) -> None:
    logging.info("Timer trigger function executed. Checking for files in Azure File Share.")

    try:
        # List files in the Azure File Share
        share_client = ShareDirectoryClient.from_connection_string(
            conn_str=STORAGE_CONNECTION_STRING, 
            share_name=SHARE_NAME, 
            directory_path=""
        )
        files = [file.name for file in share_client.list_directories_and_files()]

        for file_name in files:
            if file_name.endswith(".pdf"):
                logging.info(f"Processing file: {file_name}")

                # Access PDF
                file_client = ShareFileClient.from_connection_string(
                    conn_str=STORAGE_CONNECTION_STRING, share_name=SHARE_NAME, file_path=file_name
                )
                pdf_content = file_client.download_file().readall()

                # Process PDF with Azure Form Recognizer
                json_result = process_pdf_to_json(pdf_content)

                # Upload JSON to Azure Blob Storage
                blob_client = blob_service_client.get_blob_client(
                    container=BLOB_CONTAINER_NAME, blob=f"{os.path.splitext(file_name)[0]}.json"
                )
                blob_client.upload_blob(json_result, overwrite=True)

                logging.info(f"Successfully processed {file_name} and uploaded JSON result.")


                send_discord_notification(f"{os.path.splitext(file_name)[0]}.json")


    except Exception as e:
        logging.error(f"Error processing files: {e}")