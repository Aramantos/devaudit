# Understanding BIOS/UEFI: Your Computer's Foundation

When you press the power button, **before** Windows, macOS, or Linux even start, another piece of software runs first: your **BIOS** (or **UEFI**). It's the foundation of your computer—and like any foundation, keeping it secure and up-to-date matters.

This guide explains what BIOS/UEFI is, why updates matter, when to update (and when to skip), and how to do it safely.

---

## What Is BIOS/UEFI?

### Simple Explanation

**BIOS (Basic Input/Output System)** or **UEFI (Unified Extensible Firmware Interface)** is the first software that runs when you turn on your computer.

**Think of it as:**
- The ignition system for your car (without it, nothing starts)
- The foundation of your house (everything else builds on top)
- The conductor before the orchestra plays (coordinates all the hardware)

**What it does:**
1. **Checks hardware** - Tests RAM, CPU, hard drives (POST - Power-On Self-Test)
2. **Initializes devices** - Wakes up keyboard, mouse, graphics card, network
3. **Loads the operating system** - Finds Windows, macOS, or Linux and hands off control
4. **Stores low-level settings** - Boot order, hardware configuration, security settings

### BIOS vs. UEFI

**BIOS (Legacy):**
- Invented in 1975 for the IBM PC
- 16-bit mode, limited to 2.2 TB drives
- Text-based interface
- Slower boot times

**UEFI (Modern):**
- Introduced in 2005, standard since ~2010
- 32-bit or 64-bit mode, supports drives >2 TB
- Graphical interface (mouse support)
- Faster boot, better security (Secure Boot)

**How to tell which you have:**
- **Windows:** Press `Win + R`, type `msinfo32`, check "BIOS Mode" (shows "UEFI" or "Legacy")
- **macOS:** All Macs since 2006 use EFI/UEFI
- **Linux:** Run `sudo dmidecode -t bios` or check `/sys/firmware/efi` (exists = UEFI)

**Important:** For this guide, "BIOS" and "UEFI" are used interchangeably. Modern systems use UEFI, but the concept is the same.

---

## Why BIOS/UEFI Updates Matter

### 1. Security Vulnerabilities

BIOS runs **before** your operating system, which means:
- Malware in BIOS can survive OS reinstalls
- Antivirus software can't detect BIOS-level threats
- Attackers with BIOS access have complete control

**Real-World Example: LoJax (2018)**
- First UEFI rootkit found in the wild
- Infected BIOS firmware on systems in Eastern Europe
- Survived hard drive wipes and OS reinstalls
- Required motherboard replacement to remove

**Real-World Example: ThinkPwn (2016)**
- Vulnerability in Lenovo BIOS allowed privilege escalation
- Attackers could disable security features (Secure Boot, TPM)
- Affected millions of ThinkPad, ThinkCentre, and ThinkStation devices
- Fixed via BIOS update

**Bottom line:** Outdated BIOS = attackers can establish persistent, undetectable presence.

### 2. Hardware Compatibility

BIOS updates add support for new hardware:
- **New CPUs** - Motherboard supports newer processors after BIOS update
- **Larger drives** - Support for NVMe SSDs, drives >2 TB
- **New RAM** - Support for faster memory speeds (DDR5, etc.)
- **USB devices** - Better compatibility with modern peripherals

**Example:** Intel 300-series motherboards needed BIOS updates to support 9th-gen Intel CPUs. Without the update, the CPU wouldn't boot.

### 3. Bug Fixes and Stability

BIOS updates fix issues like:
- Random crashes or blue screens
- Sleep/wake problems
- USB device disconnects
- Overheating due to incorrect fan curves
- Boot failures

**Example:** Dell XPS 13 9370 had a BIOS bug causing random shutdowns. BIOS 1.5.1 fixed it.

### 4. Performance Improvements

BIOS updates can:
- Improve memory timings (faster RAM)
- Optimize CPU power management (better battery life)
- Enable faster boot modes
- Fix thermal throttling issues

---

## When to Update Your BIOS

