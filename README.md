# Training scripts

## Preparation
* Edit server/controller.py, line 10 with the correct path to store results
* Edit server/extract_stats.py lines 10, 11, 12 with the correct paths. Line 11 should point
to the videos used as input. Line 12 should point to the ffmpeg folder (built from sources)
* In the client folder edit script files, lines 3 and 4 with the correct address. The
first address is the address in which the controller scripts listens and the second is
the address in which ffmpeg expects packets
* In the client folder edit script files line 5 to include the correct folder
* Install the server dependencies
```
python3 -m pip install flask
```

## Execution
In the server side go to the `training\server` folder and execute

```
python3 controller.py
```

If you receive this error `tshark: Couldn't run /usr/bin/dumpcap in child process: Permission denied` execute following

```
sudo usermod -aG wireshark $USER
```

Logout and login again

