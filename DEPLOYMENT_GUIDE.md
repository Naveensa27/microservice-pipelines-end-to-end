# GitHub Actions Deployment Guide

This guide explains how to set up your GitHub repository to deploy to Kubernetes via GitHub Actions.

## 🔧 Prerequisites

1. **Running Kubernetes Cluster** - Must be accessible from the internet
2. **kubectl** configured locally to connect to your cluster
3. **Docker Hub Account** - For storing Docker images

---

## 🚀 Step 1: Get Your Kubeconfig

Your kubeconfig file tells kubectl how to connect to your Kubernetes cluster.

### From Your Local Machine (if cluster is already running)

If you already provisioned AWS infrastructure and have K3s running:

```bash
# SSH into your EC2 instance
INSTANCE_IP="your-instance-ip"
ssh -i ~/.ssh/your-key.pem ubuntu@$INSTANCE_IP

# Copy the K3s kubeconfig
cat /etc/rancher/k3s/k3s.yaml
```

Copy the entire output.

### Update the Server IP

The kubeconfig will have `server: https://127.0.0.1:6443` but needs your instance's public IP:

```bash
# Replace 127.0.0.1 with your instance public IP
# Example:
# Before: server: https://127.0.0.1:6443
# After:  server: https://54.123.45.67:6443  (your actual instance IP)
```

---

## 🔐 Step 2: Encode Kubeconfig for GitHub Secrets

GitHub Secrets must be base64 encoded:

### On Linux/Mac:
```bash
cat ~/.kube/k3s-config.yaml | base64 | tr -d '\n'
```

### On Windows (PowerShell):
```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content ~/.kube/config -Raw))) | Set-Clipboard
```

Copy the entire base64 string.

---

## 🔑 Step 3: Add GitHub Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

### Secret 1: DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username
- Click **Add secret**

### Secret 2: DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: Your Docker Hub access token
  - Get it from: https://hub.docker.com/settings/security → Personal access tokens
  - Create new token with read/write access
- Click **Add secret**

### Secret 3: KUBECONFIG
- **Name**: `KUBECONFIG`
- **Value**: The base64-encoded kubeconfig from Step 2
- Click **Add secret**

---

## ✅ Verify Secrets Are Set

```bash
# In GitHub, go to Actions tab and look for environment variables
# You should see all three secrets listed
```

---

## 🚀 Step 4: Trigger the CI/CD Pipeline

Push a commit to main branch:

```bash
git push origin main
```

This will:
1. ✅ Run tests
2. ✅ Build Docker image
3. ✅ Scan for vulnerabilities
4. ✅ Push to Docker Hub
5. ✅ Deploy to Kubernetes (if kubeconfig is set)

---

## 📊 Monitor the Pipeline

1. Go to: https://github.com/YOUR_USERNAME/microservice-pipelines-end-to-end/actions
2. Click the latest workflow run
3. Watch each job:
   - ✅ **build-and-test** - Should complete first
   - ✅ **deploy-to-k8s** - Only runs if kubeconfig is configured

---

## 🔍 Troubleshooting

### Issue: Deploy job is skipped
**Cause**: KUBECONFIG secret is not set  
**Fix**: Add KUBECONFIG secret as described in Step 3

### Issue: "connection refused" error
**Cause**: kubeconfig points to wrong IP or cluster is offline  
**Fix**: Verify cluster is running and kubeconfig has correct IP

### Issue: "Unauthorized" error
**Cause**: kubeconfig user doesn't have permissions  
**Fix**: Verify kubeconfig is for a user with cluster admin permissions

### Issue: Docker push fails
**Cause**: DOCKERHUB_USERNAME or DOCKERHUB_TOKEN is wrong  
**Fix**: Verify Docker Hub credentials in secrets

---

## 📈 Next Steps

Once deployment succeeds:

```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# Check logs
kubectl logs deployment/capstone-app

# Test the app
curl http://<instance-ip>:30080/
curl http://<instance-ip>:30080/metrics
```

---

## 🛠️ Manual Deployment (Without CI/CD)

If you want to deploy manually without GitHub Actions:

```bash
# Update kubeconfig
export KUBECONFIG=~/.kube/k3s-config.yaml

# Verify connection
kubectl cluster-info

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify
kubectl rollout status deployment/capstone-app --timeout=120s
kubectl get pods
```

---

## 📝 Environment Setup Summary

| Component | Status | Action |
|-----------|--------|--------|
| Kubernetes Cluster | ⚠️ Manual setup | Run Terraform + Ansible |
| kubeconfig | ⚠️ Manual setup | Add as KUBECONFIG secret |
| Docker Hub Username | ⚠️ Manual setup | Add as DOCKERHUB_USERNAME secret |
| Docker Hub Token | ⚠️ Manual setup | Add as DOCKERHUB_TOKEN secret |
| GitHub Actions Workflow | ✅ Ready | Already configured |
| Application Code | ✅ Ready | Already optimized |

---

For more details, see [README.md](../README.md)
