# Deployment Guide

Production deployment and hardening for Hyena-AI.

## Pre-Deployment Checklist

- [ ] Python 3.10+ installed
- [ ] Model file downloaded and verified
- [ ] Dependencies installed via `uv sync`
- [ ] Tests passing: `uv run pytest`
- [ ] Configuration reviewed and hardened
- [ ] Audit logging enabled
- [ ] Backup strategy implemented
- [ ] Monitoring configured

---

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.10, 3.11, or 3.12
- **RAM**: 16GB (8GB minimum for LLM, 8GB for system)
- **Disk**: 20GB (10GB for model + 10GB for workspace)
- **CPU**: 4 cores (more cores = better inference speed)

### Recommended for Production
- **RAM**: 32GB+
- **GPU**: NVIDIA GPU with CUDA support (optional, significantly faster)
- **Storage**: SSD with 50GB+ free space
- **Network**: Stable connection for updates

---

## Installation Steps

### 1. Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y  # Ubuntu/Debian
brew update && brew upgrade                      # macOS

# Install Python 3.12 if needed
sudo apt-get install python3.12 python3.12-venv

# Install UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
# Clone repository
git clone <repo-url> /opt/hyena-ai
cd /opt/hyena-ai

# Create virtual environment
uv venv .venv

# Activate
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
uv sync
```

### 3. Download Model

```bash
# Create models directory
mkdir -p app/models

# Download Qwen model (3.5B or 9B variant)
# Option 1: Using curl
cd app/models
curl -L -o Qwen3.5-9B.Q8_0.gguf \
  "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen-3.5-9b-instruct-q8_0.gguf"

# Verify download
sha256sum Qwen3.5-9B.Q8_0.gguf

# Option 2: Using huggingface-hub
pip install huggingface-hub
huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --local-dir app/models
```

### 4. Configure for Production

```bash
# Create production config
mkdir -p ~/.hyena
cat > ~/.hyena/config.json << 'EOF'
{
  "model_name": "Qwen3.5-9B",
  "model_path": "/opt/hyena-ai/app/models/Qwen3.5-9B.Q8_0.gguf",
  "temperature": 0.7,
  "max_tokens": 2048,
  "permission_mode": "ask",
  "memory_extraction_interval": 5,
  "logging": {
    "level": "INFO",
    "file": "/var/log/hyena-ai/app.log",
    "max_size": "100MB",
    "backup_count": 10
  },
  "performance": {
    "enable_caching": true,
    "cache_size": "10GB",
    "stream_buffer_size": 4096
  }
}
EOF

# Restrict permissions
chmod 600 ~/.hyena/config.json
```

---

## Security Hardening

### 1. User and Permissions

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash hyena-ai
sudo chown -R hyena-ai:hyena-ai /opt/hyena-ai

# Set restrictive permissions
sudo chmod 755 /opt/hyena-ai
sudo chmod 750 /opt/hyena-ai/app
sudo chmod 600 /opt/hyena-ai/.env  # If using .env file
```

### 2. Directory Security

```bash
# Create secure directories
mkdir -p /var/log/hyena-ai
mkdir -p /var/cache/hyena-ai
mkdir -p /var/lib/hyena-ai

# Set permissions
sudo chown hyena-ai:hyena-ai /var/log/hyena-ai
sudo chmod 750 /var/log/hyena-ai

sudo chown hyena-ai:hyena-ai /var/cache/hyena-ai
sudo chmod 750 /var/cache/hyena-ai

sudo chown hyena-ai:hyena-ai /var/lib/hyena-ai
sudo chmod 750 /var/lib/hyena-ai
```

### 3. Permission System Configuration

```json
{
  "permission_system": {
    "enabled": true,
    "mode": "ask",              // Always confirm operations
    "audit_logging": true,
    "audit_log_file": "/var/log/hyena-ai/audit.log",
    "audit_retention_days": 90,
    "denied_operations_alert": true
  }
}
```

### 4. Network Security

```bash
# If running as service, use firewall
sudo ufw allow 22/tcp   # SSH only
sudo ufw enable

# Configure reverse proxy (Nginx example)
# See systemd service section below
```

### 5. Secrets Management

```bash
# Use environment variables for sensitive data
export HYENA_MODEL_PATH="/opt/hyena-ai/app/models/Qwen3.5-9B.Q8_0.gguf"
export HYENA_LOG_PATH="/var/log/hyena-ai"

# Never commit secrets to version control
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
```

---

## Running as Systemd Service (Linux)

### 1. Create Service File

```bash
sudo tee /etc/systemd/system/hyena-ai.service > /dev/null << 'EOF'
[Unit]
Description=Hyena-AI Agent System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=hyena-ai
Group=hyena-ai
WorkingDirectory=/opt/hyena-ai

# Environment
Environment="PATH=/opt/hyena-ai/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"

# Startup
ExecStart=/opt/hyena-ai/.venv/bin/python -m app.app

# Restart policy
Restart=on-failure
RestartSec=5s
StartLimitInterval=600s
StartLimitBurst=3

# Resource limits
MemoryLimit=32G
CPUQuota=80%

# Logging
StandardOutput=append:/var/log/hyena-ai/stdout.log
StandardError=append:/var/log/hyena-ai/stderr.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hyena-ai
sudo systemctl start hyena-ai

# Check status
sudo systemctl status hyena-ai
```

### 2. Monitor Service

```bash
# View logs
sudo journalctl -u hyena-ai -f

# Get service status
sudo systemctl status hyena-ai

# Restart service
sudo systemctl restart hyena-ai

# Stop service
sudo systemctl stop hyena-ai
```

---

## Running as Docker Container

### 1. Dockerfile

