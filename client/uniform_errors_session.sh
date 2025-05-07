#!/bin/bash

SERVER_ADDRESS="192.168.154.10:8080"
SERVER_RTP="192.168.154.10:8000"
INPUT_PATH="/home/ubuntu/training/client/input"

for s in 0 20 50; do
  for y in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0; do
    echo "Applying tc rule with y = $y"
    tc qdisc add dev enp0s3 root netem loss ${y}% 
    for i in {1..10}; do
      BASE_SESSIONID=$(date +"%Y%m%d%H%M%S") 
      SESSIONID="${BASE_SESSIONID}"
      echo "...Starting repetition $i with SESSIONID: $SESSIONID"

      # Start session
      curl "http://$SERVER_ADDRESS/start/$SESSIONID/$s"
      sleep 2

      # Stream video via ffmpeg
      ~/bin/ffmpeg -re \
        -i ${INPUT_PATH}/webcam-10sec-${s}kmh-1.mp4 \
        -input_format mjpeg \
        -c copy \
        -f rtp_mpegts "rtp://${SERVER_RTP}?pkt_size=1316"

      # Stop session
      curl http://${SERVER_ADDRESS}/stop

      echo "Completed repetition $i"
      echo "Sleeping for 5 seconds..."
      sleep 5
    done
    tc qdisc del dev enp0s3 root
  done
done