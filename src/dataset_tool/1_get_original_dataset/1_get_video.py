import cv2


def get_fourcc(output_file):
    """Determine the codec based on the file extension."""
    if output_file.endswith(".mp4"):
        return cv2.VideoWriter_fourcc(*"mp4v")  # Codec for MP4
    elif output_file.endswith(".avi"):
        return cv2.VideoWriter_fourcc(*"XVID")  # Codec for AVI
    else:
        raise ValueError("Unsupported file format. Use .mp4 or .avi")


def initialize_camera(camera_index, width, height, fps):
    """Open the video capture with specified parameters."""
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    return cap


def capture_video(
    camera_index=0, width=640, height=480, fps=30, output_file="output.avi"
):
    """Capture video from the specified camera and save to output file."""
    try:
        fourcc = get_fourcc(output_file)
    except ValueError as e:
        print(f"Error: {e}")
        return

    cap = initialize_camera(camera_index, width, height, fps)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Capture video until 'q' key is pressed
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        out.write(frame)
        cv2.imshow("Video Capture", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the capture and writer
    cap.release()
    out.release()
    cv2.destroyAllWindows()


# Example usage
if __name__ == "__main__":
    capture_video(
        camera_index=0, width=1280, height=720, fps=30, output_file="1_output.mp4"
    )

    # Uncomment for AVI format
    # capture_video(camera_index=0, width=1280, height=720, fps=30, output_file="output.avi")
