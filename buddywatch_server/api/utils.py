from django.core.files.base import ContentFile
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential
from django.conf import settings
import uuid
import cv2
import os


def generate_and_save_thumbnail(video_url, instance):
    """
    Capture the first frame from video with OpenCV and save the frame as
    thumbnail to Video instance
    """
    # Configure Azure credentials
    credentials = ClientSecretCredential(
        client_id=settings.CLIENT_ID,
        tenant_id=settings.TENANT_ID,
        client_secret=settings.CLIENT_SECRET
    )

    # Connect to Azure Blob Storage and download the video
    blob_service_client = BlobServiceClient(account_url=settings.STORAGE_URL, credential=credentials)
    blob_client = blob_service_client.get_blob_client(container=settings.CONTAINER_NAME, blob=video_url)
    blob_data = blob_client.download_blob()
    blob_data = blob_data.readall()

    # Save the video to a temporary file that OpenCV can read
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as temp_video_file:
        temp_video_file.write(blob_data)

    # Start capturing the video
    cap = cv2.VideoCapture(temp_video_path)
    # Read first frame of the video
    ret, frame = cap.read()

    if ret:
        # Convert the frame to PNG format in memory
        is_success, buffer = cv2.imencode(".png", frame)
        if is_success:
            # Convert to bytes and then to a Django ContentFile
            thumbnail = ContentFile(buffer.tobytes())
            # Generate a unique ID for the thumbnail
            unique_id = uuid.uuid4()
            # Save thumbnail to the model's thumbnail field
            instance.thumbnail.save(f'{unique_id}_thumbnail.png', thumbnail, save=True)

    cap.release()

    try:
        os.remove(temp_video_path)
    except Exception as e:
        print(f"Error while deleting temporary video file: {e}")
