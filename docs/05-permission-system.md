# Permission System

Enterprise-grade Role-Based Access Control (RBAC) with audit logging.

## Overview

The permission system is a critical security layer that:
- **Gates all operations** - No tool runs without permission evaluation
- **Fine-grained control** - Resource and operation level granularity
- **Audit logging** - Complete trail of all operations
- **Flexible modes** - Auto-approve safe operations or require user confirmation
- **Temporary grants** - Time-limited permission overrides

---

## Core Concepts

### Resource Types (8 Categories)

1. **Files** - Read, write, delete file operations
2. **Directories** - List, create, delete directory operations
3. **Shell** - Execute shell commands, manage processes
4. **Network** - Network requests and external API calls
5. **Memory** - Access and modify session/persistent memory
6. **Configuration** - Modify system settings and configs
7. **Plugins** - Load/unload plugins and extensions
8. **Extensions** - Advanced system features

### Operation Classes

#### **Safe Operations** (Auto-Approved)
```
✓ read         - Read file contents
✓ glob         - Search for files matching pattern
✓ grep         - Full-text search in files
```

Auto-approved even without explicit permission grant.

#### **Dangerous Operations** (Require Approval)
```
✓ write        - Write/create files
✓ delete       - Delete files or directories
✓ execute      - Run shell commands
✓ modify       - Modify configuration
```

Require user confirmation or explicit permission grant.

#### **Administrative Operations** (Admin Only)
```
✓ admin_config - Modify system configuration
✓ admin_audit  - Access audit logs
✓ admin_perms  - Grant/revoke permissions
```

Require administrator access.

### Permission Modes

#### 1. **Auto Mode** (Default)
```
AUTO:
├─ Safe operations (read, glob, grep) → Automatically approved
└─ Dangerous operations (write, delete, execute) → Prompt user
```

**Configuration:**
```json
{
  "permission_mode": "auto"
}
```

#### 2. **Ask Mode**
```
ASK:
├─ All operations → Prompt user for confirmation
```

**Configuration:**
```json
{
  "permission_mode": "ask"
}
```

#### 3. **Manual Mode**
```
MANUAL:
├─ All operations → Require explicit permission grant
└─ Cannot be overridden by user
```

**Configuration:**
```json
{
  "permission_mode": "manual"
}
```

---

## Permission Flow

```
Tool Execution Request
    │
    ▼
Is it a SAFE operation?
    ├─ YES → Auto-approve (unless manual mode)
    │         │
    │         ▼
    │       Execute & Log
    │
    └─ NO → Check Mode
            │
            ├─ MANUAL → Require explicit grant
            │           │
            │           ├─ Grant exists & not expired?
            │           │   ├─ YES → Execute & Log
            │           │   └─ NO →  Deny & Log
            │
            ├─ ASK → Prompt user
            │        │
            │        ├─ User approves?
            │        │   ├─ YES → Execute & Log
            │        │   └─ NO → Deny & Log
            │
            └─ AUTO → Prompt user
                      │
                      ├─ User approves?
                      │   ├─ YES → Execute & Log
                      │   └─ NO → Deny & Log
```

---

## Managing Permissions

### Check Permission Status

```bash
# View all permissions
/config permissions

# View permissions for specific resource
/config permissions --resource files

# View audit log
/config permissions --log

# View expired permissions
/config permissions --expired
```

### Grant Permissions

**Permanent Grant:**
```bash
/tools permission read_file grant
/tools permission write_file grant
/tools permission execute_shell grant
```

**Temporary Grant (with expiration):**
```bash
# Valid duration formats:
# - "1h"  = 1 hour
# - "30m" = 30 minutes
# - "2d"  = 2 days

/tools permission write_file grant 1h    # 1 hour
/tools permission execute_shell grant 1d # 1 day
/tools permission delete_file grant 30m  # 30 minutes
```

### Revoke Permissions

```bash
/tools permission write_file revoke
/tools permission execute_shell revoke
```

### Check Single Permission

```bash
/tools permission read_file status
/tools permission execute_shell status --verbose
```

---

## Audit Logging

Every operation is logged with:

```
{
  "timestamp": "2024-04-22T10:30:45.123Z",
  "operation_id": "op_abc123",
  "user": "admin",
  "resource_type": "file",
  "resource": "/path/to/file.py",
  "operation": "write",
  "permission_granted": true,
  "permission_source": "temporary_grant",  // or "auto_approve", "user_confirmation"
  "duration_ms": 234,
  "result": "success",  // or "failed", "denied"
  "error": null  // or error message if failed
}
```

### View Audit Logs

```bash
# Show recent logs
/logs

# Filter by type
/logs --filter permission

# Show audit trail for specific resource
/logs --resource /path/to/file.py

# Export audit logs
/logs --export audit.json
```

---

## Command Usage Examples

### Example 1: Run Shell Command with Permission

