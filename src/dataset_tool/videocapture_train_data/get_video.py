import cv2


def capture_video(
    camera_index=0,
    width=640,
    height=480,
    fps=30,
    output_file="output.avi",
):
    # Determine the codec based on the file extension
    if output_file.endswith(".mp4"):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for MP4
    elif output_file.endswith(".avi"):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Codec for AVI
    else:
        print("Error: Unsupported file format. Use .mp4 or .avi")
        return

    # Open the video capture
    cap = cv2.VideoCapture(camera_index)

    # Set camera parameters
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)

    # Create a VideoWriter object
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Capture video until 'q' key is pressed
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Write the frame to the output file
        out.write(frame)

        # Display the frame
        cv2.imshow("Video Capture", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the capture and writer
    cap.release()
    out.release()
    cv2.destroyAllWindows()


# Example usage for MP4
capture_video(
    camera_index=0,
    width=1280,
    height=720,
    fps=30,
    output_file="output.mp4",
)

# Example usage for AVI
# capture_video(
#     camera_index=0,
#     width=1280,
#     height=720,
#     fps=30,
#     output_file="output.avi",
# )
