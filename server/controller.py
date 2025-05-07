from flask import Flask, Response
import subprocess
import os

app = Flask(__name__)

# Dictionary to keep track of running processes
processes = {}

OUTPUT_DIR_BASE = os.path.expanduser("/home/ubuntu/training/server/output")
INTERFACE = "ens3"

@app.route('/start/<string:session_id>/<string:speed>', methods=['GET'])
def start(session_id,speed):
    global processes
    global pcap_file
    global pcap2sec_file
    OUTPUT_DIR = os.path.expanduser(OUTPUT_DIR_BASE+speed)
    # Create output directory for this session
    session_dir = os.path.join(OUTPUT_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Define output file paths
    video_file = os.path.join(session_dir, "video.mp4")
    pcap_file = os.path.join(session_dir, "capture.pcap")
    pcap2sec_file = os.path.join(session_dir, "2sec.pcap")

    # Build the command strings
    ffmpeg_cmd = [
        "ffmpeg", "-f", "mpegts", "-timeout", "5000000", "-i", "rtp://localhost:8000",
        "-c", "copy", video_file
    ]

    tshark_cmd = [
        "tshark", "-i", INTERFACE, "-f", "udp port 8000",
        "-w", pcap_file
    ]

    try:
        # Start the processes in the background
        p_ffmpeg = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p_tshark = subprocess.Popen(tshark_cmd)

        # Store processes in dictionary
        processes[session_id] = (p_ffmpeg, p_tshark)
        return Response(f"Started recording with ID {session_id}", status=200)
    
    except Exception as e:
        return Response(f"Error starting processes: {e}", status=500)

@app.route('/stop', methods=['GET'])
def stop():
    global processes
    global pcap_file
    global pcap2sec_file
    # Stop all running processes
    for session_id, (p_ffmpeg, p_tshark) in processes.items():
        try:
            p_ffmpeg.terminate()
            p_tshark.terminate()
            editcap_cmd = ["editcap", "-i", "2", pcap_file, pcap2sec_file]
            subprocess.Popen(editcap_cmd)
        except Exception as e:
            print(f"Error terminating processes for {session_id}: {e}")

    processes.clear()
    return Response("Stopped all recordings", status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)