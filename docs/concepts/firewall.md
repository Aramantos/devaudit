# Firewalls

## What Is a Firewall?

A firewall is a network security system that monitors and controls incoming and outgoing network traffic based on predetermined security rules. Think of it as a security guard at the entrance of your computer:

- **Inbound Traffic**: Data coming TO your computer from the internet/network
- **Outbound Traffic**: Data leaving your computer to the internet/network

## Why It Matters

### Protection Against Network Attacks
- **Port Scanning**: Blocks hackers probing for open ports
- **Remote Exploits**: Prevents unauthorized access to services
- **Worms & Botnets**: Stops malware from spreading across networks
- **Man-in-the-Middle**: Reduces attack surface for interception

### Real-World Protection
Even if you have antivirus, a firewall is your first line of defense against:
- Attacks targeting network services (SMB, RDP, SSH)
- Zero-day exploits (unknown vulnerabilities)
- Lateral movement in compromised networks

## Real-World Impact

### What Happens Without a Firewall?

**WannaCry Ransomware (2017)**
- Spread via SMB port 445 (network file sharing)
- Firewall blocking port 445 would have prevented spread
- **Infected**: 200,000+ computers in 150 countries
- **Lesson**: Open network ports are attack vectors

**Mirai Botnet (2016)**
- Exploited IoT devices with open Telnet ports
- Assembled 600,000+ device botnet
- **Used for**: Massive DDoS attacks
- **Lesson**: Unprotected network services are easily compromised

**EternalBlue Exploit (2017+)**
- Exploited SMB vulnerability on Windows
- **Used by**: WannaCry, NotPetya, and others
- **Prevention**: Firewall + patches
- **Lesson**: Defense in depth matters

### "But I'm Behind a Router, Isn't That Enough?"

**Your router's firewall only protects FROM the internet:**
- ✅ Blocks external attacks
- ❌ Doesn't protect on public WiFi
- ❌ Doesn't block outbound malware connections
- ❌ Doesn't protect between devices on your network

**Your OS firewall protects:**
- ✅ On public WiFi (coffee shops, airports)
- ✅ Between devices on same network
- ✅ Outbound connections (stopping malware "phone home")
- ✅ When traveling with laptop

## When to Worry

### Critical (Act Immediately)
- ⚠️ Firewall completely disabled
- ⚠️ On public/untrusted WiFi without firewall
- ⚠️ Running servers (web, file, game) without firewall rules

### Important (Fix Soon)
- Some firewall profiles disabled (e.g., Public profile off)
- Default inbound policy set to "Allow"
- Many unnecessary open ports

### Minor (Check Eventually)
- Haven't reviewed firewall rules in 6+ months
- Don't understand which programs are allowed through

## When It's Safe to Relax (Slightly)

### Behind Corporate Firewall
- If your company has network-level firewalls
- Enterprise endpoint protection is managing rules
- But still keep OS firewall enabled as defense-in-depth

### Air-Gapped Systems
- Computers never connected to any network
- No WiFi, no Ethernet, no Bluetooth
- Rare scenarios: secure labs, classified systems

### Testing/Development
- Virtual machines isolated from network
- Sandboxed environments
- But: still best practice to keep firewall on

## How Firewalls Work

### Default Policies

**Inbound (Incoming Connections):**
- **Block by Default (Recommended)**: Only allow specific programs/ports
- Allow by Default (Dangerous): Open to all traffic

**Outbound (Outgoing Connections):**
- **Allow by Default (Common)**: Programs can connect out freely
- Block by Default (Restrictive): Must whitelist each program

### Rule Types

**Allow Rule**: Permits specific traffic (e.g., allow port 80 for web server)
**Block Rule**: Denies specific traffic (e.g., block Telnet port 23)
**Program Rule**: Allow/block specific applications

### Profiles (Windows/macOS)

**Domain**: Connected to your work network (managed by IT)
**Private**: Home or trusted networks
**Public**: Coffee shops, airports, untrusted WiFi (most restrictive)

## Managing Your Firewall

### Windows (Windows Defender Firewall)

**Check Status:**
```
Settings → Update & Security → Windows Security → Firewall & network protection
```

**Enable Firewall:**
```
Click on each network profile (Domain/Private/Public)
→ Turn on Windows Defender Firewall
```

**Manage Rules:**
```
Windows Defender Firewall → Advanced settings
→ Inbound Rules / Outbound Rules
```

**Allow an App:**
```
Firewall & network protection → Allow an app through firewall
→ Select app → Check boxes for network types
```

**Best Practice:**
- Enable firewall on ALL profiles
- Only allow apps you trust and need

### macOS (Application Firewall)

**Check Status:**
```
System Preferences → Security & Privacy → Firewall
```

**Enable Firewall:**
```
Click the lock icon (enter password)
→ Turn On Firewall
```

**Firewall Options:**
```
Firewall Options button:
- ☑ Block all incoming connections (most restrictive)
- ☑ Enable stealth mode (don't respond to scans)
- ☐ Automatically allow signed software (convenient but less secure)
```

**Best Practice:**
- Enable firewall
- Enable stealth mode
- Review allowed apps regularly

### Linux (UFW - Ubuntu/Debian)

**Check Status:**
```bash
sudo ufw status
```

**Enable Firewall:**
```bash
sudo ufw enable
```

**Allow Specific Ports:**
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