```bash
# Try to run shell command
/agentic "list all Python files"

# System prompts (if not auto-approved):
# ⚠️  Operation: execute_shell
# Resource: /bin/bash
# Command: find . -name "*.py"
# 
# Grant permission? [y/n/1h/1d] y

# Executes and logs operation
```

### Example 2: Grant Temporary Permission for Development

```bash
# Grant write permission for 2 hours
/tools permission write_file grant 2h

# Can now write files without confirmation
/agentic "Create test_file.py with content..."

# After 2 hours, permission automatically expires
# /config permissions shows: "write_file - Expired"
```

### Example 3: Audit-Only Mode

```bash
# Set to manual mode (most restrictive)
/config set permission_mode manual

# Try to execute shell command
/agentic "run tests"

# System: "Permission denied: execute_shell"
# Reason: No active grant and manual mode requires explicit grant

# Grant temporary permission
/tools permission execute_shell grant 1h

# Now can execute
/agentic "run tests"
```

### Example 4: Check Audit Log

```bash
# View all operations in last hour
/logs --since 1h

# View all write operations
/logs --filter write

# View denied operations
/logs --filter denied

# Export for compliance review
/logs --export compliance_audit_2024.json
```

---

## Security Best Practices

### 1. **Principle of Least Privilege**
- Only grant permissions when needed
- Use temporary grants instead of permanent
- Audit regularly

### 2. **Time-Limited Permissions**
```bash
# Good: Temporary with expiration
/tools permission execute_shell grant 1h

# Less ideal: Permanent grant
/tools permission execute_shell grant
```

### 3. **Restricted Mode for Production**
```json
// Production configuration
{
  "permission_mode": "ask",  // Always confirm
  "auto_accept_safe_only": true,
  "log_level": "detailed"
}
```

### 4. **Regular Audit Reviews**
```bash
# Weekly audit check
/logs --since 7d --export weekly_audit.json

# Review denied operations
/logs --filter denied
```

### 5. **Separate Admin Accounts**
- Use separate accounts for administrative operations
- Keep elevated permissions for trusted accounts only
- Audit admin operations more frequently

---

## Configuration Options

### Disable Permission System (Not Recommended)

```json
{
  "permission_system": {
    "enabled": true,  // Set to false to disable (not recommended)
    "mode": "auto",
    "audit_logging": true,
    "auto_accept_safe_operations": true
  }
}
```

### Customize Safe Operations

```json
{
  "permission_system": {
    "safe_operations": [
      "read",
      "glob",
      "grep"
      // Add more if needed, but be careful!
    ]
  }
}
```

### Set Default Grant Duration

```json
{
  "permission_system": {
    "default_grant_duration": "1h"  // Default for temporary grants
  }
}
```

---

## Troubleshooting

### Permission Denied on Safe Operation

**Scenario**: Can't run read operation

```bash
# Check permission mode
/config show permission_mode

# Check resource permissions
/config permissions --resource files

# Try forcing safe approval
/agentic "Read app/app.py"
```

**Solution**: Set mode to "auto" or grant explicitly.

### Permission Grant Not Working

**Scenario**: Permission grant doesn't appear to take effect

```bash
# Check if permission exists and not expired
/tools permission execute_shell status

# View all active grants
/config permissions --active-grants

# Check audit log
/logs --filter permission
```

**Solution**: Check expiration time, may have expired already.

### Can't Revoke Permission

**Scenario**: Permission won't revoke

```bash
# Verify it exists
/tools permission write_file status

# Force revoke
/tools permission write_file revoke --force

# Check it was revoked
/tools permission write_file status
```

---

## API Usage (For Developers)

### Check Permission Programmatically

```python
from app.agents.permission_system import PermissionSystem

perm_system = PermissionSystem()

# Check if operation allowed
allowed = perm_system.check_permission(
    resource_type="file",
    resource="/path/to/file.py",
    operation="write",
    user="admin"
)

if allowed:
    # Execute operation
    pass
else:
    # Handle denial
    pass
```

### Grant Permission from Code

```python
# Grant temporary permission
perm_system.grant_permission(
    resource_type="shell",
    operation="execute",
    duration="1h",
    user="admin"
)

# Grant permanent permission
perm_system.grant_permission(
    resource_type="file",
    resource="/path/to/file.py",
    operation="write",
    permanent=True
)
```

### Access Audit Log

```python
# Get recent audit entries
logs = perm_system.get_audit_log(
    limit=100,
    resource_type="file",
    since_seconds=3600
)

for entry in logs:
    print(f"{entry['timestamp']} - {entry['operation']}: {entry['result']}")
```

---

## Summary

| Feature | Description |
|---------|-------------|
| **Safety-First** | All operations require permission evaluation |
| **Fine-Grained** | Resource and operation level control |
| **Flexible** | Multiple modes: auto, ask, manual |
| **Auditable** | Complete operation audit trail |
| **Time-Limited** | Temporary permission grants with expiration |
| **User-Friendly** | Clear prompts and easy grant/revoke |

The permission system is enabled by default and is critical for safe operation of Hyena-AI with untrusted agents or in shared environments.

