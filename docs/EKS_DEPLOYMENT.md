# EKS Deployment Guide

A comprehensive guide to deploying applications on Amazon EKS (Elastic Kubernetes Service).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Key Concepts](#key-concepts)
3. [Tool Installation](#tool-installation)
4. [IAM Permissions](#iam-permissions)
5. [Cluster Creation](#cluster-creation)
6. [Deploying Applications](#deploying-applications)
7. [Accessing Your Application](#accessing-your-application)
8. [Cleanup (Cost Saving)](#cleanup-cost-saving)
9. [Cost Reference](#cost-reference)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Purpose | Check Command |
|------|---------|---------------|
| AWS CLI | Interact with AWS services | `aws --version` |
| kubectl | Manage Kubernetes resources | `kubectl version --client` |
| eksctl | Create/manage EKS clusters | `eksctl version` |
| Docker | Build container images | `docker --version` |

---

## Key Concepts

### AWS vs Kubernetes Terminology

| AWS Term | Kubernetes Term | Description |
|----------|-----------------|-------------|
| EKS Cluster | Cluster | Group of nodes running Kubernetes |
| EC2 Instance | Node | Worker machine running pods |
| - | Pod | Smallest unit (1+ containers) |
| - | Deployment | Manages pod replicas |
| Load Balancer | Service (LoadBalancer) | Exposes pods externally |
| ECR | Container Registry | Stores Docker images |

### Tool Comparison

| Tool | Purpose | Analogy |
|------|---------|---------|
| kubectl | Manage K8s resources (pods, services) | Like `git` commands |
| eksctl | Create/delete EKS clusters | Like creating a GitHub repo |
| aws cli | General AWS operations | Like AWS console in terminal |

### Kubernetes Resource Hierarchy

```
Cluster
  └── Namespace (logical grouping)
        └── Deployment (manages replicas)
              └── ReplicaSet (maintains pod count)
                    └── Pod (runs containers)
                          └── Container (your app)
```

### EKS Architecture Deep Dive

#### What is Amazon EKS?

**EKS = Elastic Kubernetes Service** - AWS-managed Kubernetes that handles the control plane complexity.

```
+------------------------------------------------------------------+
|                         YOUR AWS ACCOUNT                          |
|  +---------------------------+   +----------------------------+   |
|  |     EKS CONTROL PLANE     |   |       WORKER NODES         |   |
|  |      (AWS Managed)        |   |     (You manage EC2s)      |   |
|  |  - API Server             |   |  +--------+  +--------+    |   |
|  |  - etcd (data store)      |   |  |  Pod   |  |  Pod   |    |   |
|  |  - Scheduler              |   |  | (app)  |  | (app)  |    |   |
|  |  - Controller Manager     |   |  +--------+  +--------+    |   |
|  +---------------------------+   +----------------------------+   |
+------------------------------------------------------------------+
```

#### EKS Control Plane Components

| Component | Purpose |
|-----------|---------|
| **API Server** | Entry point for all kubectl commands |
| **etcd** | Key-value store for cluster state |
| **Scheduler** | Decides which node runs each pod |
| **Controller Manager** | Maintains desired state (replicas, etc.) |

**Cost:** $0.10/hour (~$72/month) per cluster

#### Node Groups

| Type | Description | Use Case |
|------|-------------|----------|
| **Managed Node Group** | AWS handles updates/scaling | Production (recommended) |
| **Self-Managed Nodes** | You manage EC2 instances | Custom AMIs needed |
| **Fargate** | Serverless (no EC2) | Variable workloads |

#### AWS CloudFormation

**CloudFormation** = Infrastructure-as-Code service that eksctl uses internally.

When you run `eksctl create cluster`, it creates CloudFormation stacks:

| Stack Name | Resources Created |
|------------|-------------------|
| `eksctl-CLUSTER-cluster` | VPC, Subnets, EKS Control Plane, IAM Roles |
| `eksctl-CLUSTER-nodegroup-NODES` | EC2 instances, Auto Scaling Group |

**View stacks:**
```powershell
aws cloudformation list-stacks --query "StackSummaries[?contains(StackName,'eksctl')]"
```

#### Auto Scaling Groups (ASG)

Node Groups use ASG to manage EC2 instances:

| Parameter | Description |
|-----------|-------------|
| `--nodes` | Desired number of nodes |
| `--nodes-min` | Minimum nodes (scale down limit) |
| `--nodes-max` | Maximum nodes (scale up limit) |

#### Fleet Requests

AWS internal process for provisioning EC2 instances.

**Common Error:** "You've reached your quota for maximum Fleet Requests"
**Solution:** Request quota increase or delete unused ASGs/clusters.

#### Complete Resource Flow

```
eksctl create cluster
         ↓
CloudFormation Stack 1 (Cluster) → VPC, Subnets, EKS Control Plane
         ↓
CloudFormation Stack 2 (NodeGroup) → Auto Scaling Group → EC2 Nodes
         ↓
Kubernetes Objects → Deployment → Pods → Your App
```

---

## Tool Installation

### Install kubectl (Windows)

```powershell
# Download
Invoke-WebRequest -Uri "https://dl.k8s.io/release/v1.28.2/bin/windows/amd64/kubectl.exe" -OutFile "kubectl.exe"

# Move to PATH
Move-Item -Path .\kubectl.exe -Destination "C:\Windows\System32\kubectl.exe"

# Verify
kubectl version --client
```

### Install eksctl (Windows)

```powershell
# Download
Invoke-WebRequest -Uri "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Windows_amd64.zip" -OutFile "eksctl.zip"

# Extract
Expand-Archive -Path .\eksctl.zip -DestinationPath . -Force

# Move to PATH (run as Administrator)
Move-Item -Path .\eksctl.exe -Destination "C:\Windows\System32\eksctl.exe" -Force

# Verify
eksctl version
```

---

## IAM Permissions

### What is IAM?

**IAM = Identity and Access Management**

It controls WHO can do WHAT in your AWS account.

| Concept | Meaning | Example |
|---------|---------|---------|
| **User** | A person or service | `dvc-s3-user` |
| **Policy** | Set of permissions | "Can read/write to S3" |
| **Role** | Temporary permissions | "EC2 can pull from ECR" |

### Required Policies for EKS

For eksctl to create a complete EKS cluster, the IAM user needs:

| Policy | Purpose |
|--------|---------|
| AdministratorAccess | Full access (easiest for demos) |

Or individually:

| Policy | What It Allows | Why Needed |
|--------|----------------|------------|
| AmazonEKSClusterPolicy | Create/manage EKS clusters | Core EKS operations |
| AmazonEKSWorkerNodePolicy | Join nodes to cluster | Nodes need this to work |
| AmazonEKSServicePolicy | EKS service operations | Internal EKS communication |
| AmazonEC2FullAccess | Create/manage EC2 instances | EKS nodes are EC2 |
| IAMFullAccess | Create IAM roles | eksctl creates service roles |
| AWSCloudFormationFullAccess | Create CloudFormation stacks | eksctl uses this internally |

### Adding Policies via CLI

```powershell
aws iam attach-user-policy --user-name YOUR_USER --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Verify Attached Policies

```powershell
aws iam list-attached-user-policies --user-name YOUR_USER
```

---

## AWS Networking Concepts (Beginner Guide)

### VPC (Virtual Private Cloud)

**Think of it as:** Your own private data center in AWS.

```
+------------------------------------------+
|               YOUR VPC                    |
|  (Isolated network, e.g., 10.0.0.0/16)   |
|                                           |
|   +------------+    +------------+        |
|   |  Subnet 1  |    |  Subnet 2  |        |
|   | (Public)   |    | (Private)  |        |
|   +------------+    +------------+        |
|                                           |
+------------------------------------------+
```

| Property | Value |
|----------|-------|
| IP Range | e.g., `10.0.0.0/16` (65,536 IPs) |
| Isolation | Completely separate from other VPCs |
| Control | You control firewall rules |

### Subnets

**Think of it as:** Rooms inside your data center.

| Type | Purpose | Internet Access |
|------|---------|-----------------|
| **Public Subnet** | Web servers, load balancers | Yes (via Internet Gateway) |
| **Private Subnet** | Databases, internal apps | No (more secure) |

**EKS uses:**
- Public subnets for Load Balancer (user-facing)
- Private subnets for worker nodes (more secure)

### Security Groups

**Think of it as:** Firewall rules for each resource.

| Rule | From | To | Port | Allow? |
|------|------|----|----|--------|
| Inbound | Internet | Load Balancer | 80 | Yes |
| Inbound | Load Balancer | Pods | 5000 | Yes |
| Outbound | All | All | All | Yes |

### How Traffic Flows (Visual)

```
Internet
    |
    v
+-------------------+
| Internet Gateway  |  <-- Entry point to VPC
+-------------------+
    |
    v
+-------------------+
| Load Balancer     |  <-- Public Subnet
+-------------------+
    |
    v
+-------------------+
| EKS Worker Node   |  <-- Private Subnet
| (runs your pods)  |
+-------------------+
    |
    v
+-------------------+
| ECR (Docker imgs) |  <-- AWS managed
+-------------------+
```

### What eksctl Creates (Detailed)

When you run `eksctl create cluster`, it creates:

| Resource | Count | Purpose |
|----------|-------|---------|
| VPC | 1 | Isolated network |
| Subnets | 6 | 3 public + 3 private (across 3 AZs) |
| Internet Gateway | 1 | Internet access for public subnets |
| NAT Gateway | 3 | Internet access for private subnets |
| Route Tables | 4 | Traffic routing rules |
| Security Groups | 3+ | Firewall rules |
| EKS Cluster | 1 | Kubernetes control plane |
| Node Group | 1 | EC2 worker nodes |
| IAM Roles | 2 | Cluster role + Node role |

---

## Cluster Creation

### Basic Cluster Command

```powershell
eksctl create cluster \
  --name deepguard-cluster \
  --region us-east-1 \
  --nodegroup-name deepguard-nodes \
  --node-type t3.small \
  --nodes 1 \
  --nodes-min 1 \
  --nodes-max 1 \
  --managed
```

### Flag Explanation

| Flag | Value | Purpose |
|------|-------|---------|
| --name | deepguard-cluster | Cluster name |
| --region | us-east-1 | AWS region |
| --nodegroup-name | deepguard-nodes | Node group name |
| --node-type | t3.small | EC2 instance type (~$0.02/hr) |
| --nodes | 1 | Initial node count |
| --nodes-min | 1 | Minimum nodes (autoscaling) |
| --nodes-max | 1 | Maximum nodes (autoscaling) |
| --managed | - | AWS manages node updates |

### What Gets Created

eksctl creates these AWS resources:

1. **CloudFormation Stacks** - Infrastructure templates
2. **VPC** - Virtual Private Cloud with subnets
3. **EKS Control Plane** - Kubernetes master (managed by AWS)
4. **Node Group** - EC2 instances as worker nodes
5. **IAM Roles** - Service roles for cluster operations
6. **Security Groups** - Network access rules

### Creation Time

- Total: 15-20 minutes
- Control Plane: ~10 minutes
- Node Group: ~5 minutes

---

## Deploying Applications

### Step 1: Create deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deepguard-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: deepguard
  template:
    metadata:
      labels:
        app: deepguard
    spec:
      containers:
      - name: deepguard
        image: YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/deepguard-app:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Step 2: Create service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: deepguard-service
spec:
  type: LoadBalancer
  selector:
    app: deepguard
  ports:
  - port: 80
    targetPort: 5000
```

### Step 3: Apply to Cluster

```powershell
# Apply deployment
kubectl apply -f deployment.yaml

# Apply service
kubectl apply -f service.yaml

# Check pods
kubectl get pods

# Check service (get external URL)
kubectl get service deepguard-service
```

---

## Accessing Your Application

### Get LoadBalancer URL

```powershell
kubectl get service deepguard-service
```

Look for the `EXTERNAL-IP` column. It will show a URL like:
`a1b2c3d4-1234567890.us-east-1.elb.amazonaws.com`

Open this URL in your browser to access your app.

### Common kubectl Commands

| Command | Purpose |
|---------|---------|
| `kubectl get pods` | List all pods |
| `kubectl get services` | List all services |
| `kubectl get deployments` | List all deployments |
| `kubectl describe pod POD_NAME` | Pod details |
| `kubectl logs POD_NAME` | View pod logs |
| `kubectl delete pod POD_NAME` | Delete a pod |

---

## Cleanup (Cost Saving)

### IMPORTANT: Delete Cluster After Demo

EKS costs money every hour. Always delete when done:

```powershell
eksctl delete cluster --name deepguard-cluster --region us-east-1
```

This deletes:
- EKS cluster
- All EC2 nodes
- Load balancers
- VPC and subnets
- CloudFormation stacks

### Deletion Time: 5-10 minutes

### Verify Deletion

```powershell
aws eks list-clusters --region us-east-1
```

Should return empty: `{ "clusters": [] }`

---

## Cost Reference

### EKS Pricing

| Resource | Cost | Notes |
|----------|------|-------|
| EKS Control Plane | $0.10/hour | ~$2.40/day |
| t3.small EC2 node | $0.02/hour | ~$0.50/day |
| Load Balancer | $0.025/hour | ~$0.60/day |
| **Total** | **~$0.15/hour** | **~$3.50/day** |

### Cost-Saving Tips

1. Use `t3.small` or `t3.micro` for demos
2. Keep only 1 node for testing
3. Delete cluster immediately after demo
4. Use spot instances for non-production

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| AccessDeniedException | Missing IAM permissions | Add AdministratorAccess |
| Cluster not found | kubectl not configured | Run `aws eks update-kubeconfig` |
| ImagePullBackOff | Can't pull Docker image | Check ECR permissions |
| Pending pods | Node capacity issue | Check node resources |
| **OOMKilled** | Container out of memory | Increase memory limits (see below) |
| CrashLoopBackOff | Container keeps crashing | Check logs with `kubectl logs POD_NAME` |

### OOMKilled Fix (Common Issue)

TensorFlow models require more memory than default limits. If you see `OOMKilled` in pod describe:

```powershell
kubectl describe pod POD_NAME
# Look for: Reason: OOMKilled
```

**Fix:** Increase memory limits in deployment.yaml:

```yaml
resources:
  requests:
    memory: "512Mi"    # Minimum memory
    cpu: "250m"
  limits:
    memory: "1536Mi"   # Maximum memory (1.5Gi for TensorFlow)
    cpu: "1000m"
```

Then apply and restart:

```powershell
kubectl apply -f k8s/deployment.yaml
kubectl rollout restart deployment YOUR_APP
```

### Verify kubectl Config

```powershell
# Update kubectl config
aws eks update-kubeconfig --name deepguard-cluster --region us-east-1

# Test connection
kubectl get nodes
```

### Check Cluster Status

```powershell
# List clusters
aws eks list-clusters --region us-east-1

# Describe cluster
aws eks describe-cluster --name deepguard-cluster --region us-east-1
```

---

## Quick Reference Commands

```powershell
# Create cluster
eksctl create cluster --name CLUSTER_NAME --region REGION --node-type t3.small --nodes 1 --managed

# Configure kubectl
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION

# Deploy app
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs POD_NAME

# Delete cluster (IMPORTANT!)
eksctl delete cluster --name CLUSTER_NAME --region REGION
```

---

## DeepGuard Deployment Walkthrough

This is the exact sequence of commands used to deploy DeepGuard to EKS.

### 1. Create EKS Cluster

```powershell
eksctl create cluster --name deepguard-cluster --region us-east-1 --nodegroup-name deepguard-nodes --node-type t3.small --nodes 1 --nodes-min 1 --nodes-max 1 --managed
```

### 2. Verify Cluster

```powershell
kubectl get nodes
# Expected: 1 node in "Ready" status
```

### 3. Build and Push Docker Image

```powershell
# Build
docker build -t deepguard-app:latest .

# Tag for ECR
docker tag deepguard-app:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/deepguard-app:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Push
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/deepguard-app:latest
```

### 4. Deploy to Cluster

```powershell
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 5. Get LoadBalancer URL

```powershell
kubectl get services
# Look for EXTERNAL-IP column
```

### 6. Verify and Debug

```powershell
# Check pods
kubectl get pods

# Check logs
kubectl logs -l app=deepguard

# Describe pod for errors
kubectl describe pod POD_NAME
```

### 7. Update Deployment (if needed)

```powershell
# After changing deployment.yaml
kubectl apply -f k8s/deployment.yaml

# Force restart to pull new image
kubectl rollout restart deployment deepguard-app
```

### 8. Delete Cluster (IMPORTANT!)

```powershell
eksctl delete cluster --name deepguard-cluster --region us-east-1

# Verify deletion
aws eks list-clusters --region us-east-1
```

---

## Lessons Learned

### 1. Memory Limits for TensorFlow
TensorFlow models require at least 1-1.5Gi memory. Default 512Mi limits cause OOMKilled errors.

### 2. Model File in Docker Image
Ensure model files are **not** in `.dockerignore`. The Docker build must include all required model files.

### 3. IAM Permissions
For quick demos, `AdministratorAccess` is easiest. Remove it after deployment for security.

### 4. Rollout Restarts
After pushing a new image with the same tag (`:latest`), use `kubectl rollout restart` to force the cluster to pull the new image.

### 5. Cost Management
- Always delete cluster after demo
- Use `t3.small` (cheapest option that works)
- Keep nodes to minimum (1 for testing)

---

## Related Documentation

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [eksctl Documentation](https://eksctl.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
