# DevAudit on Raspberry Pi - Complete Setup Guide

Turn your Raspberry Pi into a **privacy-first security monitoring hub** for your home network. This guide walks you through every step, from unboxing to running your first scan.

**Total Time:** ~30-45 minutes
**Difficulty:** Moderate (step-by-step instructions provided)
**Cost:** ~$50-80 (Raspberry Pi + SD card + power supply)

---

## Table of Contents

1. [Why Raspberry Pi?](#why-raspberry-pi)
2. [What You'll Need](#what-youll-need)
3. [Step 1: Set Up Raspberry Pi OS](#step-1-set-up-raspberry-pi-os)
4. [Step 2: Install DevAudit](#step-2-install-devaudit)
5. [Step 3: Configure Network Access](#step-3-configure-network-access)
6. [Step 4: Set Up Auto-Start Service](#step-4-set-up-auto-start-service)
7. [Step 5: Access from Other Devices](#step-5-access-from-other-devices)
8. [Advanced Configuration](#advanced-configuration)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance & Updates](#maintenance--updates)

---

## Why Raspberry Pi?

### Benefits of a Dedicated Security Hub

**Always-On Monitoring**
- Raspberry Pi runs 24/7 with minimal power (~3W)
- Costs ~$2-5/year in electricity
- Auto-restarts after power outages
- No need to leave your main computer on

**Centralized Access**
- Access dashboard from any device: phone, tablet, laptop
- One hub for all your devices (future multi-device support)
- Network-wide visibility
- Perfect for home labs

**Privacy & Control**
- 100% local - never touches the cloud
- You own the hardware and data
- No subscription fees
- Full control over everything

**Learning Opportunity**
- Learn Linux basics
- Practice networking concepts
- Understand system services
- Hands-on DevOps experience

### Pi Model Recommendations

| Model | Performance | Best For | Price |
|-------|------------|----------|-------|
| **Pi 4 (4GB)** | ⭐⭐⭐ Excellent | Recommended for most users | ~$55 |
| **Pi 4 (2GB)** | ⭐⭐ Good | Budget-conscious, smaller scans | ~$35 |
| **Pi 5** | ⭐⭐⭐ Excellent | Future-proofing, heavy usage | ~$60 |
| Pi 3 B+ | ⭐ Adequate | Works but slower | ~$35 |
| Pi Zero 2 W | ⭐ Minimal | Not recommended (too slow) | ~$15 |

**Recommendation:** Raspberry Pi 4 with 4GB RAM is the sweet spot.

---

## What You'll Need

### Hardware

**Required:**
- ✅ Raspberry Pi 4 (4GB) - ~$55
- ✅ MicroSD card (32GB+, Class 10) - ~$10
- ✅ USB-C Power Supply (official 15W recommended) - ~$8
- ✅ Ethernet cable (for setup) - ~$5

**Optional:**
- 💡 Case with cooling fan - ~$10 (recommended for 24/7 operation)
- 💡 HDMI cable + monitor (for initial setup only)
- 💡 USB keyboard (for initial setup only)

**Total Cost:** ~$78 (required) or ~$98 (with case & accessories)

### Software

- Raspberry Pi OS Lite (free - we'll download it)
- Raspberry Pi Imager (free - we'll download it)
- DevAudit (free - we'll install it)

### Network Requirements

- Wi-Fi network or Ethernet connection
- Router with available ethernet port (for setup)
- Devices on same network to access dashboard

---

## Step 1: Set Up Raspberry Pi OS

### 1.1 Download Raspberry Pi Imager

**On your computer (Windows/Mac/Linux):**

1. Visit: [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Download Raspberry Pi Imager
3. Install and open it

### 1.2 Flash the OS to SD Card

1. **Insert your microSD card** into your computer (use adapter if needed)

2. **Open Raspberry Pi Imager**

3. **Choose OS:**
   - Click "Choose OS"
   - Select: **"Raspberry Pi OS (64-bit)"** (recommended)
   - Or: "Raspberry Pi OS Lite (64-bit)" (headless, no desktop)

4. **Choose Storage:**
   - Click "Choose Storage"
   - Select your microSD card
   - ⚠️ **Warning:** This will erase the card!

5. **Configure Settings (Important!):**
   - Click the **⚙️ gear icon** (bottom right)
   - Check "Enable SSH"
     - Set username: `pi`
     - Set password: (choose a strong password)
   - Check "Configure wireless LAN"
     - SSID: (your Wi-Fi network name)
     - Password: (your Wi-Fi password)
     - Country: (your country code)
   - Check "Set locale settings"
     - Timezone: (your timezone)
   - Click "Save"

6. **Write to SD Card:**
   - Click "Write"
   - Wait ~5-10 minutes for completion

7. **Eject SD card** when done

### 1.3 Boot the Raspberry Pi

1. Insert the microSD card into the Raspberry Pi
2. Connect Ethernet cable (optional but recommended for first boot)
3. Connect power supply
4. Wait 2-3 minutes for first boot

The Pi will:
- Boot up
- Connect to your Wi-Fi
- Enable SSH
- Be ready for connection

---

## Step 2: Install DevAudit

### 2.1 Connect to Raspberry Pi via SSH

**On your computer:**

**Windows (PowerShell or Command Prompt):**
```bash
ssh pi@raspberrypi.local
```

**Mac/Linux (Terminal):**
```bash
ssh pi@raspberrypi.local
```

**If `raspberrypi.local` doesn't work:**
1. Log into your router's admin panel
2. Find the Pi's IP address (e.g., `192.168.1.100`)
3. Connect via IP: `ssh pi@192.168.1.100`

**First connection:**
- You'll see: "Are you sure you want to continue connecting?"
- Type: `yes`
- Enter the password you set in Step 1.2

### 2.2 Update the System

```bash
# Update package lists
sudo apt update

# Upgrade existing packages (takes 5-10 minutes)
sudo apt upgrade -y

# Reboot to apply updates
sudo reboot
```

Wait 1 minute, then reconnect:
```bash
ssh pi@raspberrypi.local
```

### 2.3 Install Python and pip

```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version  # Should show Python 3.9+
pip3 --version     # Should show pip 20+
```

### 2.4 Install DevAudit

```bash
# Install DevAudit with server dependencies
pip3 install devaudit[server]

# Verify installation
devaudit --version  # Should show version number
```

### 2.5 Test DevAudit

```bash
# Run a test scan (takes ~30 seconds)
devaudit scan

# You should see output with scan results
```

---

## Step 3: Configure Network Access

By default, DevAudit only listens on `localhost` (127.0.0.1). To access from other devices, we need to bind to all network interfaces.

### 3.1 Test Local Access First

```bash
# Start DevAudit server
devaudit serve --host 0.0.0.0 --port 8888
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

**Keep this running** and proceed to Step 5 to test from another device.

Press `Ctrl+C` when ready to continue setup.

---

## Step 4: Set Up Auto-Start Service

Let's configure DevAudit to start automatically when the Pi boots.

### 4.1 Create systemd Service File

```bash
# Create the service file
sudo nano /etc/systemd/system/devaudit.service
```

**Paste this content:**

```ini
[Unit]
Description=DevAudit Security Dashboard
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
Environment="PATH=/home/pi/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pi/.local/bin/devaudit serve --host 0.0.0.0 --port 8888
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y`
- Press `Enter`

### 4.2 Enable and Start the Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable devaudit

# Start the service now
sudo systemctl start devaudit

# Check status
sudo systemctl status devaudit
```

You should see:
```
● devaudit.service - DevAudit Security Dashboard
   Loaded: loaded (/etc/systemd/system/devaudit.service; enabled)
   Active: active (running) since ...
```

**If status shows "failed":**
```bash
# Check logs for errors
sudo journalctl -u devaudit -f
```

---

## Step 5: Access from Other Devices

### 5.1 Find Your Pi's IP Address

```bash
hostname -I
```

Example output: `192.168.1.100`

### 5.2 Access the Dashboard

**From any device on your network:**

**Option 1: Use hostname (easier)**
```
http://raspberrypi.local:8888
```

**Option 2: Use IP address (more reliable)**
```
http://192.168.1.100:8888
```

**You should see:**
- DevAudit Dashboard loads
- "Ready to audit your environment" message
- Click "Run Scan" to test

### 5.3 Bookmark It!

Add the dashboard URL to your bookmarks on:
- Your phone
- Your tablet
- Your laptop
- Any device you use regularly

**Pro Tip:** Add to home screen on mobile:
- iOS: Safari → Share → Add to Home Screen
- Android: Chrome → Menu → Add to Home Screen

---

## Advanced Configuration

### Custom Hostname

Change `raspberrypi.local` to something more memorable:

```bash
# Change hostname
sudo hostnamectl set-hostname devaudit-hub

# Edit hosts file
sudo nano /etc/hosts

# Change this line:
# 127.0.1.1    raspberrypi
# To:
# 127.0.1.1    devaudit-hub

# Reboot
sudo reboot
```

Now access via: `http://devaudit-hub.local:8888`

### Static IP Address

Prevent IP address from changing:

```bash
# Edit DHCP config
sudo nano /etc/dhcpcd.conf
```

Add at the end:
```bash
# Static IP for DevAudit
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Change `192.168.1.100` to your desired IP.

```bash
# Reboot to apply
sudo reboot
```

### HTTPS Setup (Optional)

For encrypted access (advanced):

```bash
# Install Caddy (reverse proxy)
sudo apt install -y caddy

# Configure Caddy
sudo nano /etc/caddy/Caddyfile
```

Add:
```
devaudit.local {
    reverse_proxy localhost:8888
}
```

```bash
# Restart Caddy
sudo systemctl restart caddy
```

Access via: `https://devaudit.local`

---

## Troubleshooting

### Can't Connect via SSH

**Problem:** `ssh: connect to host raspberrypi.local port 22: Connection refused`

**Solutions:**
1. Wait longer (first boot takes 2-3 minutes)
2. Try IP address instead: `ssh pi@192.168.1.X`
3. Ensure Pi is on same network
4. Check router admin panel for Pi's IP
5. Reconnect Ethernet cable

### Dashboard Won't Load

**Problem:** Browser shows "Can't reach this page"

**Solutions:**
1. **Check service status:**
   ```bash
   sudo systemctl status devaudit
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u devaudit -n 50
   ```

3. **Try direct IP instead of `.local`:**
   ```
   http://192.168.1.100:8888
   ```

4. **Restart service:**
   ```bash
   sudo systemctl restart devaudit
   ```

### Scans Take Forever

**Problem:** Scan stuck or very slow

**Solutions:**
1. Pi 3 or older? Upgrade to Pi 4
2. Check CPU usage: `top`
3. Check SD card speed (Class 10 required)
4. Reduce concurrent scans

### Service Won't Start

**Problem:** `systemctl status devaudit` shows "failed"

**Solutions:**
1. **Check logs:**
   ```bash
   sudo journalctl -u devaudit -f
   ```

2. **Verify devaudit path:**
   ```bash
   which devaudit
   # Should show: /home/pi/.local/bin/devaudit
   ```

3. **Update service file if path differs:**
   ```bash
   sudo nano /etc/systemd/system/devaudit.service
   # Update ExecStart path
   ```

4. **Reinstall DevAudit:**
   ```bash
   pip3 uninstall devaudit
   pip3 install devaudit[server]
   ```

### "Permission Denied" Errors

**Problem:** Can't run certain scans

**Solution:** Some scans require sudo. For Docker:
```bash
# Add pi user to docker group
sudo usermod -aG docker pi

# Log out and back in
exit
ssh pi@raspberrypi.local
```

---

## Maintenance & Updates

### Update DevAudit

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Update DevAudit
pip3 install --upgrade devaudit

# Restart service
sudo systemctl restart devaudit
```

### Update Raspberry Pi OS

```bash
# Update monthly for security patches
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### Backup SD Card (Recommended)

**On your computer:**

1. Shut down Pi: `sudo shutdown -h now`
2. Remove SD card
3. Use Raspberry Pi Imager
4. Choose "Create custom image" → "Backup"
5. Save to your computer
6. Keep backup in safe place

**Frequency:** Monthly or after major changes

### Monitor Pi Health

**Check temperature:**
```bash
vcgencmd measure_temp
```

Normal: 40-60°C
Warning: 70°C+
Critical: 80°C+ (throttling)

**If too hot:**
- Add heatsinks
- Add case fan
- Improve ventilation
- Reduce ambient temperature

---

## Next Steps

✅ **You now have a 24/7 security monitoring hub!**

**What's Next?**

1. **Bookmark the dashboard** on all your devices
2. **Run weekly scans** to track changes
3. **Explore scan history** and comparison features
4. **Join the community** - share your setup!
5. **Future: Install agents** on other devices (coming in v0.6)

**Want to Do More?**

- Set up alerts/notifications (coming soon)
- Schedule automatic scans (coming soon)
- Monitor multiple devices (v0.6+)
- Contribute to DevAudit development!

---

## Community & Support

**Questions? Issues? Ideas?**

- GitHub Issues: [github.com/aramantos/devaudit/issues](https://github.com/aramantos/devaudit/issues)
- Documentation: [docs/](docs/)
- Share your setup: Tag us on social media!

**Show off your Pi setup!**
We'd love to see photos of your DevAudit Pi hub. Share your build on GitHub Discussions!

---

## Appendix: Quick Command Reference

```bash
# Service management
sudo systemctl start devaudit      # Start service
sudo systemctl stop devaudit       # Stop service
sudo systemctl restart devaudit    # Restart service
sudo systemctl status devaudit     # Check status

# View logs
sudo journalctl -u devaudit -f     # Follow live logs
sudo journalctl -u devaudit -n 100 # Last 100 lines

# Update DevAudit
pip3 install --upgrade devaudit
sudo systemctl restart devaudit

# System updates
sudo apt update && sudo apt upgrade -y
sudo reboot

# Networking
hostname -I                         # Show IP address
ping raspberrypi.local              # Test connectivity
ip a                                # Show all network interfaces

# Diagnostics
vcgencmd measure_temp               # CPU temperature
top                                 # CPU/RAM usage
df -h                               # Disk space
```

---

*Happy monitoring! 🎉*

*Raspberry Pi + DevAudit = Privacy-first security hub for ~$50*
