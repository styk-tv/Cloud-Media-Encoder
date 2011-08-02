default:
	
install:
	mkdir -p ${DESTDIR}/opt/node/nodetools
	mkdir ${DESTDIR}/opt/node/modules
	cp *.py ${DESTDIR}/opt/node
	cp nodetools/*.py ${DESTDIR}/opt/node/nodetools
	cp modules/*.py ${DESTDIR}/opt/node/modules
	mkdir ${DESTDIR}/opt/node/queue
	mkdir ${DESTDIR}/opt/node/etc
	cp extra/Encoders.xml ${DESTDIR}/opt/node/etc
	cp nodetools/prodconfig.py ${DESTDIR}/opt/node/nodetools/config.py
	echo "<queue />" > ${DESTDIR}/opt/node/queue/Queue.xml
	mkdir -p ${DESTDIR}/etc/udev/rules.d
	cp extra/*.rules ${DESTDIR}/etc/udev/rules.d
gitinstall:
	ln -s ${PWD} ${DESTDIR}/opt/node
	mkdir -p ${DESTDIR}/opt/node/queue 
	echo "<queue />" > ${DESTDIR}/opt/node/queue/Queue.xml
	chmod ugo+x ${DESTDIR}/opt/node/debian/init.d
	ln -s ${DESTDIR}/opt/node/extra ${DESTDIR}/opt/node/etc
	ln -s ${DESTDIR}/opt/node/extra/80-nodedisk.rules ${DESTDIR}/etc/udev/rules.d
	ln -s ${DESTDIR}/opt/node/nodetools/prodconfig.py ${DESTDIR}/opt/node/nodetools/config.py
	ln -s ${DESTDIR}/opt/node/debian/init.d ${DESTDIR}/etc/init.d/node-encoding
	rm -f ${DESTDIR}/etc/rc.local
	ln -s ${DESTDIR}/opt/node/console.py ${DESTDIR}/etc/rc.local
	chown -R node /var/www/volumes
	mkdir -p /home/node/.ssh
	ssh-keygen -q -N '' -t rsa /home/node/.ssh/id_rsa
	touch /home/node/.ssh/authorized_keys
	chown -R /home/node/.ssh
	chmod 0600 /home/node/.ssh/*
	
clean:
	
	