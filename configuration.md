Marquee Lighted Sign Project - configuration

* **Ethernet Devices**
    * Raspberry Pi Zero 2
        * WiFi
            * sudo nmcli connection down "preconfigured"
        * Ethernet
            * 192.168.64.101
            * sudo nmcli con mod "Wired connection 1" ipv4.address "192.168.64.101/24"
            * sudo nmcli con mod "Wired connection 1" ipv4.method manual

    * Laptop
        * 192.168.64.105
    * Shelly ProDimmer2PM FCE8C0D8ED98| 1.4.4| 679fcca9
        * 192.168.64.111
    * Shelly ProDimmer2PM 2CBCBB9F5470| 1.4.4| 679fcca9
        * 192.168.64.112
    * Shelly ProDimmer2PM 2CBCBB9EBE8C| 1.4.4| 679fcca9
        * 192.168.64.113
    * Shelly ProDimmer2PM 2CBCBBA247DC| 1.4.4| 679fcca9
        * 192.168.64.114
    * Shelly ProDimmer2PM 2CBCBBA21C5C| 1.4.4| 679fcca9
        * 192.168.64.115
    * Shelly ProDimmer2PM A0DD6C9F72D0| 1.4.4| 679fcca9
        * 192.168.64.116
* **USB Ports**
SUBSYSTEM=="tty", ATTRS{serial}=="NLRL250501R0027", SYMLINK+="marquee_lights"
SUBSYSTEM=="tty", ATTRS{serial}=="NLRL260501R0296", SYMLINK+="marquee_drums"
SUBSYSTEM=="tty", ATTRS{serial}=="NLRL250409R0868", SYMLINK+="marquee_bells"
* **Dependencies**
    * pip install aiohttp --break-system-packages
* **Bells**
* * >   c   d   e
* * >   b   a   G
* * >   D   E

_
* **Auto Start**
* /etc/systemd/system/marquee.service

        [Unit]
        Description=Marquee
        After=multi-user.target

        [Service]
        Type=idle
        ExecStart=/usr/bin/python /home/mjmccaffrey/marquee/marquee.py mode 1
        WorkingDirectory=/home/mjmccaffrey/marquee
        User=mjmccaffrey

        [Install]
        WantedBy=multi-user.target
