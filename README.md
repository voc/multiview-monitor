# MultiView Monitor
This tool uses the ffmpeg `ebur128` Filter to produce realtime loudness charts for multiple streams, which are then mixed into a larger video-stream within gstreamer.
The resulting multiview of the loudness charts can now be streamed back to the streaming-server, which makes it easily available for people to check.

![Example Output](screenshot.jpg)

# Run with Docker
```
docker run --rm --volume $(pwd)/config-34c3.ini:/opt/multiview-monitor.ini mazdermind/multiview-monitor:latest
```

# Create and Publish new Docker-Image
```
docker build --tag mazdermind/multiview-monitor:latest .
docker push mazdermind/multiview-monitor:latest
```
