# Microservice Pipelines - End-to-End DevOps Project

A complete **CI/CD, IaC, and observability** pipeline for deploying a Python microservice to AWS with Kubernetes, Prometheus monitoring, and automated testing.

## 📋 Project Overview

This project demonstrates a production-grade microservices architecture with:
- **Application**: Flask API with Prometheus metrics
- **Infrastructure**: AWS VPC, EC2, provisioned with Terraform
- **Container Orchestration**: Kubernetes (K3s) with rolling deployments
- **Observability**: Prometheus + Node Exporter monitoring
- **CI/CD**: GitHub Actions for automated testing, building, and deployment
- **Infrastructure Automation**: Ansible for node setup
- **Security**: Non-root container users, security scanning, RBAC

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         GitHub Repository                       │
│  ┌─────────────────────────────────────────┐   │
│  │  GitHub Actions CI/CD Pipeline          │   │
│  │  • Run Tests (Python unittest)          │   │
│  │  • Build Docker Image                   │   │
│  │  • Security Scan (Trivy)                │   │
│  │  • Push to Docker Hub                   │   │
│  │  • Deploy to Kubernetes                 │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│           AWS Infrastructure                     │
│  ┌────────────────────────────────────────┐    │
│  │  VPC (10.0.0.0/16)                    │    │
│  │  ├─ Public Subnet (10.0.1.0/24)       │    │
│  │  └─ EC2 Instance (t3.small)           │    │
│  │     └─ K3s Cluster                    │    │
│  │        ├─ capstone-app (2 replicas)   │    │
│  │        ├─ Prometheus                  │    │
│  │        └─ Node Exporter               │    │
│  └────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
.
├── app/                          # Flask Application
│   ├── app.py                   # Main application with error handling
│   ├── test_app.py              # Unit tests
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile               # Multi-stage Docker build
│
├── k8s/                         # Kubernetes Manifests
│   ├── deployment.yaml          # App deployment (2 replicas)
│   └── service.yaml             # NodePort service (port 30080)
│
├── terraform/                   # AWS Infrastructure
│   ├── main.tf                  # VPC, EC2, Security Groups
│   ├── variables.tf             # Input variables with defaults
│   └── outputs.tf               # Outputs (public IP, instance ID)
│
├── ansible/                     # Configuration Management
│   ├── playbooks/setup.yml      # K3s + Node Exporter setup
│   └── inventory.ini            # Ansible hosts
│
├── monitoring/                  # Observability
│   └── prometheus.yml           # Prometheus scrape config
│
├── .github/workflows/           # CI/CD Pipeline
│   └── deploy.yml               # GitHub Actions workflow
│
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Git
- Docker & Docker Compose (for local testing)
- Terraform >= 1.6.0
- Ansible >= 2.9
- kubectl >= 1.24
- AWS Account with credentials configured
- Docker Hub account

### 1. Clone Repository

```bash
git clone https://github.com/Naveensa27/microservice-pipelines-end-to-end.git
cd microservice-pipelines-end-to-end
```

### 2. Test Locally

```bash
cd app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest discover -s .

# Run application
python app.py
# Visit http://localhost:5000 (health check)
# Visit http://localhost:5000/metrics (Prometheus metrics)
# Visit http://localhost:5000/health (liveness probe)
```

### 3. Build Docker Image

```bash
docker build -t capstone-app:latest app/
docker run -p 5000:5000 capstone-app:latest
```

### 4. Deploy to AWS

#### Step 4.1: Configure AWS Infrastructure

```bash
cd terraform

# Create terraform.tfvars with your values
cat > terraform.tfvars <<EOF
aws_region       = "us-east-1"
environment      = "production"
key_name         = "your-ec2-key-pair"  # Must exist in AWS
allowed_ssh_cidr = "YOUR_IP/32"         # Your public IP for SSH
instance_type    = "t3.small"
ami_id           = "ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS
EOF

# Initialize and apply Terraform
terraform init
terraform plan
terraform apply

# Save outputs
terraform output -json > ../outputs.json
```

#### Step 4.2: Configure Ansible

```bash
cd ansible

# Update inventory with instance public IP
sed -i "s/YOUR_INSTANCE_PUBLIC_IP/$(cat ../outputs.json | jq -r '.node_public_ip.value')/g" inventory.ini

# Run playbook to setup K3s and monitoring
ansible-playbook -i inventory.ini playbooks/setup.yml
```

#### Step 4.3: Get Kubeconfig

```bash
# From your local machine
INSTANCE_IP=$(cat outputs.json | jq -r '.node_public_ip.value')
ssh -i ~/.ssh/your-key.pem ubuntu@$INSTANCE_IP "cat /etc/rancher/k3s/k3s.yaml" > ~/.kube/k3s-config.yaml

# Update server IP in kubeconfig
sed -i "s/127.0.0.1/$INSTANCE_IP/g" ~/.kube/k3s-config.yaml

# Set as default
export KUBECONFIG=~/.kube/k3s-config.yaml
kubectl get nodes  # Verify connection
```

#### Step 4.4: Deploy Application

```bash
# Update deployment image tag
sed -i "s|DOCKERHUB_USERNAME/capstone-app:IMAGE_TAG|YOUR_DOCKERHUB_USERNAME/capstone-app:latest|g" k8s/deployment.yaml

# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check deployment status
kubectl rollout status deployment/capstone-app --timeout=120s
kubectl get pods
kubectl get svc
```

