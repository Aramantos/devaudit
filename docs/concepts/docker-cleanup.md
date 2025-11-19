# Docker Cleanup: Reclaiming Disk Space and Understanding Container Waste

Docker is incredibly convenient—pull an image, run a container, done! But over time, Docker quietly accumulates **gigabytes** of disk space from stopped containers, unused images, dangling volumes, and orphaned networks.

This guide explains what Docker cleanup is, why it matters, and how to safely reclaim disk space without breaking your applications.

---

## What Is Docker Cleanup?

**Docker cleanup** is the process of removing unused Docker resources:
- **Stopped containers** - Containers you're no longer running
- **Dangling images** - Intermediate build layers with no tags
- **Unused images** - Images not referenced by any container
- **Unused volumes** - Data volumes not attached to any container
- **Unused networks** - Networks not used by any container

### Why Docker Accumulates Waste

**Docker's design philosophy: Never delete by default.**

When you:
- Stop a container → Docker keeps it (you might want logs or to restart it)
- Build a new image → Old layers stay (you might rollback)
- Remove a container → Volumes persist (data shouldn't disappear accidentally)
- Update an image → Old version remains (in case new version breaks)

**This is intentional safety**, but it means Docker never cleans up automatically.

---

## Real-World Impact

### Disk Space

**Typical Docker installation after 6 months:**

```bash
docker system df
```

**Actual output:**
```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          47        12        15.2GB    8.9GB (58%)
Containers      89        3         1.2GB     1.1GB (91%)
Local Volumes   34        5         2.8GB     2.3GB (82%)
Build Cache     0         0         0B        0B

Total:                              19.2GB    12.3GB (64%)
```

**Translation:** 12.3 GB of reclaimable waste—**64% of Docker's disk usage is junk.**

### Performance Impact

**Too many stopped containers:**
- Slow `docker ps -a` commands
- Cluttered dashboards
- Confusing troubleshooting (which container is the current one?)

**Too many unused images:**
- Slow image pulls (checking local cache)
- Difficulty finding the right image
- Wasted download bandwidth when re-pulling

**Too many volumes:**
- Hard to identify which data is important
- Risk of deleting wrong volume
- Backup confusion

---

## Understanding Docker Storage

### 1. Containers

**What they are:** Running or stopped instances of images.

**When they become waste:**
- Container stops and you don't need it anymore
- Container exited due to error and you've fixed the issue
- Container was for a one-off task (testing, migration, etc.)

**Check your containers:**
```bash
# List all containers (running + stopped)
docker ps -a

# Count stopped containers
docker ps -a -f status=exited | wc -l
```

**Example output:**
```
CONTAINER ID   IMAGE          STATUS                    SIZE
abc123def456   nginx:latest   Exited (0) 3 weeks ago    1.2MB (virtual 133MB)
789ghi012jkl   postgres:14    Exited (1) 2 months ago   63B (virtual 376MB)
```

**Translation:** These containers are stopped and consuming disk space.

### 2. Images

**What they are:** Templates for creating containers (like VM snapshots).

**Image types:**

**Tagged images:**
```bash
docker images
REPOSITORY    TAG       IMAGE ID       SIZE
nginx         latest    a1b2c3d4e5f6   133MB
postgres      14        f6e5d4c3b2a1   376MB
```

**Dangling images** (no tag, just `<none>`):
```bash
docker images -f "dangling=true"
REPOSITORY    TAG       IMAGE ID       SIZE
<none>        <none>    9876543210ab   1.2GB
```

**When images become waste:**
- **Dangling:** Intermediate build layers after rebuilding an image
- **Unused:** Image pulled but never used
- **Old versions:** Newer version pulled, old one not needed

### 3. Volumes

**What they are:** Persistent data storage for containers (databases, uploaded files, configs).

**When volumes become waste:**
- Container deleted but volume persists
- Development testing created volumes that are no longer needed
- Old application versions left behind volumes

**⚠️ DANGER ZONE:** Volumes contain actual data. Deleting the wrong volume = permanent data loss.

**Check your volumes:**
```bash
docker volume ls

# Find unused volumes
docker volume ls -f dangling=true
```

**Example output:**
```
DRIVER    VOLUME NAME
local     postgres_data       # ← Probably important (database data)
local     abc123def456789     # ← Random name = probably orphaned
local     old_project_uploads # ← Outdated project?
```

### 4. Networks

**What they are:** Virtual networks for container communication.

**When networks become waste:**
- Custom network created for a project that's been removed
- Leftover from docker-compose down without `-v` flag

**Check your networks:**
```bash
docker network ls

# Find unused networks
docker network prune --dry-run
```

---

## Safe Cleanup: Step-by-Step

### Step 1: Check What You Have

**Get the overview:**
```bash
docker system df
```

This shows total usage and reclaimable space—your "before" snapshot.

### Step 2: Remove Stopped Containers (Safest)

**Why it's safe:** Stopped containers are rarely needed. If you haven't restarted it in weeks, you don't need it.

**Command:**
```bash
# See what will be removed (dry run)
docker container prune --dry-run

# Actually remove stopped containers
docker container prune
```

**What this removes:** All containers with status `Exited` or `Created`.

**What this keeps:** Running containers.

**When to skip:** If you need container logs for debugging, grab them first:
```bash
docker logs <container_id> > container.log
```

### Step 3: Remove Dangling Images (Very Safe)

**Why it's safe:** Dangling images are build artifacts—they have no purpose except wasting space.

**Command:**
```bash
# See what will be removed
docker images -f "dangling=true"

# Remove dangling images
docker image prune
```

**What this removes:** Images tagged `<none>:<none>` (intermediate build layers).

**What this keeps:** All tagged images (nginx:latest, postgres:14, etc.).

### Step 4: Remove Unused Images (Moderate Risk)

**Why moderate risk:** You might pull an image for future use. Removing it means re-downloading later.

**Command:**
```bash
# See what will be removed
docker image prune -a --dry-run

# Remove all unused images
docker image prune -a
```

**What this removes:** Images not currently used by any container (running or stopped).

**What this keeps:** Images used by at least one container.

**When to skip:**
- You frequently switch between image versions
- Slow internet connection (re-downloading is painful)
- Images are large (multi-GB base images)

### Step 5: Remove Unused Volumes (HIGH RISK)

**⚠️ WARNING:** Volumes contain actual data. Only remove volumes if you're certain they're not needed.

**Command:**
```bash
# See what will be removed
docker volume prune --dry-run

# Remove unused volumes
docker volume prune
```

**What this removes:** Volumes not attached to any container.

**What this keeps:** Volumes currently mounted by containers.

**CRITICAL: Backup first!**
```bash
# Backup a volume before removing
docker run --rm -v volume_name:/data -v $(pwd):/backup ubuntu tar czf /backup/volume_backup.tar.gz /data
```

**When to skip:**
- Volume names suggest important data (postgres_data, uploads, configs)
- You're not 100% certain the data is disposable
- No recent backup exists

### Step 6: Remove Unused Networks (Safe)

**Why it's safe:** Networks are just configuration—no data loss risk.

**Command:**
```bash
# Remove unused networks
docker network prune
```

**What this removes:** Networks not used by any container.

**What this keeps:** Default networks (bridge, host, none) and networks in use.

### Step 7: Nuclear Option - Full Cleanup

**⚠️ DANGER:** This removes **everything** not currently in use.

**Command:**
```bash
# See everything that will be removed
docker system prune -a --volumes --dry-run

# Remove everything unused (containers, images, volumes, networks)
docker system prune -a --volumes
```

**When to use:**
- Fresh development environment setup
- You've backed up all important data
- You're okay re-downloading images

**When NEVER to use:**
- Production servers
- Systems with important volume data
- Shared development machines (teammates might be using those images)

---

## What's Safe vs. Risky

### ✅ Always Safe

| Command | What It Removes | Risk Level |
|---------|----------------|------------|
| `docker container prune` | Stopped containers | 🟢 Minimal |
| `docker image prune` | Dangling images (`<none>`) | 🟢 Minimal |
| `docker network prune` | Unused networks | 🟢 Minimal |

### ⚠️ Moderate Risk

| Command | What It Removes | Risk Level |
|---------|----------------|------------|
| `docker image prune -a` | All unused images | 🟡 Moderate - May need to re-download |
| `docker container prune -f` | Stopped containers (no confirmation) | 🟡 Moderate - Loses logs |

### 🔴 High Risk

| Command | What It Removes | Risk Level |
|---------|----------------|------------|
| `docker volume prune` | Unused volumes | 🔴 High - Permanent data loss |
| `docker system prune -a --volumes` | Everything unused | 🔴 Critical - No undo |

---

## How DevAudit Helps

### What DevAudit Scans

When you run `devaudit scan`, the Docker auditor checks:

1. **Stopped containers** - How many, how long they've been stopped
2. **Dangling images** - Untagged build artifacts
3. **Unused images** - Images not referenced by containers
4. **Unused volumes** - Volumes not mounted anywhere
5. **Disk usage** - Total Docker storage consumption

### DevAudit Output Example

```json
{
  "Docker": {
    "installed": true,
    "version": "24.0.7",
    "cleanup_candidates": [
      {
        "type": "stopped_container",
        "id": "abc123def456",
        "name": "eloquent_newton",
        "image": "nginx:latest",
        "status": "Exited (0) 3 weeks ago",
        "size": "1.2MB",
        "recommendation": "Safe to remove - stopped for 21 days"
      },
      {
        "type": "dangling_image",
        "id": "sha256:9876543210ab",
        "size": "1.2GB",
        "recommendation": "Safe to remove - intermediate build layer"
      },
      {
        "type": "unused_volume",
        "name": "abc123def456789",
        "size": "340MB",
        "recommendation": "⚠️ Verify before removing - may contain data"
      }
    ],
    "total_reclaimable": "8.9GB"
  }
}
```

### DevAudit Safety Features

**Risk classification:**
- 🟢 **Green (Safe):** Stopped containers, dangling images, unused networks
- 🟡 **Yellow (Verify):** Unused images you might need later
- 🔴 **Red (Dangerous):** Volumes with data

**No automatic deletion:** DevAudit **never** deletes anything—it only identifies cleanup candidates.

**Educational context:** Shows *why* something is safe or risky to remove.

---

## Automation and Best Practices

### 1. Weekly Cleanup Routine

**Safe weekly cleanup (no volumes):**
```bash
#!/bin/bash
# weekly-docker-cleanup.sh

echo "Docker Cleanup Report - $(date)"
echo "========================================"

# Show current usage
echo "Before cleanup:"
docker system df

# Remove stopped containers
echo -e "\nRemoving stopped containers..."
docker container prune -f

# Remove dangling images
echo -e "\nRemoving dangling images..."
docker image prune -f

# Remove unused networks
echo -e "\nRemoving unused networks..."
docker network prune -f

# Show results
echo -e "\nAfter cleanup:"
docker system df
```

**Schedule with cron (Linux/macOS):**
```bash
# Run every Sunday at 2 AM
0 2 * * 0 /home/user/weekly-docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1
```

**Schedule with Task Scheduler (Windows):**
```powershell
$action = New-ScheduledTaskAction -Execute "docker" -Argument "system prune -f"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Docker Cleanup"
```

### 2. Development vs. Production

**Development:**
- Cleanup aggressively (unused images, volumes)
- Re-downloading images is acceptable
- Data is typically test data

**Production:**
- **NEVER** use automated cleanup
- Manual cleanup only after verification
- Always backup volumes before removal
- Keep image versions for rollback capability

### 3. Docker Compose Cleanup

**When you stop a docker-compose project:**

```bash
# ❌ BAD - Leaves volumes behind
docker-compose down

# ✅ GOOD - Removes volumes too
docker-compose down -v

# ✅ BEST - Removes volumes and orphaned containers
docker-compose down -v --remove-orphans
```

### 4. Build Cleanup

**When building images, use multi-stage builds to reduce waste:**

```dockerfile
# ❌ BAD - Leaves build tools in final image (600MB)
FROM node:18
RUN apt-get update && apt-get install -y build-essential python3
COPY . .
RUN npm install
CMD ["npm", "start"]

# ✅ GOOD - Build tools only in build stage (150MB)
FROM node:18 AS builder
RUN apt-get update && apt-get install -y build-essential python3
COPY . .
RUN npm install

FROM node:18-slim
COPY --from=builder /app /app
CMD ["npm", "start"]
```

### 5. Set Storage Limits

**Prevent Docker from consuming entire disk:**

```json
// /etc/docker/daemon.json (Linux)
// C:\ProgramData\docker\config\daemon.json (Windows)
{
  "data-root": "/mnt/docker-data",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Restart Docker after changes:**
```bash
sudo systemctl restart docker  # Linux
# or restart Docker Desktop (Windows/macOS)
```

---

## Troubleshooting Common Issues

### Issue 1: "Cannot Remove Container - Conflict"

**Error:**
```
Error response from daemon: conflict: unable to remove abc123 - container is running
```

**Solution:**
```bash
# Stop the container first
docker stop abc123

# Then remove it
docker rm abc123

# Or force remove (stops and removes)
docker rm -f abc123
```

### Issue 2: "Image Is Referenced by Stopped Container"

**Error:**
```
Error response from daemon: conflict: unable to delete abc123 (must be forced) - image is being used by stopped container
```

**Solution:**
```bash
# Find which container is using the image
docker ps -a --filter ancestor=image_name

# Remove the stopped container first
docker rm container_id

# Then remove the image
docker rmi image_name
```

### Issue 3: "Volume Is in Use"

**Error:**
```
Error response from daemon: remove volume_name: volume is in use
```

**Solution:**
```bash
# Find which container is using the volume
docker ps -a --filter volume=volume_name

# Stop and remove the container
docker rm -f container_id

# Then remove the volume
docker volume rm volume_name
```

### Issue 4: Cleanup Freed Space But Disk Still Full

**Problem:** Docker's storage driver may not immediately release disk space to the OS.

**Solution (Linux):**
```bash
# Force Docker to reclaim disk space
sudo systemctl stop docker
sudo rm -rf /var/lib/docker/overlay2/l/*
sudo systemctl start docker
```

**Solution (Windows/macOS Docker Desktop):**
Settings → Resources → Disk Image → Reset to factory defaults (⚠️ Nuclear option)

### Issue 5: Lost Data After Volume Cleanup

**Problem:** Accidentally deleted a volume with important data.

**Bad news:** No built-in undo. Data is likely gone.

**Prevention:**
1. **Always backup before cleanup:**
   ```bash
   docker run --rm -v volume_name:/data -v $(pwd):/backup ubuntu tar czf /backup/volume-backup.tar.gz /data
   ```

2. **Use named volumes (easier to identify):**
   ```bash
   # ❌ Anonymous volume (hard to track)
   docker run -v /data postgres

   # ✅ Named volume (clear purpose)
   docker run -v postgres_production_data:/data postgres
   ```

3. **Use DevAudit to identify volumes before removing**

---

## Quick Reference

### Safe Daily Commands

```bash
# Check disk usage
docker system df

# Remove stopped containers (safe)
docker container prune -f

# Remove dangling images (safe)
docker image prune -f
```

### Monthly Deep Clean

```bash
# Remove stopped containers
docker container prune -f

# Remove dangling images
docker image prune -f

# Remove unused images (verify first!)
docker image prune -a

# Remove unused networks
docker network prune -f

# ⚠️ Only if you're certain: Remove unused volumes
docker volume prune
```

### Emergency: Reclaim Maximum Space

```bash
# ⚠️ DANGER: Removes everything unused
docker system prune -a --volumes

# Confirm by typing 'y'
```

### Check What Commands Will Do

```bash
# All cleanup commands support --dry-run or manual inspection first
docker container prune --dry-run
docker image prune -a --dry-run
docker volume ls -f dangling=true  # Inspect before pruning
```

---

## Best Practices Checklist

- [ ] Run `docker system df` weekly to monitor disk usage
- [ ] Remove stopped containers regularly (`docker container prune`)
- [ ] Remove dangling images after builds (`docker image prune`)
- [ ] Use `docker-compose down -v` to clean up properly
- [ ] Name volumes descriptively (e.g., `postgres_prod_data` not `abc123`)
- [ ] Backup volumes before removal
- [ ] Use multi-stage builds to reduce image size
- [ ] Set log rotation limits in Docker daemon config
- [ ] Never automate volume cleanup in production
- [ ] Use DevAudit to identify cleanup candidates before manual removal

---

## Related Documentation

- [Understanding Package Dependencies](dependencies.md) - Similar cleanup concepts for packages
- [Understanding Security Vulnerabilities (CVEs)](cves.md) - Why outdated images are risky
- [Docker Security Best Practices](../guides/docker-security.md) *(coming soon)*
- [DevAudit Docker Auditor](../../README.md#docker) - How DevAudit scans Docker

---

*Last updated: January 2025 (v0.2.x)*

*Found an error or have a suggestion? [Open an issue](https://github.com/aramantos/devaudit/issues) or [contribute](../../CONTRIBUTING.md)!*
