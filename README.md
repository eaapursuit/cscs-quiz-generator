# CSCS Quiz Generator

A Python-based automated video generation tool that creates multiple-choice quiz videos using text, audio, and video overlays.

## 🛠️ Current Issues & TODOs

### 1️⃣ Large File Issue with GitHub  
- ❌ `minecraft_clip.mp4` exceeds GitHub's 100MB limit.  
- **Solution:** Use [Git LFS](https://git-lfs.github.com/) or exclude large files from commits.  
- **Fix:**  
  ```bash
  git lfs track "*.mp4"
  git add .gitattributes
  git commit -m "Track large files with Git LFS"
  git push origin main


### 3️⃣ FFmpeg Font Issue
- ❌ ffmpeg is throwing a duplicate font argument error.
- **Possible Fixes:**
Ensure fontfile or font isn't passed twice in drawtext.
Debug ffmpeg command by printing it before execution.

### 4️⃣ Missing or Untracked Files
- **Possible Fixes:**
chapter1_questions.json (ensure it's included)
.env (excluded, needs manual setup)
minecraft_clip.mp4 (exceeds GitHub limits, use LFS or external storage)


