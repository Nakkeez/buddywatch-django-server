from django.core.files.base import ContentFile
import uuid
import cv2
import os


def generate_and_save_thumbnail(video, instance):
    """
    Capture the first frame from video with OpenCV and save the frame as
    thumbnail to Video instance
    """
    # Save the video to a temporary file that OpenCV can read
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as temp_video_file:
        for chunk in video.chunks():
            temp_video_file.write(chunk)

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
