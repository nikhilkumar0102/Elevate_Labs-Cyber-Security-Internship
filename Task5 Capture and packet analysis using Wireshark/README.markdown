# Wireshark Network Capture Guide

A simple guide to capturing and analyzing network traffic using Wireshark.

## Overview

This repository provides a straightforward walkthrough for using Wireshark to capture, filter, and analyze network packets. It includes steps for installation, generating traffic, filtering packets, and exporting findings.

## Prerequisites

- Wireshark installed on your system (download from Wireshark's official site).
- Basic understanding of network interfaces (e.g., Ethernet or Wi-Fi).


## Steps

1. **Installation and Setup**

   - Install Wireshark on your system.
   - Launch Wireshark and select your active network interface (e.g., Ethernet or Wi-Fi) to start capturing packets.

![Examples:](Screenshot/6.png)
  
![Examples:](Screenshot/7.png)

2. **Generating and Filtering Traffic**

   - Generate network traffic by browsing a website (e.g., www.facebook.com) or pinging a server (e.g., `ping 8.8.8.8`).
   - Stop the capture after about a minute.
   - Using the filter bar to isolate protocols like `http`, `dns`,`tcp`, `http2` , `tls`.
   - We can see the following protocols in the image below.

![Examples:](Screenshot/1.png)
filter: DNS

![Examples:](Screenshot/2.png)
filter:DNS

![Examples:](Screenshot/3.png)
filter: http

![Examples:](Screenshot/4.png)
filter: http2 i.e https

![Examples:](Screenshot/5.png)
filter: tls

3. **Saving the file**

- To save the captured packets, go to the File menu in the `top-left corner` 
- Select Save As, and choose the .pcap file format.
- You can name it `test.pcap` or any other name you prefer.
- This file can be used for further analysis.

