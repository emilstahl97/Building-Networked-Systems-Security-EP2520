# Instructions to run snort:

* To run snort: $ docker run -it --rm --net=host emilstahl/snort /bin/bash
* To change HOME_NET: vim etc/snort.conf on line 45
* update: To make snort run correctly atm, set EXTERNAL_NET equal to **any** on line 50 in snort.conf
* vim .bashrc
* change interface at bottom of file in alias of **runsnort** and **testsnort**
* source .bashrc
* runsnort 