**Block All by Default:**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

**Delete Rules:**
```bash
sudo ufw delete allow 80/tcp
```

### Linux (firewalld - RHEL/CentOS/Fedora)

**Check Status:**
```bash
sudo firewall-cmd --state
```

**Enable Firewall:**
```bash
sudo systemctl start firewalld
sudo systemctl enable firewalld
```

**Allow Specific Services:**
```bash
sudo firewall-cmd --add-service=ssh --permanent
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --reload
```

**List Active Rules:**
```bash
sudo firewall-cmd --list-all
```

## Understanding Open Ports

### What Are Ports?
Ports are virtual endpoints for network connections. Think of them as numbered doors:
- **Port 80**: HTTP (web traffic)
- **Port 443**: HTTPS (secure web)
- **Port 22**: SSH (secure remote access)
- **Port 3389**: RDP (Windows Remote Desktop)
- **Port 445**: SMB (Windows file sharing)

### Why Open Ports Are Risky
Every open port is a potential entry point for attackers:
- **Known Vulnerabilities**: Old service versions with exploits
- **Misconfigurations**: Default passwords, weak settings
- **Zero-Days**: Newly discovered vulnerabilities

### Check Your Open Ports

**Windows:**
```powershell
netstat -an | findstr LISTENING
```

**macOS/Linux:**
```bash
sudo netstat -tuln
# or
sudo ss -tuln
```

**Only open ports you need. Close everything else.**

## Common Firewall Scenarios

### Scenario 1: Working from Coffee Shop
**Risk**: Public WiFi is untrusted
**Solution**: Ensure Public profile firewall is ON
**Extra**: Use VPN for encryption

### Scenario 2: Running a Home Server
**Risk**: Need to allow specific ports
**Solution**:
- Create specific inbound rules for required ports only
- Use router port forwarding + OS firewall together
- Consider VPN instead of exposing services

### Scenario 3: Game Not Connecting
**Risk**: Firewall blocking legitimate game traffic
**Solution**:
- Add game executable to allowed apps
- Or open specific ports (check game documentation)
- Don't disable firewall entirely!

### Scenario 4: Remote Work (VPN)
**Risk**: Need VPN to connect to work
**Solution**:
- Add VPN client to allowed apps
- IT may manage firewall rules via MDM
- Keep OS firewall enabled (defense-in-depth)

## Risks of Disabling Firewall

### Immediate Exposure
- **Port Scans**: Attackers can see open services
- **Exploitation**: Vulnerable services can be exploited
- **Worm Spread**: Network worms can infect quickly

### False Sense of Security
**"My antivirus will protect me"**
- Antivirus detects malware AFTER it's on your system
- Firewall prevents attacks BEFORE they reach your system
- Both are needed (defense-in-depth)

### Network Trust
**"I'm on my home network, it's safe"**
- Compromised IoT devices (cameras, printers, smart TVs)
- Guest WiFi devices
- Infected laptops/phones on same network

## Advanced Firewall Concepts

### Stateful vs. Stateless

**Stateful Firewall (Modern)**:
- Tracks connection state (new, established, related)
- Allows return traffic for outbound connections
- More intelligent, fewer rules needed

**Stateless Firewall (Old)**:
- Evaluates each packet independently
- Requires rules for both directions
- Less efficient

**All modern OS firewalls are stateful.**

### Application-Aware Firewalls

**Windows/macOS**:
- Rules based on applications, not just ports
- Allows "Chrome.exe" instead of "Port 443"
- More user-friendly

**Linux (with AppArmor/SELinux)**:
- Can restrict applications beyond network
- File access, system calls, etc.

### Next-Generation Firewalls (Enterprise)

**Features**:
- Deep packet inspection (DPI)
- Intrusion prevention (IPS)
- Application control
- URL filtering

**Examples**: Palo Alto, Fortinet, Check Point
**Home users**: Don't need these (expensive, complex)

## FAQs

**Q: Will a firewall slow down my internet?**
A: No. Modern firewalls have negligible performance impact (<1%).

**Q: Can I use two firewalls at once?**
A: Yes! Router firewall + OS firewall = defense-in-depth.

**Q: What if I disable it "just for a minute"?**
A: Port scans happen in seconds. Attacks are automated. Don't risk it.

**Q: Do I need firewall on Linux?**
A: Yes! Linux is not immune to network attacks, especially if running services.

**Q: Should I block outbound traffic too?**
A: For most users, no. But blocking outbound prevents malware from "phoning home."

**Q: What if a program can't connect?**
A: Add it to allowed apps. DON'T disable the entire firewall.

**Q: How do I know if I'm being attacked?**
A: Check firewall logs (Windows Event Viewer, syslog on Linux). But most attacks are silent.

## Learn More

- [NIST Firewall Best Practices](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-41r1.pdf)
- [CISA Firewall Guide](https://www.cisa.gov/firewall-best-practices)
- [Microsoft Windows Firewall Documentation](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/)
- [Red Hat Firewalld Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/sec-using_firewalls)

## DevAudit Tip

**Enable firewall on ALL network profiles. Only allow apps you trust. Review rules every 6 months.**

The firewall is your first line of defense—don't leave the front door open.

---

**Remember**: A firewall is like locking your car doors. It won't stop a determined thief, but it prevents opportunistic crime. Most attacks are automated and move on to easier targets when they hit a firewall.
