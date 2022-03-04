

## Intrusion Detection System - Snort

Intrusion Detection System (IDS) is deployed using thhe open source IDS software named Snort. 
Snort is deployed as a container using Docker. The Docker image is available at emilstahl/snort on [Dockerhub](https://hub.docker.com/r/emilstahl/snort). 
Tu run the Snort image, execute the following command on Unix: $ docker run -it --rm --net=host emilstahl/snort /bin/bash where --net-host is needed to analyze traffic on
the host machines interfaces. 

Once in the container, the entrypoint is in the Snort directory where two directories are present, ./etc and ./rules. 
In ./etc the snort.conf is located where user can specify the subnet of which to analyze traffic. This is specified at line 45 and is predefined to ipvar HOME_NET 192.168.1.0/24. Furthermore, one can specify which IP range the EXTERNAL_NET shall correspond to, the default is the inverse of the HOME_NET, meaning all adresses except the HOME_NET.

#### N O T E: 
When deploying this image on another network then initially attended, make sure to update HOME_NET and EXTERNAL_NET accordingly.

In ./rules the local.rules file is located which includes site specific rules such as:

* ICMP requests originating from the EXTERNAL_NET which destination matching the HOME_NET
* FTP connection attempts
* SSH connections from the EXTERNAL_NET
* Potential bruteforce attacks due to three failed SSH authentications during the last 60 seconds originating from any IP-adress, including HOME_NET.

In ./rules/standard-rules/, various other rule files are located with the purpose of analyzing situations such as malicious port scannings, ddos attacks, SQL injections, dns lookups, and NTP. All .rules files are included in the ./etc/snort.conf file. 

To test and run the configuration, a .bashrc script is provided in ./.bashrc. 
The script must be sourced with the command 
```bash
source ./.bashrc
```
The current speci