### ✅ Update If:

1. **Manufacturer recommends it for security**
   - BIOS update changelog mentions "security fixes" or CVEs
   - Example: "Fixes CVE-2023-12345 - Privilege escalation vulnerability"

2. **You're experiencing hardware issues**
   - Random crashes, freezes, or reboots
   - Sleep/wake problems
   - USB or peripheral detection issues
   - Overheating or fan control problems

3. **You're upgrading hardware**
   - Installing a new CPU that requires BIOS support
   - Adding new RAM or storage types
   - Enabling features like TPM 2.0 for Windows 11

4. **Vendor provides a critical update**
   - Manufacturer specifically recommends the update
   - Update fixes known instability

### ⏸️ Think Twice If:

1. **Everything is working fine**
   - Old IT saying: "If it ain't broke, don't fix it"
   - BIOS updates carry risk—only update if there's a benefit

2. **Update only adds features you don't need**
   - Example: "Adds support for 13th-gen Intel CPUs" (you have 11th-gen)
   - Example: "Improves RGB lighting control" (you don't care about RGB)

3. **You have an older system (5+ years old)**
   - Manufacturer may have stopped testing updates thoroughly
   - Risk of update breaking compatibility with older components

### ❌ Skip If:

1. **No clear benefit for your configuration**
   - Changelog doesn't mention anything relevant to you

2. **You're not comfortable with the process**
   - BIOS updates require careful steps—better to skip than mess up

3. **System is critical and downtime is unacceptable**
   - BIOS updates require reboot and risk bricking the system
   - Production servers, medical equipment, etc. should be updated during maintenance windows only

---

## How to Check Your BIOS Version

### Windows

**Method 1: System Information**
1. Press `Win + R`
2. Type `msinfo32` and press Enter
3. Look for:
   - **BIOS Version/Date** - Shows version and release date
   - **BIOS Mode** - Shows UEFI or Legacy

**Method 2: Command Prompt**
```cmd
wmic bios get manufacturer,smbiosbiosversion,releasedate
```

**Example output:**
```
Manufacturer       ReleaseDate    SMBIOSBIOSVersion
American Megatrends Inc.  20221215000000.000000+000  F20
```
Translation: BIOS version F20, released December 15, 2022

### macOS

**Terminal command:**
```bash
system_profiler SPHardwareDataType | grep -i "boot rom"
```

**Example output:**
```
Boot ROM Version: 1037.120.66.0.0 (iBridge: 19.16.10730.0.0,0)
```

**Or:**
1. Click Apple menu → About This Mac
2. Click "System Report"
3. Look under "Hardware" → "Boot ROM Version"

### Linux

**Command:**
```bash
sudo dmidecode -t bios
```

**Example output:**
```
BIOS Information
    Vendor: American Megatrends Inc.
    Version: F20
    Release Date: 12/15/2022
```

**Or check kernel messages:**
```bash
dmesg | grep -i bios
```

---

## How to Find BIOS Updates

### 1. Identify Your Motherboard/System

**Windows:**
```cmd
wmic baseboard get manufacturer,product,version
```

**macOS:**
```bash
system_profiler SPHardwareDataType | grep "Model Identifier"
```

**Linux:**
```bash
sudo dmidecode -t baseboard
```

**Example output:**
```
Manufacturer: Gigabyte Technology Co., Ltd.
Product: Z690 AORUS ELITE AX
Version: 1.0
```

### 2. Visit Manufacturer's Support Site

**Desktop (custom build):** Motherboard manufacturer
- ASRock: https://www.asrock.com/support/index.asp
- ASUS: https://www.asus.com/support/
- Gigabyte: https://www.gigabyte.com/Support
- MSI: https://www.msi.com/support/

**Laptop/Pre-built:** System manufacturer
- Dell: https://www.dell.com/support/
- HP: https://support.hp.com/
- Lenovo: https://support.lenovo.com/
- Apple: macOS updates include firmware updates automatically

### 3. Download the Correct BIOS

**⚠️ CRITICAL:** Download the **exact** version for your model.

**Example: Gigabyte Z690 AORUS ELITE AX**
1. Go to Gigabyte support
2. Search "Z690 AORUS ELITE AX"
3. Click "Support" → "BIOS"
4. Download the latest version

**Check the changelog:**
```
F20 (2022/12/15)
1. Update CPU microcode
2. Improve memory compatibility
3. Fix USB connectivity issues

F19 (2022/10/01)
1. Support Intel 13th Gen processors
2. Security fixes (CVE-2022-xxxxx)
```

**Decision:** If you have 12th-gen Intel and no USB issues, F19 might be enough (security fixes). If you have USB problems, F20 is better.

---

## How to Update BIOS Safely

### ⚠️ Before You Start: Critical Safety Steps

**1. Fully charge laptop (or use AC power)**
   - **Never** update BIOS on battery power
   - Power loss during update = bricked motherboard

**2. Close all programs**
   - Antivirus, game launchers, background apps
   - Some BIOS utilities require no other programs running

**3. Backup important data**
   - BIOS updates rarely fail, but when they do, it's catastrophic
   - Backup personal files to external drive or cloud

**4. Verify the BIOS file**
   - Make sure you downloaded the correct model
   - Check file hash if manufacturer provides it

### Method 1: Windows BIOS Update Utility (Easiest)

**Most manufacturers provide Windows utilities:**
- **ASUS:** EZ Flash Utility, ASUS Update
- **Gigabyte:** @BIOS, Q-Flash Plus
- **MSI:** MSI Live Update, M-Flash
- **Dell/HP/Lenovo:** Automated installer (double-click .exe)

**Example: ASUS EZ Flash**
1. Download BIOS file from ASUS website
2. Extract the .CAP file to USB drive (FAT32 format)
3. Restart computer
4. Press `F7` or `Delete` to enter BIOS
5. Go to "Tool" → "ASUS EZ Flash Utility"
6. Select USB drive and the .CAP file
7. Confirm update → **Do not turn off computer**
8. System will reboot automatically when done

**Example: Dell/HP/Lenovo Automated Installer**
1. Download .exe file from manufacturer website
2. Double-click to run (requires administrator)
3. Follow on-screen instructions
4. System will reboot → **Do not turn off computer**
5. BIOS update happens during boot (progress bar shown)
6. System reboots again automatically

### Method 2: UEFI BIOS Update (Advanced)

**For systems without Windows or manufacturer utility:**

1. **Format USB drive to FAT32**
   ```cmd
   diskpart
   list disk
   select disk X (your USB drive number)
   clean
   create partition primary
   format fs=fat32 quick
   assign
   exit
   ```

2. **Copy BIOS file to USB root**
   - Don't put it in a folder—just the root of the USB drive

3. **Restart and enter BIOS**
   - Press `Delete`, `F2`, `F10`, or `F12` (depends on manufacturer)

4. **Find the update utility**
   - ASUS: "EZ Flash"
   - Gigabyte: "Q-Flash"
   - MSI: "M-Flash"
   - ASRock: "Instant Flash"

5. **Select the BIOS file from USB**
   - Confirm update
   - **Do not turn off or reset the computer**

6. **Wait for completion**
   - Typically 2-5 minutes
   - System will reboot automatically

### Method 3: macOS Firmware Updates (Automatic)

**Apple handles firmware updates automatically:**

1. Open "System Preferences" → "Software Update"
2. If a firmware update is available, it will be listed
3. Click "Update Now"
4. System will reboot → **Do not turn off computer**
5. Progress bar shown during firmware update
6. System reboots again automatically

**Note:** macOS firmware updates are integrated with OS updates—you rarely need to manually check.

---

## What to Do If BIOS Update Fails

### Symptoms of Failed BIOS Update

- System won't boot (no POST beep, no display)
- Stuck on manufacturer logo screen
- Fans spin but nothing happens
- Error message: "BIOS corrupted" or "Checksum error"

### Recovery Options

**1. Try BIOS Recovery Mode (Most Motherboards)**

Many motherboards have a recovery mode:
- **ASUS:** Press `Ctrl + Home` during boot (with USB drive containing BIOS)
- **Gigabyte:** Q-Flash Plus button on rear I/O
- **MSI:** Flash BIOS Button on rear I/O
- **Dell/HP:** Some models have recovery partition

**Steps:**
1. Prepare USB drive with BIOS file (FAT32, root directory)
2. Rename BIOS file to manufacturer-specific name (e.g., `GIGABYTE.bin`)
3. Insert USB, press recovery button/key combo
4. Wait 5-10 minutes (no display, system will reboot when done)

**2. Clear CMOS**

Sometimes clearing CMOS settings can help:
1. Unplug power cord
2. Locate CMOS battery on motherboard (coin-sized)
3. Remove battery for 10 seconds
4. Reinsert battery, plug in power, try booting

**3. Dual BIOS (Some Motherboards)**

Gigabyte, MSI, and some ASUS boards have dual BIOS chips:
- If primary BIOS fails, backup BIOS takes over
- System automatically recovers from backup

**4. Contact Manufacturer Support**

If recovery doesn't work:
- **Laptops:** Contact manufacturer (Dell, HP, Lenovo) for RMA
- **Desktops:** Contact motherboard manufacturer
- **Last resort:** Professional repair or motherboard replacement

---

## How DevAudit Helps

### What DevAudit Will Check (v0.3.0+)

When you run `devaudit scan`, the BIOS auditor will:

1. **Detect BIOS information:**
   - Vendor (American Megatrends, Award, Phoenix, Apple, etc.)
   - Current version
   - Release date
   - Motherboard model

2. **Check for updates:**
   - Compare against manufacturer's latest version (where possible)
   - Flag if BIOS is >2 years old (potential security risk)

3. **Assess risk level:**
   - 🟢 **Low:** BIOS is recent, no known vulnerabilities
   - 🟡 **Medium:** BIOS is 1-2 years old, consider updating
   - 🔴 **High:** BIOS is >2 years old, known vulnerabilities

4. **Provide educational content:**
   - What BIOS is and why it matters
   - Why this specific update is recommended
   - How to update safely for your platform
   - Risks and when to skip

### Example DevAudit Output

```json
{
  "BIOS": {
    "installed": true,
    "vendor": "American Megatrends Inc.",
    "version": "F18",
    "release_date": "2021-06-15",
    "motherboard": "Gigabyte Z590 AORUS ELITE AX",
    "latest_version": "F20",
    "update_available": true,
    "age_days": 945,
    "risk_level": "medium",
    "recommendation": "Update recommended - security fixes in F20",
    "educational_content": {
      "what_is_it": "BIOS is the first software that runs when you turn on your computer...",
      "why_it_matters": "Outdated BIOS can have security vulnerabilities...",
      "how_to_fix": "Visit Gigabyte support and download BIOS F20...",
      "risks": "BIOS updates carry small risk of system failure if power is lost...",
      "learn_more_url": "https://github.com/aramantos/devaudit/blob/main/docs/concepts/bios-uefi.md"
    }
  }
}
```

---

## Common BIOS Issues and Solutions

### Issue 1: "USB Boot Not Working"

**Problem:** Can't boot from USB drive to update BIOS or install OS.

**Solution:**
1. Enter BIOS setup (press Delete/F2 during boot)
2. Go to "Boot" settings
3. Enable "USB Boot" or "Legacy USB Support"
4. Change boot order (USB should be first)
5. Save and exit

### Issue 2: "Secure Boot Violation"

**Problem:** "Secure Boot Violation. Invalid signature detected. Check Secure Boot Policy in Setup."

**Solution:**
1. Enter BIOS setup
2. Go to "Security" or "Boot" section
3. Disable "Secure Boot"
4. Boot normally
5. *After* troubleshooting, re-enable Secure Boot for security

### Issue 3: "CMOS Battery Low" or "CMOS Checksum Error"

**Problem:** Settings reset every reboot, wrong date/time.

**Solution:**
1. Replace CMOS battery (CR2032 coin cell, $3-5)
2. On laptops, may require partial disassembly (check YouTube for model-specific guides)

### Issue 4: "No POST After BIOS Update"

**Problem:** Updated BIOS, now system won't boot.

**Solution:**
1. Try BIOS recovery mode (see "What to Do If BIOS Update Fails" above)
2. Clear CMOS
3. Remove all peripherals except keyboard/monitor
4. Try with one RAM stick only
5. If still fails, contact manufacturer

### Issue 5: "Fan Always Running at 100%"

**Problem:** After BIOS update, fans run at full speed constantly.

**Solution:**
1. Enter BIOS setup
2. Go to "Fan Control" or "Hardware Monitor"
3. Change fan mode from "Full Speed" to "Auto" or "Smart Fan"
4. Set custom fan curve if available
5. Save and exit

---

## Best Practices for BIOS Management

### 1. Check BIOS Version Annually

**Why:** Stay aware of security updates without obsessing over every release.

**How:**
- Run DevAudit quarterly
- Check manufacturer website annually
- Subscribe to security mailing lists for your hardware

### 2. Document Your BIOS Settings

**Before updating, take photos or write down:**
- Boot order
- Overclocking settings (CPU, RAM speeds)
- Fan curves
- Enabled/disabled devices
- Secure Boot status

**Why:** BIOS updates often reset settings to defaults.

### 3. Update During Low-Risk Times

**Best time:**
- Weekend morning (time to troubleshoot if issues)
- When you have another computer available (to search for solutions)
- When you don't have urgent deadlines

**Worst time:**
- Night before a presentation
- During a power outage warning
- When you're in a hurry

### 4. Keep BIOS Files Archived

**After successful update:**
- Keep the BIOS file on USB drive
- Store in safe place
- Label with version and date

**Why:** If you need to downgrade or recover, you have the file ready.

### 5. Understand Your Warranty

**Some manufacturers:**
- Void warranty if you flash third-party BIOS
- Require RMA for failed BIOS updates
- Provide free motherboard replacement if official update fails

**Check your motherboard/system warranty before updating.**

---

## Quick Reference

### Should I Update My BIOS?

| Scenario | Update? | Priority |
|----------|---------|----------|
| Security vulnerability (CVE) | ✅ Yes | High |
| System is unstable/crashing | ✅ Yes | High |
| Upgrading CPU/RAM | ✅ Yes | High |
| BIOS is >3 years old | ✅ Probably | Medium |
| Minor feature additions | ⏸️ Maybe | Low |
| System working perfectly | ❌ No | None |

### BIOS Update Safety Checklist

- [ ] Laptop is plugged into AC power (or desktop PSU is connected)
- [ ] BIOS file is correct for exact motherboard model
- [ ] All important data is backed up
- [ ] All programs are closed
- [ ] You have 30 minutes of uninterrupted time
- [ ] You've read the changelog and understand what's changing
- [ ] You've documented current BIOS settings (photos or notes)

### BIOS Update Command Reference (Linux)

```bash
# Check current BIOS version
sudo dmidecode -t bios

# Identify motherboard
sudo dmidecode -t baseboard

# Check for fwupd-supported updates (Linux firmware updater)
fwupdmgr get-devices
fwupdmgr refresh
fwupdmgr get-updates

# Apply BIOS update via fwupd (if supported)
fwupdmgr update
```

---

## Related Documentation

- [Understanding Security Vulnerabilities (CVEs)](cves.md) - Why BIOS vulnerabilities matter
- [OS Updates](os-updates.md) - Keeping your operating system secure *(coming soon)*
- [System Security Checklist](../guides/system-security.md) - Complete security audit *(coming soon)*

---

*Last updated: January 2025 (v0.3.x planning)*

*Found an error or have a suggestion? [Open an issue](https://github.com/aramantos/devaudit/issues) or [contribute](../../CONTRIBUTING.md)!*
