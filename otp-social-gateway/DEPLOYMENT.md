# 🏭 Production Deployment Guide

## Pre-Deployment Checklist

- [ ] Telegram Bot Token obtained and tested
- [ ] Environment variables configured
- [ ] Docker image tested locally
- [ ] Monitoring setup ready (Prometheus/Grafana)
- [ ] Backup plan for rate limiting data
- [ ] Load balancer configured (if scaling)

---

## Deployment Options

### Option 1: Docker Compose (Simplest)

**Recommended for:** Single-server deployments, development staging

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  otp-gateway:
    image: otp-social-gateway:latest
    container_name: otp-gateway-prod
    restart: always
    ports:
      - \"55155:55155\"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DEFAULT_EXPIRE_SECONDS=30
      - RATE_LIMIT_PER_USER=5
      - LOG_LEVEL=WARNING
    healthcheck:
      test: [\"CMD\", \"python\", \"-c\", \"import urllib.request; urllib.request.urlopen('http://localhost:55155/health')\"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: \"json-file\"
      options:
        max-size: \"10m\"
        max-file: \"3\"
    networks:
      - otp-network

  # Optional: Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    ports:
      - \"9090:9090\"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - otp-network

  # Optional: Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - \"3000:3000\"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - otp-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  otp-network:
    driver: bridge
```

**Deploy:**
```bash
# Build production image
docker build -t otp-social-gateway:latest .

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f otp-gateway
```

---

### Option 2: Kubernetes (Scalable)

**Recommended for:** Multi-server, high-availability, auto-scaling

```yaml
# k8s-deployment.yml
apiVersion: v1
kind: Secret
metadata:
  name: otp-gateway-secrets
type: Opaque
stringData:
  telegram-bot-token: \"YOUR_TOKEN_HERE\"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otp-gateway
  labels:
    app: otp-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otp-gateway
  template:
    metadata:
      labels:
        app: otp-gateway
    spec:
      containers:
      - name: otp-gateway
        image: otp-social-gateway:latest
        ports:
        - containerPort: 55155
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: otp-gateway-secrets
              key: telegram-bot-token
        - name: DEFAULT_EXPIRE_SECONDS
          value: \"30\"
        - name: RATE_LIMIT_PER_USER
          value: \"5\"
        - name: LOG_LEVEL
          value: \"INFO\"
        resources:
          requests:
            memory: \"128Mi\"
            cpu: \"100m\"
          limits:
            memory: \"256Mi\"
            cpu: \"200m\"
        livenessProbe:
          httpGet:
            path: /health
            port: 55155
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 55155
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: otp-gateway-service
spec:
  selector:
    app: otp-gateway
  ports:
  - protocol: TCP
    port: 55155
    targetPort: 55155
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: otp-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: otp-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Deploy:**
```bash
# Apply configurations
kubectl apply -f k8s-deployment.yml

# Check status
kubectl get pods -l app=otp-gateway
kubectl get svc otp-gateway-service

# View logs
kubectl logs -l app=otp-gateway -f

# Scale manually
kubectl scale deployment otp-gateway --replicas=5
```

---

### Option 3: Cloud Services

#### AWS ECS (Fargate)

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag otp-social-gateway:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/otp-gateway:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/otp-gateway:latest

# Create ECS task definition (via AWS Console or CLI)
# Set environment variables via AWS Secrets Manager
```

#### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/otp-gateway
gcloud run deploy otp-gateway \
  --image gcr.io/<project-id>/otp-gateway \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=<token> \
  --allow-unauthenticated \
  --port 55155
```

#### Azure Container Instances

```bash
# Create container instance
az container create \
  --resource-group myResourceGroup \
  --name otp-gateway \
  --image otp-social-gateway:latest \
  --dns-name-label otp-gateway \
  --ports 55155 \
  --environment-variables TELEGRAM_BOT_TOKEN=<token>
```

---

## Configuration Best Practices

### 1. Secrets Management

**DO NOT** commit `.env` files to version control!

**Docker Secrets:**
```bash
# Create secret
echo \"YOUR_TOKEN\" | docker secret create telegram_bot_token -

# Use in compose
services:
  otp-gateway:
    secrets:
      - telegram_bot_token
    environment:
      - TELEGRAM_BOT_TOKEN_FILE=/run/secrets/telegram_bot_token

secrets:
  telegram_bot_token:
    external: true
```

**Kubernetes Secrets:**
```bash
kubectl create secret generic otp-gateway-secrets \
  --from-literal=telegram-bot-token=YOUR_TOKEN
```

**Environment Variable Providers:**
- AWS: AWS Secrets Manager or Parameter Store
- GCP: Secret Manager
- Azure: Key Vault
- HashiCorp Vault

### 2. Reverse Proxy with HTTPS

**Nginx Configuration:**
```nginx
upstream otp_gateway {
    server localhost:55155;
}

server {
    listen 443 ssl http2;
    server_name otp.example.com;

    ssl_certificate /etc/ssl/certs/otp.example.com.crt;
    ssl_certificate_key /etc/ssl/private/otp.example.com.key;

    location / {
        proxy_pass http://otp_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Traefik Configuration:**
```yaml
http:
  routers:
    otp-gateway:
      rule: \"Host(`otp.example.com`)\"
      service: otp-gateway-service
      tls:
        certResolver: letsencrypt

  services:
    otp-gateway-service:
      loadBalancer:
        servers:
          - url: \"http://localhost:55155\"
```

### 3. Monitoring Setup

**Prometheus Configuration (`prometheus.yml`):**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'otp-gateway'
    static_configs:
      - targets: ['otp-gateway:55155']
    metrics_path: '/metrics'
```

**Grafana Dashboard:**
- Import dashboard ID: Create custom
- Panels:
  - OTP Send Rate (rate(otp_sent_total[5m]))
  - Failure Rate (rate(otp_failed_total[5m]))
  - Rate Limit Hits (rate_limit_exceeded_total)

### 4. Logging

**Structured Logging to External Service:**
```python
# In app/config.py - add logging config
LOGGING = {
    'version': 1,
    'handlers': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    }
}
```

**Log Aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki + Grafana
- Datadog, Splunk, CloudWatch

---

## Security Hardening

### 1. Network Security

```bash
# Firewall rules (iptables)
iptables -A INPUT -p tcp --dport 55155 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP

# Or use cloud security groups
# Allow only: 55155 (API), 22 (SSH - restricted IPs)
```

### 2. Rate Limiting (Advanced)

For distributed rate limiting, use Redis:

```python
# In app/otp_service.py
import redis
from datetime import timedelta

redis_client = redis.Redis(host='redis', port=6379, db=0)

def check_rate_limit(chat_id: str) -> bool:
    key = f\"rate_limit:{chat_id}\"
    count = redis_client.incr(key)
    
    if count == 1:
        redis_client.expire(key, timedelta(hours=1))
    
    return count <= settings.rate_limit_per_user
```

### 3. API Authentication

Add API key authentication:

```python
# In app/main.py
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name=\"X-API-Key\")

@app.post(\"/send-otp\")
async def send_otp(
    request: Request, 
    otp_request: SendOTPRequest,
    api_key: str = Depends(API_KEY_HEADER)
):\n    if api_key != settings.api_key:
        raise HTTPException(status_code=401, detail=\"Invalid API key\")
    # ... rest of code
```

---

## Backup & Disaster Recovery

### 1. Service Redundancy

- Deploy in multiple availability zones
- Use load balancer with health checks
- Set up automatic failover

### 2. Bot Token Backup

- Store token in multiple secret managers
- Document bot recovery process:
  1. Access @BotFather
  2. Use `/token` to regenerate
  3. Update all instances

### 3. Monitoring & Alerts

**Alert Rules:**
```yaml
groups:
  - name: otp_gateway_alerts
    rules:
      - alert: HighFailureRate
        expr: rate(otp_failed_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: \"High OTP failure rate detected\"
      
      - alert: ServiceDown
        expr: up{job=\"otp-gateway\"} == 0
        for: 1m
        annotations:
          summary: \"OTP Gateway is down\"
```

---

## Performance Optimization

### 1. Connection Pooling

Already handled by `python-telegram-bot` - no action needed.

### 2. Caching

Cache bot verification:
```python
@lru_cache(maxsize=1)
async def verify_bot_token(self) -> bool:
    # ... existing code
```

### 3. Async Optimization

Ensure all I/O is async (already done in codebase).

---

## Scaling Strategy

### Horizontal Scaling

**Stateless Design:** Current implementation is stateless - perfect for scaling!

**Load Balancing:**
```bash
# HAProxy example
frontend otp_frontend
    bind *:55155
    default_backend otp_backend

backend otp_backend
    balance roundrobin
    server otp1 10.0.1.10:55155 check
    server otp2 10.0.1.11:55155 check
    server otp3 10.0.1.12:55155 check
```

**Autoscaling Triggers:**
- CPU > 70%
- Request rate > 100/sec per instance
- Queue depth > 50

---

## Cost Optimization

### 1. Telegram API Limits

- **Free tier:** 30 messages/second per bot
- **No cost** for bot usage
- Respect rate limits to avoid bans

### 2. Infrastructure Costs

**Single Instance:**
- CPU: 0.5 core
- RAM: 256 MB
- Cost: ~$5-10/month (cloud VM)

**Multi-Instance (3 replicas):**
- Cost: ~$15-30/month

**Serverless (Cloud Run/Lambda):**
- Pay per request
- Cost: ~$0.01 per 1000 OTPs

---

## Troubleshooting Production Issues

### Issue: High Latency

**Diagnosis:**
```bash
curl -w \"\\nTime: %{time_total}s\\n\" http://localhost:55155/health
```

**Solutions:**
- Check Telegram API status
- Verify network connectivity
- Scale horizontally

### Issue: Memory Leaks

**Diagnosis:**
```bash
docker stats otp-gateway
```

**Solutions:**
- Set memory limits in Docker
- Monitor with Prometheus
- Restart containers periodically

### Issue: Telegram API Errors

**Common errors:**
- `429 Too Many Requests`: Slow down sending
- `401 Unauthorized`: Invalid token
- `400 Bad Request`: Check chat_id format

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review logs for errors
- Check disk space
- Verify metrics

**Monthly:**
- Update dependencies
- Review security advisories
- Backup configuration

**Quarterly:**
- Load testing
- Security audit
- Performance review

### Updating

```bash
# Zero-downtime update
docker build -t otp-social-gateway:v2 .
docker-compose up -d --no-deps --build otp-gateway
```

---

## Support & Resources

- **Telegram Bot API Status:** https://telegram.org/blog
- **Docker Hub:** Store production images
- **Monitoring:** Prometheus + Grafana
- **Logs:** Centralized logging (ELK, Loki)

---

**Deployment Checklist:**

- [ ] Production image built and tested
- [ ] Secrets configured securely
- [ ] HTTPS enabled via reverse proxy
- [ ] Monitoring and alerts set up
- [ ] Backups configured
- [ ] Documentation updated
- [ ] Team trained on operations
- [ ] Incident response plan ready

**You're production-ready! 🚀**
