## build:
# docker build -t local/multiview-monitor .
#

FROM ubuntu:xenial

MAINTAINER MaZderMind <peter@mazdermind.de>

ENV DEBIAN_FRONTEND noninteractive

ENV uid 1000
ENV gid 1000

RUN useradd -m voc

RUN apt-get update && apt-get install -y --no-install-recommends \
	vim-tiny wget python3 ca-certificates \
	libx264-148 libvdpau1 libva1 libva-x11-1 libva-drm1 libxcb-shape0 \
	gstreamer1.0-tools libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-x \
	python3-gi gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 gir1.2-gstreamer-1.0 gir1.2-gtk-3.0 \
		&& apt-get clean

RUN wget --progress=bar:force https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -O /opt/ffmpeg-release-amd64-static.tar.xz && \
	cd /opt/ && tar -xvaf /opt/ffmpeg-release-amd64-static.tar.xz && \
	ln -s /opt/ffmpeg-4.1-64bit-static/ffmpeg /usr/bin/ffmpeg && \
	which ffmpeg

VOLUME ["/opt/multiview-monitor.ini"]
WORKDIR /opt/multiview-monitor
COPY . /opt/multiview-monitor/
COPY docker-ep.sh /opt/voctomix/

ENTRYPOINT ["/opt/voctomix/docker-ep.sh"]
