import os
import subprocess
import re
from pathlib import Path
import json


for s in ["0","20","50"]:
    # Define the base directory
    base_dir = f"/home/ubuntu/training/server/output{s}"
    reference_video = f"/home/ubuntu/training/client/input/webcam-10sec-{s}kmh-1.mp4"
    ffmpeg_path =  "/home/ubuntu/bin/ffmpeg"
    print("Extracting stats from:", base_dir)
    index=0
    timestamp=0
    # Walk through each folder in the base directory
    for root, dirs, files in os.walk(base_dir):
        trace_data = {
            "QoE": None,
            "timestamp":0
        }
        mIndex = 8
        folder_name=""
        for file in files:
            
            if file.startswith("2sec") and file.endswith(".pcap"):
                folder_name = os.path.basename(root)
                timestamp = int(folder_name)
                pcap_path = os.path.join(root, file)
                print(f"Processing: {pcap_path}")

                # Construct the tshark command
                cmd = [
                    "tshark",
                    "-r", pcap_path,
                    "-d", "udp.port==8000,rtp",
                    "-q",
                    "-z", "rtp,streams",
                    "-z", "io,stat,0"
                ]

                try:
                    # Run the command and capture the output
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    output = result.stdout
                    print(output)
                    lines = output.split("\n")
                    words = lines[12].split(" ")
                    filtered_arr = [s for s in words if s.strip()]
                    bytes = int(filtered_arr[7])*8/1000
                    words = lines[16].split(" ")
                    filtered_arr = [s for s in words if s.strip()]
                    #loss = float(filtered_arr[10].strip("()%"))
                    plost = filtered_arr[10]
                    #loss = filtered_arr[11]
                    loss = float(filtered_arr[11].strip("()%"))
                    mean = float(filtered_arr[16])
                    formatted_mean = "{:.3f}".format(mean)
                    speed = s #get_speed()
                    print(round(bytes/2, 1), "\t\t", plost, loss, "\t", formatted_mean, "\t\t", speed)
                    measurement = {}
                    measurement["throughput"] = round(bytes/2, 1)
                    measurement["packets_lost"] = float(plost)
                    measurement["packet_loss_rate"] = loss
                    measurement["jitter"] = float(formatted_mean)
                    measurement["speed"] = speed
                    trace_data[str(timestamp-mIndex)]=measurement
                    mIndex=mIndex-2
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {pcap_path}: {e.stderr}")
        # Check for the video.mp4 file in the current directory
        video_path = os.path.join(root, "video.mp4")

        if os.path.exists(video_path):
            print(f"Calculating VMAF for: {video_path}")

            # Construct the ffmpeg command
            ffmpeg_cmd = [
                str(ffmpeg_path),
                "-i", video_path,
                "-i", str(reference_video),
                "-lavfi", "libvmaf=log_path=/dev/null",
                "-f", "null", "-"
            ]

            try:
                # Run the ffmpeg command and capture the output
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
                match = re.search(r"VMAF score: ([0-9.]+)", result.stderr)
                if match:
                    
                    vmaf_score = float(match.group(1))
                    print(f"VMAF Score: {vmaf_score}")
                    trace_data["QoE"] = vmaf_score
                    trace_data["timestamp"] = timestamp
                    filename = folder_name + ".json"
                    output_file = base_dir + "/" +   filename
                    with open(output_file, "w") as f:
                        json.dump(trace_data, f, indent=4)
                    index=index+1
            except subprocess.CalledProcessError as e:
                print(f"Error calculating VMAF for {video_path}: {e.stderr}")
        else:
            print(video_path, " does not exist")

    

