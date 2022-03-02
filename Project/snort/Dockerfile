FROM linton/docker-snort
COPY . /root/Building-Networked-Systems-Security-EP2520/Project/snort/
WORKDIR /root/Building-Networked-Systems-Security-EP2520/Project/snort/
RUN alias runsnort="snort -A console -c /root/Building-Networked-Systems-Security-EP2520/Project/snort/etc/snort.conf -i enp1s0"
CMD [ "snort -A console -c /root/Building-Networked-Systems-Security-EP2520/Project/snort/etc/snort.conf -i enp1s0" ]