#!/bin/bash
##
## entrypoint for the docker images

if [ ! -f /.dockerenv ] && [ ! -f /.dockerinit ]; then
	echo "WARNING: this script should be only run inside docker!!"
	exit 1
fi

if [ ! -z $gid ] && [ ! -z $uid ]; then
	groupmod -g $gid voc
	usermod -u $uid -g $gid voc

	# check if homedir is mounted
	if grep -q '/home/voc' /proc/mounts; then
		# homedir is mounted into the docker so don't touch the ownership of the files
		true
	else
		# fixup for changed uid and gid
		chown -R voc:voc /home/voc
	fi
fi

exec su -l -c "/opt/multiview-monitor/multiview-monitor.py -vv -i /opt/multiview-monitor.ini" voc
