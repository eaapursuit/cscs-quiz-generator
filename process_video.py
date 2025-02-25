import os
import subprocess
import json
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.video.fx.FadeOut import FadeOut
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip
)

class VideoProcessor:
    def __init__(self, video_url: str):
        """Initialize the video processor with paths and URL."""
        self.video_url = video_url
        self.base_dir = os.getcwd()
        self.output_folder = os.path.join(self.base_dir, "processed_output")
        self.temp_folder = os.path.join(self.base_dir, "temp")
        self.audio_folder = os.path.join(self.base_dir, "audio_output")

        # File paths
        self.temp_video = os.path.join(self.temp_folder, "downloaded_video.mp4")
        self.output_audio = os.path.join(self.temp_folder, "merged_audio.mp3")
        self.final_output = os.path.join(self.output_folder, "final_video.mp4")
        self.audio_list_file = os.path.join(self.temp_folder, "audio_list.txt")

    def download_youtube_video(self) -> bool:
        """Download video from URL with progress reporting."""
        print(f"\n📥 Downloading video from URL...")
        try:
            # Create a YouTube object from URL
            import yt_dlp
            
            ydl_opts = {
                'format': 'best', # Gest best quality
                'outtmpl': self.temp_video,
                'progress_hooks': [
                    lambda d: print(f"Download Progress: {d.get('_percent_str', '0%')}", end='\r')
                ],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("🔍 Finding video stream...")
                ydl.download([self.video_url])

            if not os.path.exists(self.temp_video):
                raise Exception("Video file was not created")

            print("✅ Video downloaded successfully")
            return True
        
        except Exception as e:
            print(f"❌ Failed to download video: {str(e)}")
            return False

    def merge_audio_files(self, audio_files: list) -> bool:
        """Merge audio files with enhanced error handling."""
        print("\n🔊 Merging audio files...")
        try:
            # Create audio list file
            with open(self.audio_list_file, "w") as f:
                for audio in audio_files:
                    abs_path = os.path.abspath(audio)
                    f.write(f"file '{abs_path}'\n")
            
            cmd = f'ffmpeg -f concat -safe 0 -i "{self.audio_list_file}" -c copy "{self.output_audio}"'
            print(f"Running command: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Failed to merge audio files: {result.stderr}")
                return False
            
            print("✅ Audio files merged successfully")
            return True
        
        except Exception as e:
            print(f"❌ Error during audio merge: {e}")
            return False
        
    def create_final_video(self, questions_data):
        """Create video with text overlays and audio."""
        print("\n🎬 Creating final video with text overlays...")
        try:
            # Load the background video and audio
            video = VideoFileClip(self.temp_video)
            audio = AudioFileClip(self.output_audio)

            clips = []
            current_time = 0

            # Specify font path if needed
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
            
            for i, question in enumerate(questions_data):
                # Format the text
                question_text = f"Question {i + 1}:\n{question['question']}"
                options_text = "\n".join([f"{k}) {v}" for k, v in question['options'].items()])

                # Create text clips with proper fadein effect
                question_clip = TextClip(
                    question_text,
                    size=(video.w * 0.8, None),
                    font=font_path,
                    color='white',
                    stroke_width=2,
                    stroke_color='black',
                    method='caption'
                ).set_position('center').set_start(current_time).set_duration(38)
                
                # Add options text seperately
                options_clip = TextClip(
                    options_text,
                    size=(video.w * 0.8, None),
                    font=font_path,
                    color='white',
                    stroke_width=2,
                    stroke_color='black',
                    method='caption'
                ).set_position(('center', 250)).set_start(current_time).set_duration(38)
                
                clips.extend([question_clip, options_clip])
                current_time += 39

            # Create final composition
            final = CompositeVideoClip([video] + clips).set_audio(audio).set_duration(audio.duration)

            # Write the final video
            print("💾 Saving final video with overlays...")
            final.write_videofile(
                self.final_output,
                codec='libx264',
                audio_codec='aac',
                fps=30
            )

            # Clean up
            video.close()
            audio.close()
            for clip in clips:
                clip.close()
            print("✅ Video created with text overlays")

        except Exception as e:
                print(f"❌ Error creating video with overlays: {str(e)}")
                raise
            
    def run(self):
            """Run the complete video processing pipeline."""
            try:
                print("\n Starting Video Processing")
                print("===================================")

                # Create directories
                os.makedirs(self.output_folder, exist_ok=True)
                os.makedirs(self.temp_folder, exist_ok=True)
                print("✅ Processing directories created")

                # Download Youtube video
                if not self.download_youtube_video():
                    raise Exception("❌ Failed to download video")
                
                # Get audio files
                audio_files = [
                    os.path.join(self.audio_folder, f)
                    for f in os.listdir(self.audio_folder)
                    if f.endswith(".mp3")
                ]

                if not audio_files:
                    raise Exception("No MP3 files found in audio folder")

                print(f"✅ Found {len(audio_files)} audio files to process")
                
                # Merge audio files
                if not self.merge_audio_files(audio_files):
                    raise Exception("Failed to merge audio files")
                
                # Get merged audio duration
                cmd = f'ffprobe -i "{self.output_audio}" -show_entries format=duration -v quiet -of csv="p=0"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                total_duration = float(result.stdout.strip())
                print(f"📊 Total audio duration: {total_duration:.2f} seconds")

                # Load questions data for overlay
                with open('chapter1_questions.json', 'r') as f:
                    questions_data = json.load(f)

                # Create final video with overlays
                self.create_final_video(questions_data)

                print(f"\n✅ Final video created: {self.final_output}")
            
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
            finally:
                # Cleanup
                print("\n Cleaning up temporary files...")
                if os.path.exists(self.temp_folder):
                    for file in os.listdir(self.temp_folder):
                        try:
                            os.remove(os.path.join(self.temp_folder, file))
                        except:
                            pass
                    try:
                        os.rmdir(self.temp_folder)
                    except:
                        pass
                print("✅ Temporary files cleaned up")
    
# def main():
#     #Replace with video URL
#     video_url = "https://youtu.be/nNTxtEI9dZw?si=qPmXciccTkEWIlge"
#     processor = VideoProcessor(video_url)
#     processor.run()

if __name__ == "__main__":
    main()