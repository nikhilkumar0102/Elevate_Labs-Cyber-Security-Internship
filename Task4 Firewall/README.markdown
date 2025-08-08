# UFW Firewall Configuration Guide

This guide provides step-by-step instructions for configuring the Uncomplicated Firewall (UFW) on Ubuntu/Debian-based Linux systems to manage network traffic securely.

## Prerequisites
- UFW installed (pre-installed on most Ubuntu/Debian systems).
- Administrative privileges (`sudo` access).

## Step 1: Open Firewall Configuration Tool (UFW)
Ensure UFW is enabled and active.

```bash
sudo ufw enable  # Enable the firewall
sudo ufw status  # Check status (should show "active")
```



## Step 2: List Current Firewall Rules
View existing rules to understand the current configuration.

```bash
sudo ufw status verbose
```

### Example Output
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
```

### Default Policies
- **deny (incoming)**: Blocks all inbound traffic by default.
- **allow (outgoing)**: Permits all outbound traffic.

## Step 3: Block Inbound Traffic on a Specific Port (e.g., Port 23/Telnet)
Block Telnet (port 23) to prevent insecure connections.

```bash
sudo ufw deny 23/tcp
```

### Explanation
- **deny**: Blocks traffic.
- **23/tcp**: Targets TCP port 23 (Telnet).

Verify the rule:

```bash
sudo ufw status numbered
```

![NetScan Banner](Screenshot/1.png)

### Expected Output
```
[1] 23/tcp                   DENY IN     Anywhere
```

## Step 4: Test the Rule
Test the Telnet block locally or remotely to confirm it’s blocked.

### Test Locally (from the same machine)
```bash
telnet localhost 23
```

![NetScan Banner](Screenshot/2.png)

**Expected Result**: Connection fails with "Connection refused" or timeout.

### Test Remotely (from another machine)
```bash
telnet <your-server-ip> 23
```

**Expected Result**: Connection fails (blocked by UFW).

## Step 5: Allow SSH (Port 22)
Ensure SSH remains accessible for remote management.

```bash
sudo ufw allow 22/tcp
```

![NetScan Banner](Screenshot/3.png)

Verify:

```bash
sudo ufw status
```

![NetScan Banner](Screenshot/4.png)

### Expected Output
```
22/tcp                   ALLOW IN     Anywhere
```

## Step 6: Remove the Test Block Rule
To restore the original state, delete the Telnet block rule.

```bash
sudo ufw delete deny 23/tcp
```

![NetScan Banner](Screenshot/5.png)

Alternatively, if using rule numbers:

```bash
sudo ufw status numbered  # Identify rule number (e.g., [1])
sudo ufw delete 1         # Delete rule by number
```

## Step 7: Summary of Commands
For reference, here are all the commands used:

```bash
# Enable UFW
sudo ufw enable

# List rules
sudo ufw status verbose

# Block Telnet (port 23)
sudo ufw deny 23/tcp

# Allow SSH (port 22)
sudo ufw allow 22/tcp

# Test Telnet block
telnet localhost 23

# Delete Telnet block rule
sudo ufw delete deny 23/tcp
```

## Step 8: How UFW Filters Traffic
- **Default Policies**:
  - **Incoming**: Denied (unless explicitly allowed).
  - **Outgoing**: Allowed.
- **Rule Types**:
  - **allow**: Permits traffic (e.g., `allow 22/tcp` for SSH).
  - **deny**: Blocks traffic (e.g., `deny 23/tcp` for Telnet).
- **Order of Evaluation**: Rules are processed top-down (first match applies).
- **Stateful Filtering**: UFW automatically allows replies to outbound traffic.

## Key Notes
- **Persistence**: UFW rules survive reboots.
- **Logs**: Check UFW logs for blocked attempts:
  ```bash
  sudo tail -f /var/log/ufw.log
  ```
- **Reset UFW**: To start fresh:
  ```bash
  sudo ufw reset
  ```

## Contributing
Feel free to open issues or submit pull requests to improve this guide.

## License
This project is licensed under the MIT License.
