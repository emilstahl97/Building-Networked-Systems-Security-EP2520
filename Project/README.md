# ACME Network Setup

For more clear explanation, we consider that our internal network where everything is set up is the **192.168.9.0/24** network and the IP of the server for the containers is **192.168.9.10**. Also, the FreeIPA server, i.e the container that is going to run on the host pc, is going to be named **server.final.test** and the domain is of course final.test. The host machine runs UBUNTU 20.4 but since we run almost everything in containers, few things should change in the configurations below, which will be noted if there is a difference in other Unix distributions.

## SETTING UP THE ROUTER WITH DD-WRT:

We flush the routers and we install dd+wrt. THOMAS ADD STUFF HERE
After we set everything up and change the networks provided, we need to go to **services->wireless** security and pick **wpa2-eap**, add the IP 1**92.168.9.10** in the FreeRadius one (leave the default port and default encryption method) and for the secret use.

## DOCKER-ENGINE AND DOCKER COMPOSE

We install both so anyone can either chose to install every container either with docker run commands ( like we did ) or use a Dockerfile and use the docker compose up command. To install docker engine first go to the docker docs official site and follow the instructions for your distributions.

For Ubuntu Linux we do:

```bash 
$ sudo apt-get update

$ sudo apt-get install ca-certificates curl gnupg lsb-release

$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-
archive-keyring.gpg] https://download.docker.com/linux/ubuntu \ $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

$ sudo apt-get update

$ sudo apt-get install docker-ce docker-ce-cli containerd.io
```
These commands should have docker engine running: 
Confirm with
```bash 
$ docker run hello-world
```

