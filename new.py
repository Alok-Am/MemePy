import os
import schedule
import time
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
import shutil

# Replace these paths with your actual folder locations
VIDEO_FOLDER = "D:/YT Vid sticher/IP"
OUTPUT_FOLDER = "D:/YT Vid sticher/OP"
MAX_DURATION = 120  # 2 minutes in seconds
MAX_ITERATIONS = 60  # Maximum number of iterations before exiting the loop

def get_video_duration(video_path):
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return 0

def stitch_videos(video_clips, output_path):
    # Remove clips with None frames
    video_clips = [clip for clip in video_clips if clip.get_frame(0) is not None]

    if video_clips:
        sorted_clips = sorted(video_clips, key=get_video_duration)
        final_clip = concatenate_videoclips(sorted_clips)
        final_clip.write_videofile(output_path, codec="libx264", fps=24)
        final_clip.close()

def create_video():
    video_clips = []

    for filename in os.listdir(VIDEO_FOLDER):
        if filename.endswith(".mp4"):
            video_path = os.path.join(VIDEO_FOLDER, filename)
            duration = get_video_duration(video_path)

            if duration > 0 and sum(map(get_video_duration, video_clips)) + duration <= MAX_DURATION:
                video_clip = VideoFileClip(video_path)
                # Check if the clip has a valid frame before appending
                if video_clip.get_frame(0) is not None:
                    video_clips.append(video_clip)
                    # Move the processed file to a subfolder with retries
                    processed_folder = os.path.join(VIDEO_FOLDER, "processed")
                    os.makedirs(processed_folder, exist_ok=True)
                    new_filename = f"{filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"

                    # Retry the move operation with a delay
                    for _ in range(3):  # Attempt move operation up to 3 times
                        try:
                            time.sleep(5)  # Add a delay before the move
                            shutil.move(video_path, os.path.join(processed_folder, new_filename))
                            break  # Move successful, exit the retry loop
                        except PermissionError as pe:
                            print(f"PermissionError: {pe}. Retrying move operation.")
                            time.sleep(5)  # Add a delay before retrying

    if len(video_clips) >= 2:  # Minimum 2 clips required for concatenation
        # Print the list of video clips before stitching
        print("Video Clips to Stitch:", video_clips)

        output_path = os.path.join(OUTPUT_FOLDER, f"output_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
        stitch_videos(video_clips, output_path)
        print(f"Video created: {output_path}")

# Run the script for a maximum number of iterations
for _ in range(MAX_ITERATIONS):
    create_video()
    time.sleep(60)  # Sleep for 1 minute between iterations
