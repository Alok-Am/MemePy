import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
from pathlib import Path
import concurrent.futures

# Replace these paths with your actual folder locations
VIDEO_FOLDER = "D:/YT Vid sticher"
OUTPUT_FOLDER = "D:/YT Vid sticher/OP"
PROCESSED_FOLDER = "D:/YT Vid sticher/processed"  # New folder for processed clips
MIN_TOTAL_DURATION = 120  # 3 minutes in seconds

def get_video_duration(fileeName):
    try:
        clip = VideoFileClip(fileeName)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"Error processing {fileeName}: {str(e)}")
        return 0

def stitch_videos(video_clips, output_path):
    try:
        # Remove clips with None frames
        video_clips = [clip for clip in video_clips if clip.get_frame(0) is not None]

        if video_clips:
            sorted_clips = sorted(video_clips, key=lambda x: x.fps)
            final_clip = concatenate_videoclips(sorted_clips)
            final_clip.write_videofile(output_path, codec="libx264", fps=24)
            final_clip.close()
            print(f"Video created: {output_path}")

            # Create a subfolder within the "processed" folder
            output_folder_name = os.path.splitext(os.path.basename(output_path))[0]
            processed_subfolder = os.path.join(PROCESSED_FOLDER, output_folder_name)
            os.makedirs(processed_subfolder, exist_ok=True)

            # Move processed clips to the subfolder
            for clip in video_clips:
                clip_path = Path(clip.filename).as_posix()
                new_clip_name = f"{os.path.splitext(os.path.basename(clip_path))[0]}_{output_folder_name}.mp4"
                processed_clip_path = os.path.join(processed_subfolder, new_clip_name)
                os.rename(clip_path, processed_clip_path)
                print(f"Moved {clip_path} to {processed_clip_path}")
        else:
            print("No valid video clips to stitch.")
    except Exception as e:
        print(f"Error stitching videos: {str(e)}")

def process_video_clip(filename):
    video_pat = os.path.join(VIDEO_FOLDER, filename)
    video_path = Path(video_pat).as_posix()

    # Skip directories
    if os.path.isdir(video_path):
        return None

    print(video_path)

    try:
        video_clip = VideoFileClip(video_path)

        # Check if the clip has a valid frame before appending
        if video_clip.get_frame(0) is not None:
            return video_clip
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return None

def create_video():
    video_clips = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process video clips in parallel
        results = list(executor.map(process_video_clip, os.listdir(VIDEO_FOLDER)))

    # Filter out None results and append valid video clips
    video_clips.extend(filter(None, results))

    total_duration = sum(get_video_duration(video_path) for video_path in os.listdir(VIDEO_FOLDER) if video_path.endswith(".mp4"))

    if total_duration > MIN_TOTAL_DURATION and video_clips:
        # Print the list of video clips before stitching
        print("Video Clips to Stitch:", video_clips)

        output_path = os.path.join(OUTPUT_FOLDER, f"Output {datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
        stitch_videos(video_clips, output_path)
    else:
        print("Total duration is less than 2 minutes. No video created.")

if __name__ == "__main__":
    create_video()
