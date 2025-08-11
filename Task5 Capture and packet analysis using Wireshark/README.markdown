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

   ![Examples:](screenshot/6.png)
  
  ![Examples:](screenshot/7.png)

2. **Generating and Filtering Traffic**

   - Generate network traffic by browsing a website (e.g., www.facebook.com) or pinging a server (e.g., `ping 8.8.8.8`).
   - Stop the capture after about a minute.
   - Use the filter bar to isolate protocols like `http`, `dns`, or `tcp`.

3. **Analysis and Export**

   - Identify at least three protocols in the captured packets (e.g., DNS, HTTP/HTTPS, TCP).
   - Save the captured packets in `.pcap` format for further analysis.
   - Document your findings, including identified protocols and a brief summary of packet details.
