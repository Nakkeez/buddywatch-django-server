from django.core.files.base import ContentFile
import io
import os
import cv2


def generate_and_save_thumbnail(video_name, instance):
    """Capture the first frame from video with OpenCV and save the frame as thumbnail to Video instance"""
    video_path = os.path.join(__file__, '..', '..', 'media', video_name)
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()

    if ret:
        # Convert the image to PNG format in memory
        is_success, buffer = cv2.imencode(".png", frame)
        if is_success:
            # Convert to bytes and then to a Django ContentFile
            io_buf = io.BytesIO(buffer)
            thumbnail = ContentFile(io_buf.getvalue())
            # Save thumbnail to the model's thumbnail field
            instance.thumbnail.save(f"{instance.pk}_thumbnail.png", thumbnail, save=True)

    cap.release()
    cv2.destroyAllWindows()
