import os
import subprocess
import time
from typing import Dict, Tuple, Optional

class AudioDurationChecker:
    def __init__(self):
        self.audio_folder = "audio_output"
        self.total_files_processed = 0
        self.start_time = time.time()
    
    def verify_ffprobe_installation(self) -> bool:
        """Verify that ffprobe is installed and accessible."""
        try:
            subprocess.run(['ffprobe', '-version'], capture_output=True)
            print("✅ ffprobe installation verified")
            return True
        except FileNotFoundError:
            print("❌ ffprobe not found. Please install ffmpeg/ffprobe to continue.")
            return False
    
    def verify_audio_folder(self) -> bool:
        """Verify audio folder exists and contains MP3 files."""
        if not os.path.exists(self.audio_folder):
            print(f"❌ Audio folder not found: {self.audio_folder}")
            print("Please ensure the audio_output folder exists in the same directory as this script.")
            return False
        
        mp3_files = [f for f in os.listdir(self.audio_folder) if f.endswith('.mp3')]
        if not mp3_files:
            print("❌ No MP3 files found in audio folder")
            print("Please ensure your audio files are in MP3 format and located in the audio_output folder.")
            return False
        
        print(f"✅ Found {len(mp3_files)} MP3 files in {self.audio_folder}")
        return True
    
    def get_audio_duration(self, file_path: str) -> Optional[float]:
        """Get duration of a single audio fioe with enhanced error handling."""
        full_path = os.path.join(self.audio_folder, file_path)

        #Verify file exists and is accessible
        if not os.path.exists(full_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        #Check file size
        file_size = os.path.getsize(full_path)
        if file_size == 0:
            print(f"Warning: {file_path} is empty (0 bytes)")
            return None
        
        try:
            cmd = f'ffprobe -i "{full_path}" -show_entries format=duration -v quiet -of csv="p=0"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ ffprobe failed for {file_path}")
                print(f"Error: {result.stderr}")
                return None
            
            duration = float(result.stdout.strip())
            self.total_files_processed += 1
            return duration
        
        except ValueError as e:
            print("f❌ Invalid duration value for {file_path}: {e}")
        except Exception as e:
            print("f❌ Unexpected error processing {file_path}: {e}")
        
        return None
    
    def check_audio_durations(self) -> Tuple[float, Dict[str, float]]:
        """Check durations of all MP3 files with progress reporting."""
        print("\n🔍 Starting Audio Duration Analysis")
        print("================================")
        
        # Initial verifications
        if not self.verify_ffprobe_installation() or not self.verify_audio_folder():
            return 0.0, {}

        # Get a list of all audio files and sort them
        audio_files = sorted([f for f in os.listdir(self.audio_folder) if f.endswith(".mp3")])
        total_files = len(audio_files)

        print("\n📊 Processing {total_files} audio files...")
        print("--------------------------------")

        file_durations = {}
        for index, audio_file in enumerate(audio_files, 1):
            print(f"\nProcessing file {index}/{total_files}: {audio_file}")
            duration = self.get_audio_duration(audio_file)

            if duration is not None:
                file_durations[audio_file] = duration
                print(f"✅ Duration: {duration:.2f} seconds")
            else:
                print(f"⚠️ Failed to get duration for {audio_file}")

        # Calculate and display summary
        total_duration = sum(file_durations.values())
        elapsed_time = time.time() - self.start_time

        print("\n📈 Analysis Summary")
        print("--------------------------------")
        print(f"Total files processed: {self.total_files_processed}/{total_files}")
        print(f"Successfully processed: {len(file_durations)} files")
        print(f"Failed to process: {total_files - len(file_durations)} files")
        print(f"Total audio duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        print(f"Analysis completed in: {elapsed_time:.2f} seconds")

        return total_duration, file_durations

def main():
    try:
        checker = AudioDurationChecker()
        total_duration, durations = checker.check_audio_durations()

        if durations:
            print("\n✅ Analysis completed successfully")
        else:
            print("\n⚠️ Analysis completed with errors")

    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        print("Please check the error message and try again.")

if __name__ == "__main__":
    main()