To install docker-compose:
```bash 
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker- compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

$ sudo chmod +x /usr/local/bin/docker-compose

$sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

And to confirm you should get a result with the command:

```bash
docker-compose --version
```

## FREEIPA

Now that we have installed docker, we need to set up FreeIpa and Nextcloud. Before we do that though, we need to configure some details. First, in the ```bash /etc/hosts``` file we need to add the following entries:

```bash 192.168.9.10 server.final.test ipa-server```
```bash 172.17.0.1 host.docker.internal``` (needed to have communication with containers in Linux distribs)
```bash 192.168.9.1 <name-of-your-router>``` ( not really needed but just in case for later )

Also, if we consider that our PWD is ```bash /home/myuser``` we create a new directory for the freeipa volumes with the command
```bash /var/lib/ipa-data```

Now, we run the command

```bash Docker run -h server.final.test --name my-group-server -p 53:53/udp -p 53:53 -p 80:80 -p 443:443 -p 389:389 -p 636:636 -p 88:88 -p 464:464 -p 88:88/udp -p 464:464/udp -p 123:123/udp -v /sys/fs/cgroup:/fs/cgroup:ro -v /var/lib/ipa-data:/data:Z -e PASSWORD=Secret123 –sysctl net.ipv6.conf.all.disable_ipv6=0 freeipa/freeipa-server:centros-8-4.8.7 ipa-server-install -U -r FINAL.TEST --no-ntp```

There might be a problem of port 53 already being used due to DNS and the docker command won’t run. To fix that in Ubuntu, do the following: 

Check firstly if that’s the case with the command ```bash sudo lsof -i :53```. If that has an output, your port is being used.
You then need to edit the ```bash /etc/system/resolved.conf``` file to the following version:

```bash
[Resolve]
DNS=1.1.1.1 #pick any DNS server this is the one I picked #FallbackDNS=
#Domains=
#LLMNR=no
#MulticastDNS=no
#DNSSEC=no
#DNSOverTLS=no
#Cache=no
DNSStubListener=no
#ReadEtcHosts=yes
```
Create a symbolic link with the command ```bash sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf ``` and reboot your system. 

Now the command ```bash sudo lsof -I :53``` should have no outputs and the docker command will run. For other distributions follow other similar guides. Also, for FreeIPA to run in other distributions you might need to disable SELinux.

If all is done properly, you should be able to type to your browser the 192.168.9.10 and go to the FreeIPA web UI, where you can connect with ```bash username admin``` and ```bash password Secret123```

You can easily users from the web UI with a certain password. Then log out and try to log in with that user. The system will immediately say that the password has expired, and you need to create a new password for the user. That guarantees that in real life, when the user tries to log in for the first time, the admin won’t know the final password of the user. We create a user with ```bash username alex``` and ```bash password password``` to test things out. Also, through the webui you can easily enable two-factor authentication (2FA) for the users. You need to log in as a user first and click on actions in the user profile and add otp token. Pick the TOTP and use the freeOTP app in your phone and connect the user with the OTP. Then log in as an admin and enable two factor authentication (password+OTP ) in the user settings. 2FA should run now if you want to use it.
 


## Intrusion Detection System - Snort

Intrusion Detection System (IDS) is deployed using the open source IDS software named Snort. 

### Docker image

Snort is deployed as a container using Docker. The Docker image is available at emilstahl/snort on [Dockerhub](https://hub.docker.com/r/emilstahl/snort). 
To run the Snort image, execute the following command on Unix: 
```bash 
$ docker run -it --rm --net=host emilstahl/snort /bin/bash 
```
where --net-host is needed to analyze traffic on the host machines interfaces. 

### Snort configuration 

Once in the container, the entrypoint is in the ./Snort directory where two directories are present, ./etc and ./rules. 
In ./etc the snort.conf is located where the user can specify the subnet of which to analyze traffic. This is specified at line 45 and is predefined to 
```bash
ipvar HOME_NET 192.168.1.0/24
```
Furthermore, one can specify which IP range the EXTERNAL_NET shall correspond to, the default is the inverse of the HOME_NET, meaning all adresses except the HOME_NET.

#### N O T E: 
When deploying this image on another network than initially attended, make sure to update HOME_NET and EXTERNAL_NET accordingly.

### Applied rules

In ./rules the local.rules file is located which includes site specific rules such as:

* ICMP requests originating from the EXTERNAL_NET with destination matching the HOME_NET
* FTP connection attempts
* SSH connections from the EXTERNAL_NET
* Potential bruteforce attacks due to three failed SSH authentications during the last 60 seconds originating from any IP-adress, including HOME_NET.

In .snort/rules/standard-rules/, various other rule files are located with the purpose of analyzing situations such as malicious port scannings, ddos attacks, SQL injections, dns lookups, and NTP. All .rules files are included in the ./etc/snort.conf file. 

### Test Snort configuration

To test and run the configuration, a .bashrc script is provided in .snort/.bashrc. 
The script must be sourced with the command 
```bash
source ./.bashrc
```
Once sourced, the current specification is tested with the ```bash $ testsnort``` command. The output shows number the of applied rules and the status of current configuration. 

### Run Snort

To start the Snort IDS, execute the command ```bash $ runsnort ```. 
The IDS can also be started explicitly with the following command:
```bash 
snort -A console -c /root/Building-Networked-Systems-Security-EP2520/Project/snort/etc/snort.conf -i enp1s0
```

N O T E: 
Make sure to specicy the correct network interface to listen on. Either in the alias of .bashrc or in the command above. The default interface is enp1s0. The interface is specified with the -i flag. 

As default, Snort writes alerts to the console. To write to log file, execute:

```bash 
snort -A console -c /root/Building-Networked-Systems-Security-EP2520/Project/snort/etc/snort.conf -i enp1s0 >> /var/log/snort/snort.log
```
Alternatively, remove the "-A console" from the command. 

## Commmon alerts

Below, some common alerts are shown including SSH connection attempts, ICMP requests, Port scannings, FTP connections, and SSH Brute Force Attack. 

```bash
03/04-16:41:28.802112  [**] [1:1000004:1] SSH incoming [**] [Priority: 0] {TCP} 192.168.1.2:55338 -> 192.168.1.26:22
03/04-16:41:28.805635  [**] [1:628:8] SCAN nmap TCP [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.2:55338 -> 192.168.1.26:22
03/04-16:41:56.717214  [**] [1:368:6] ICMP PING BSDtype [**] [Classification: Misc activity] [Priority: 3] {ICMP} 192.168.1.2 -> 192.168.1.26
03/04-16:41:56.717214  [**] [1:384:5] ICMP PING [**] [Classification: Misc activity] [Priority: 3] {ICMP} 192.168.1.2 -> 192.168.1.26
03/04-16:41:56.717273  [**] [1:1000001:0] Pinging... [**] [Priority: 0] {ICMP} 192.168.1.26 -> 192.168.1.2
03/04-16:42:15.831005  [**] [1:453:5] ICMP Timestamp Request [**] [Classification: Misc activity] [Priority: 3] {ICMP} 192.168.1.2 -> 192.168.1.26
03/04-16:42:15.851048  [**] [1:620:11] SCAN Proxy Port 8080 attempt [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.2:55340 -> 03/04-16:42:16.960237  [**] [1:620:11] SCAN Proxy Port 8080 attempt [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.2:55362 -> 03/04-16:42:17.064509  [**] [1:1000002:1] FTP connection attempt [**] [Priority: 0] {TCP} 192.168.1.2:55368 -> 192.168.1.26:21
03/04-16:42:18.397314  [**] [1:1000005:4] Potential SSH Brute Force Attack [**] [Classification: Attempted Denial of Service] [Priority: 2] {TCP} 192.168.1.2:55860 -> 192.168.1.26:22
03/04-16:42:18.606497  [**] [1:1421:11] SNMP AgentX/tcp request [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.2:56020 -> 192.168.1.26:705
03/04-16:42:18.827199  [**] [1:618:10] SCAN Squid Proxy attempt [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.2:56207 -> 192.168.1.26:3128
```