### 5. Access Application

```bash
# Get NodePort service external IP
INSTANCE_IP=$(cat ../outputs.json | jq -r '.node_public_ip.value')

# Access endpoints
curl http://$INSTANCE_IP:30080/         # Health check
curl http://$INSTANCE_IP:30080/metrics  # Prometheus metrics
curl http://$INSTANCE_IP:30080/health   # Liveness probe
```

---

## 🔧 Configuration

### Environment Variables

The application supports the following environment variables:

```bash
APP_HOST="0.0.0.0"           # Bind address (default: 0.0.0.0)
APP_PORT="5000"              # Port number (default: 5000)
APP_ENV="production"         # Environment (development/production, default: development)
```

Example:
```bash
export APP_ENV=production
export APP_PORT=8080
python app.py
```

### Terraform Variables

Edit `terraform/terraform.tfvars`:

```hcl
aws_region       = "us-east-1"
environment      = "production"
vpc_cidr         = "10.0.0.0/16"
subnet_cidr      = "10.0.1.0/24"
instance_type    = "t3.small"
key_name         = "your-ec2-key-pair"
allowed_ssh_cidr = "0.0.0.0/0"  # Change to your IP for security
```

### GitHub Secrets

Set these secrets in your GitHub repository (Settings → Secrets):

```
DOCKERHUB_USERNAME     # Your Docker Hub username
DOCKERHUB_TOKEN        # Docker Hub access token
KUBECONFIG            # Base64-encoded kubeconfig for deployment
```

To encode kubeconfig:
```bash
cat ~/.kube/k3s-config.yaml | base64 | tr -d '\n' | pbcopy
```

---

## 📊 Monitoring

### Prometheus Dashboard

Access Prometheus on the instance:
```
http://$INSTANCE_IP:9090
```

### Key Metrics

- `http_requests_total` - Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request latency distribution
- `app_errors_total` - Application errors by type
- `node_*` - Node Exporter system metrics

### Prometheus Configuration

Update `monitoring/prometheus.yml` with your instance IP:

```yaml
scrape_configs:
  - job_name: 'capstone-app'
    static_configs:
      - targets: ['YOUR_INSTANCE_IP:30080']
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['YOUR_INSTANCE_IP:9100']
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On Push/PR to main**:
   - Checkout code
   - Run Python tests
   - Build Docker image
   - Scan for vulnerabilities (Trivy)
   - Push to Docker Hub

2. **On Push to main** (after successful build):
   - Deploy to Kubernetes cluster
   - Update deployment with new image tag
   - Verify rollout status

### Workflow Triggers

```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```

---

## 🧪 Testing

### Run Unit Tests

```bash
cd app
python -m unittest discover -s .
```

### Test Coverage

```bash
cd app
pip install coverage
coverage run -m unittest discover -s .
coverage report
coverage html  # generates htmlcov/index.html
```

### Available Tests

- `test_healthcheck` - Verify health endpoint returns 200
- `test_metrics_endpoint` - Verify metrics are generated
- `test_health_endpoint` - Verify dedicated health check
- `test_404_endpoint` - Verify 404 handling
- `test_environment_variable_in_response` - Verify env in response

---

## 🔒 Security Features

✅ **Container Security**
- Non-root user (UID 10001)
- Multi-stage build (smaller image size)
- Minimal base image (python:3.12-slim)

✅ **Kubernetes Security**
- Security context with runAsNonRoot
- Resource limits and requests
- Health probes (liveness & readiness)

✅ **Infrastructure Security**
- VPC isolation
- Security group ingress rules
- SSH key-based authentication

✅ **Pipeline Security**
- Vulnerability scanning (Trivy)
- Secrets management via GitHub Secrets
- HTTPS for Docker registry

---

## 📝 Troubleshooting

### Issue: Tests fail locally

```bash
# Make sure you're in the app directory
cd app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Run tests with verbose output
python -m unittest discover -s . -v
```

### Issue: Docker build fails

```bash
# Check Docker daemon is running
docker ps

# Build with verbose output
docker build --progress=plain -t capstone-app:latest app/
```

### Issue: Kubernetes deployment fails

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs deployment/capstone-app

# Check events
kubectl get events
```

### Issue: Connection to cluster fails

```bash
# Verify kubeconfig
kubectl config view

# Test connection
kubectl get nodes

# Verify service is accessible
kubectl get svc capstone-app-service
curl http://$INSTANCE_IP:30080/
```

---

## 🛠️ Maintenance

### Update Python Dependencies

```bash
# Update requirements.txt
pip install --upgrade Flask prometheus-client gunicorn
pip freeze > app/requirements.txt
```

### Update Docker Image

```bash
# Rebuild and push
docker build -t YOUR_USERNAME/capstone-app:latest app/
docker push YOUR_USERNAME/capstone-app:latest

# Trigger rollout
kubectl rollout restart deployment/capstone-app
```

### Scale Deployment

```bash
# Scale to 3 replicas
kubectl scale deployment capstone-app --replicas=3

# Or edit deployment
kubectl edit deployment capstone-app
```

---

## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Prometheus Metrics](https://prometheus.io/docs/instrumenting/exposition_formats/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Ansible Documentation](https://docs.ansible.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👤 Contributing

Contributions are welcome! Please:
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

---

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review GitHub Issues
- Create a new issue with detailed description

---

**Last Updated**: July 2026  
**Author**: DevOps Team  
**Status**: Production Ready ✅
