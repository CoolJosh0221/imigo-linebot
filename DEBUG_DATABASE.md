# Database Connection Debugging Guide

## The Error
```
sqlite3.OperationalError: unable to open database file
```

## Debug Steps (run these on your machine)

### 1. Check if container can access the mounted directory
```bash
docker-compose exec backend ls -la /data/
```
**Expected:** You should see the `/data` directory with write permissions

### 2. Check what user the container runs as
```bash
docker-compose exec backend id
```
**Expected:** Should show uid=0 (root) or another user

### 3. Try to create a test file
```bash
docker-compose exec backend touch /data/test.txt
```
**Expected:** File should be created. If it fails, there's a permission issue.

### 4. Check volume mount
```bash
docker-compose exec backend cat /proc/mounts | grep data
```
**Expected:** Should show the volume mount

### 5. Check SELinux (if on Linux with SELinux)
```bash
# On your host machine
getenforce
```
If it says "Enforcing", you need to add `:z` to the volume mount.

## Quick Fixes

### Fix 1: Ensure host directory has correct permissions
```bash
# On your host machine
chmod 755 ./data
```

### Fix 2: If SELinux is the issue, update docker-compose.yaml
Change this line:
```yaml
volumes:
  - ./data:/data
```

To this:
```yaml
volumes:
  - ./data:/data:z
```

The `:z` flag tells Docker to relabel the content with the correct SELinux context.

### Fix 3: Rebuild and restart
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d backend
docker-compose logs -f backend
```

### Fix 4: Use in-memory database temporarily (for testing)
In `.env` or docker-compose.yaml, change:
```yaml
DATABASE_URL=sqlite+aiosqlite:///data/database.db
```

To:
```yaml
DATABASE_URL=sqlite+aiosqlite:///:memory:
```

This will use an in-memory database (data won't persist but it will work).

## What to check in logs

Look for:
```
INFO:database.database:Ensured database directory exists: /data
INFO:database.database:Database initialized with URL: sqlite+aiosqlite:///data/database.db
INFO:database.database:DB init ok
```

If you see "Ensured database directory exists" but still get the error, it's a permissions/mount issue.
