
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
* **GPIO Pinout**
* **Dependencies**
    * pip install aiohttp --break-system-packages

*   c   d   e
*   G   a   b