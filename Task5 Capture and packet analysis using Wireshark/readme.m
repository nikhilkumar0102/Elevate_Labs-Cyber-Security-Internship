#Wireshark Network Capture Guide

This guide provides a simple walkthrough for capturing and analyzing network traffic using Wireshark.

1. Installation and Setup
Install Wireshark: Download and install Wireshark on your system.

Start Capture: Launch Wireshark and select your active network interface (e.g., Ethernet or Wi-Fi) to begin capturing live packets.

2. Generating and Filtering Traffic
Generate Traffic: Browse to a website (e.g., www.facebook.com) or ping a server (ping 8.8.8.8) to create network activity.

Stop Capture: After about a minute, stop the capture to analyze the packets.

Filter Packets: Use the filter bar to isolate specific protocols. Examples of filters include http, dns, or tcp.

3. Analysis and Export
Identify Protocols: Look through the captured packets to identify at least three different protocols. Common examples are DNS (for domain name resolution), HTTP/HTTPS (for web traffic), and TCP (for connection management).

Export Findings: Save the captured packets by exporting the file in the .pcap format. This file can be used for further analysis.

Summary of Findings: Document your findings, including the protocols you identified and a brief summary of the packet details.
