"""Turn carousel slides into a vertical slideshow video for an Instagram Reel.
Usage: python3 tools/slideshow.py out.mp4 slide0.jpg slide1.jpg ...  (3 seconds per slide)"""
import subprocess, sys, tempfile, os
def make(out, slides, secs=3):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for s in slides:
            f.write(f"file '{os.path.abspath(s)}'\nduration {secs}\n")
        f.write(f"file '{os.path.abspath(slides[-1])}'\n")
        lst = f.name
    subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i",lst,
        "-vf","scale=1080:1350,pad=1080:1920:0:285:color=0x0F0F0F,format=yuv420p,fps=30",
        "-c:v","libx264","-preset","veryfast","-crf","23","-movflags","+faststart",out], check=True)
    os.unlink(lst)
if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2:])