```dockerfile
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup working directory
WORKDIR /app

# Copy project
COPY . .

# Install Python dependencies
RUN /root/.cargo/bin/uv sync

# Create non-root user
RUN useradd -m -s /bin/bash hyena-ai
RUN chown -R hyena-ai:hyena-ai /app

# Download model (optional, can mount as volume)
RUN mkdir -p app/models

# Switch to non-root user
USER hyena-ai

# Expose port if using API interface
EXPOSE 8000

# Run application
CMD [".venv/bin/python", "-m", "app.app"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  hyena-ai:
    build: .
    container_name: hyena-ai
    volumes:
      - ./app/models:/app/app/models
      - hyena-cache:/home/hyena-ai/.hyena
      - hyena-logs:/var/log/hyena-ai
    environment:
      - HYENA_MODEL_PATH=/app/app/models/Qwen3.5-9B.Q8_0.gguf
      - HYENA_LOG_PATH=/var/log/hyena-ai
    memory: 32g
    cpus: '4'
    restart: unless-stopped
    networks:
      - hyena-network

volumes:
  hyena-cache:
  hyena-logs:

networks:
  hyena-network:
    driver: bridge
```

### 3. Run Docker

```bash
# Build image
docker build -t hyena-ai:latest .

# Run container
docker run -d \
  --name hyena-ai \
  -v ~/hyena-models:/app/app/models \
  -v hyena-logs:/var/log/hyena-ai \
  -m 32g \
  --cpus 4 \
  hyena-ai:latest

# Or use Docker Compose
docker-compose up -d

# View logs
docker logs -f hyena-ai

# Stop container
docker stop hyena-ai
```

---

## Monitoring and Maintenance

### 1. Health Checks

```bash
# Monitor system resources
while true; do
  echo "=== Hyena-AI Health Check ==="
  systemctl status hyena-ai
  ps aux | grep "python -m app.app"
  free -h
  df -h /
  echo ""
  sleep 300
done
```

### 2. Log Management

```bash
# Rotate logs
sudo tee /etc/logrotate.d/hyena-ai > /dev/null << 'EOF'
/var/log/hyena-ai/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 hyena-ai hyena-ai
    sharedscripts
    postrotate
        systemctl reload hyena-ai > /dev/null 2>&1 || true
    endscript
}
EOF

# Test logrotate
sudo logrotate -d /etc/logrotate.d/hyena-ai
```

### 3. Backup Strategy

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backup/hyena-ai"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config-$DATE.tar.gz ~/.hyena/

# Backup memory and state
tar -czf $BACKUP_DIR/memory-$DATE.tar.gz ~/.hyena/memory/

# Backup audit logs
tar -czf $BACKUP_DIR/audit-$DATE.tar.gz /var/log/hyena-ai/audit.log

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup-$DATE.tar.gz"
```

### 4. Performance Tuning

```json
{
  "performance": {
    "model_threads": 8,           // Adjust based on CPU cores
    "cache_enabled": true,
    "cache_size": "16GB",         // Adjust based on available RAM
    "streaming_buffer_size": 4096,
    "memory_compaction_interval": 86400,  // Daily
    "max_concurrent_operations": 10
  }
}
```

---

## Troubleshooting Deployment

### Model File Not Found

```bash
# Check model path
ls -lh /opt/hyena-ai/app/models/

# Verify permissions
stat /opt/hyena-ai/app/models/Qwen3.5-9B.Q8_0.gguf

# Update config if needed
/config set model_path /new/path/to/model.gguf
```

### Out of Memory

```bash
# Check memory usage
free -h
vmstat 1 5

# Solution: Use smaller model or reduce batch size
/config set max_tokens 1024

# Monitor during operation
watch -n 1 free -h
```

### Service Won't Start

```bash
# Check logs
journalctl -u hyena-ai -n 50

# Verify PYTHONPATH
export PYTHONPATH=/opt/hyena-ai:$PYTHONPATH

# Try manual start
/opt/hyena-ai/.venv/bin/python -m app.app

# Check dependencies
pip check
```

### Permission Denied Errors

```bash
# Verify file ownership
ls -la /opt/hyena-ai/app/models/

# Fix permissions
sudo chown -R hyena-ai:hyena-ai /opt/hyena-ai
sudo chmod -R 755 /opt/hyena-ai
```

---

## Disaster Recovery

### 1. Backup Current State

```bash
# Create emergency backup
tar -czf /backup/hyena-ai-emergency.tar.gz /opt/hyena-ai ~/.hyena
```

### 2. Restore from Backup

```bash
# Stop service
sudo systemctl stop hyena-ai

# Restore files
tar -xzf /backup/hyena-ai-backup.tar.gz -C /

# Restart service
sudo systemctl start hyena-ai
```

### 3. Database Reconstruction

```bash
# Clear and rebuild memory indices
/memory compact --rebuild

# Verify data integrity
/memory stats

# If corrupted, restore from backup
```

---

## Production Checklist

| Item | Status | Notes |
|------|--------|-------|
| Python 3.10+ installed | ✓ | |
| Model downloaded/verified | ✓ | |
| Tests passing | ✓ | 495+ tests |
| Config hardened | ✓ | Permission mode: ask |
| Audit logging enabled | ✓ | 90-day retention |
| Backup strategy | ✓ | Daily backups |
| Monitoring configured | ✓ | systemd service |
| Security audit completed | ✓ | RBAC, permissions |
| Performance tuned | ✓ | Based on hardware |
| Documentation updated | ✓ | This guide |

---

## Support & Help

- Check `/logs` for error messages
- Review [troubleshooting guide](13-troubleshooting.md)
- Check [development guide](11-development.md) for debugging
- Review architecture in [01-overview.md](01-overview.md)

