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
                 
    if video_clips:
        # Print the list of video clips before stitching
        print("Video Clips to Stitch:", video_clips)

        output_path = os.path.join(OUTPUT_FOLDER, f"output_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
        stitch_videos(video_clips, output_path)
        print(f"Video created: {output_path}")

if __name__ == "__main__":
    # Schedule the task to run every hour (adjust as needed)
    schedule.every().second.do(create_video)

    while True:
        schedule.run_pending()
        time.sleep(1)
