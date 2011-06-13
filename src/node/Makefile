default:
	
install:
	cp *.py ${DESTDIR}/opt/node
	mkdir ${DESTDIR}/opt/node/nodetools
	cp nodetools/*.py ${DESTDIR}/opt/node/nodetools
	mkdir ${DESTDIR}/opt/node/queue
	mkdir ${DESTDIR}/opt/node/etc
	cp nodetools/prodconfig.py ${DESTDIR}/opt/node/nodetools/config.py
	echo "<queue />" > ${DESTDIR}/opt/node/queue/Queue.xml
clean:
	
	