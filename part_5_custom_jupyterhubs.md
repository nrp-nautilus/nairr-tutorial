# 5. Custom Hosted JupyterHubs (Instructor: Daniel Diaz)

The primary access mechanism we support for NAIRR Pilot Classroom usage on NRP is via JupyterHub. In this section we will provide information on how instructors/TAs can deploy custom JupyterHub instances. We will cover configuration aspects such as controlled access, custom software stacks/containers and resource scaling.

## Overview

This section covers how to deploy and manage JupyterHub environments for groups or courses. **Note: This section requires namespace admin privileges.**

## Prerequisites

- ✅ Namespace admin access
- ✅ Helm 3.x installed
- ✅ kubectl configured with admin access to your namespace
- ✅ Understanding of Kubernetes basics (from Beginner Track)

## Key Concepts

- **Helm Charts**: Package managers for Kubernetes applications
- **JupyterHub Helm Chart**: Pre-configured deployment for JupyterHub
- **Configuration**: Customize JupyterHub through YAML configuration files
- **Resource Management**: Set CPU, memory, and GPU limits per user
- **Storage**: Configure persistent storage for user home directories


## Section 4.1: Install Helm


If you're running inside a headless Linux environment (JupyterHub), this is a script to install and configure `kubectl` and `kubelogin`:

```bash
/bin/bash -c '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>/dev/null || true; eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" || eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)"; brew install -q kubectl; eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" || eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)"; brew install -q kubelogin; eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" || eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)"; wget -q http://nrp.ai/config -O ~/.kube/config; sed -i "s/      - --token-cache-storage=keyring/      - --token-cache-storage=disk/" ~/.kube/config; printf "\n      - --grant-type=device-code\n      - --skip-open-browser\n" >> ~/.kube/config; eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv 2>/dev/null)" || eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null)"; kubectl get node | head -n 5'
```

Then run:
```bash
source ~/.bashrc
```

First, ensure Helm is installed on your system:



```python
# Check if Helm is installed
helm version

```

If Helm is not installed, install it:

**macOS:**
```bash
brew install helm
```

**Linux:**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Windows:**
Download from https://helm.sh/docs/intro/install/


## Section 4.2: Add JupyterHub Helm Repository

Add the JupyterHub Helm repository:



```python
# Add JupyterHub Helm repository
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/

```


```python
# Update Helm repositories
helm repo update

```


```python
# Verify the repository was added
helm repo list

```

## Section 4.3: Basic JupyterHub Deployment

Link to full documentation: https://nrp.ai/documentation/userdocs/jupyter/jupyterhub/

Let's create a basic JupyterHub configuration. First, create a configuration file:


### Create Basic JupyterHub Configuration

Create a file called `jupyterhub-config.yaml`:



```python
hub:
  config:
    JupyterHub:
      authenticator_class: dummy
      admin_access: true
      admin_users: ["admin"]
    DummyAuthenticator:
      password: "training123"
    # Allow all users to sign in (for tutorial purposes)
    Authenticator:
      allowed_users: set()
  service:
    type: ClusterIP
    annotations: {}
    ports:
      nodePort:
    loadBalancerIP:
  deploymentStrategy:
    type: Recreate
  db:
    type: sqlite-pvc
    pvc:
      accessModes:
        - ReadWriteOnce
      storage: 1Gi
      storageClassName: rook-ceph-block
  resources:
    limits:
      cpu: "2"
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 512Mi
  networkPolicy:
    enabled: false
proxy:
  secretToken: 'secret_token'
  service:
    type: ClusterIP
  chp:
    resources:
      limits:
        cpu: "6"
        memory: 10Gi
      requests:
        cpu: "1"
        memory: 512Mi
singleuser:
  uid: 0
  fsGid: 100
  extraEnv:
    GRANT_SUDO: "yes"
  extraPodConfig:
    securityContext:
        fsGroupChangePolicy: "OnRootMismatch"
        fsGroup: 100
  extraNodeAffinity:
    required:
      - matchExpressions:
        - 'key': 'topology.kubernetes.io/region'
          'operator': 'In'
          'values': ["us-west"]
  cloudMetadata:
    blockWithIptables: false
  networkPolicy:
    enabled: false
  storage:
    type: dynamic
    extraLabels: {}
    extraVolumes: []
    extraVolumeMounts: []
    capacity: 5Gi
    homeMountPath: /home/jovyan
    dynamic:
      storageClass: rook-ceph-block
      pvcNameTemplate: claim-{username}{servername}
      volumeNameTemplate: volume-{username}{servername}
      storageAccessModes: [ReadWriteOnce]
  image:
    name: quay.io/jupyter/scipy-notebook
    tag: 2024-04-22
  startTimeout: 600
  cpu:
    limit: 3
    guarantee: 3
  memory:
    limit: 10G
    guarantee: 10G
  extraResource:
    limits: {}
    guarantees: {}
  cmd: null
  defaultUrl: "/lab"
  profileList:
  - display_name: Scipy
    kubespawner_override:
      image_spec: quay.io/jupyter/scipy-notebook:2024-04-22
    default: True
  - display_name: R
    kubespawner_override:
      image_spec: quay.io/jupyter/r-notebook:2024-04-22
  - display_name: Julia
    kubespawner_override:
      image_spec: quay.io/jupyter/julia-notebook:2024-04-22
  - display_name: Tensorflow
    kubespawner_override:
      image_spec: quay.io/jupyter/tensorflow-notebook:cuda-2024-04-22
  - display_name: Pytorch
    kubespawner_override:
      image_spec: quay.io/jupyter/pytorch-notebook:cuda12-2024-04-22
  - display_name: Datascience (scipy, Julia, R)
    kubespawner_override:
      image_spec: quay.io/jupyter/datascience-notebook:2024-04-22
  - display_name: Pyspark
    kubespawner_override:
      image_spec: quay.io/jupyter/pyspark-notebook:2024-04-22
  - display_name: All Spark
    kubespawner_override:
      image_spec: quay.io/jupyter/all-spark-notebook:2024-04-22
  - display_name: B-Data python scipy
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/python/scipy:3
  - display_name: B-Data Julia
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/julia/base:1
  - display_name: B-Data R
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/r/base:4
  - display_name: B-Data R tidyverse
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/r/tidyverse:4
  - display_name: B-Data R verse
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/r/verse:4
  - display_name: B-Data R geospatial
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/r/geospatial:4
  - display_name: B-Data R qgisprocess
    kubespawner_override:
      image_spec: glcr.b-data.ch/jupyterlab/cuda/r/qgisprocess:4

scheduling:
  userScheduler:
    enabled: false
  userPlaceholder:
    enabled: false
# prePuller relates to the hook|continuous-image-puller DaemonsSets
prePuller:
  hook:
    enabled: false
  continuous:
    enabled: false


cull:
  enabled: true
  users: false
  removeNamedServers: false
  timeout: 3600
  every: 600
  concurrency: 10
  maxAge: 0
```

### Generate Secret Token

Before deploying, you need to generate a secret token for the proxy:



```python
# Generate a secret token
openssl rand -hex 32

```

**Important**: Replace `REPLACE_WITH_GENERATED_TOKEN` in the `jupyterhub-config.yaml` file with the token generated above.


### Deploy JupyterHub

Now deploy JupyterHub using Helm. **Important**: Replace `<namespace>` with your namespace name.



```python
# Deploy JupyterHub
# Replace <namespace> with your namespace
# Replace <release-name> with a name for your JupyterHub instance (e.g., jhub-basic)

helm upgrade --cleanup-on-fail --install <release-name> jupyterhub/jupyterhub \
    --namespace <namespace> \
    --version=3.3.7 \
    --values jupyterhub-config.yaml \
    --wait \
    --timeout=10m

```


```python
# Check deployment status
kubectl get pods -n <namespace>

```


```python
# Check services
kubectl get services -n <namespace>

```

## Section 4.4: Configure Ingress

To make JupyterHub accessible via a URL, create an Ingress resource:


### Create Ingress Configuration

Add the following to your `jupyterhub-config.yaml` or create a separate ingress file:



```python
ingress:
  enabled: true
  ingressClassName: haproxy
  hosts: ["<your-jupyterhub-name>.nrp-nautilus.io"]
  pathSuffix: ''
  tls:
    - hosts:
      - <your-jupyterhub-name>.nrp-nautilus.io

```

**Note**: Replace `<your-jupyterhub-name>` with your desired subdomain. You may need to coordinate with NRP administrators to set up the DNS.

After adding the ingress configuration, upgrade your Helm release:



```python
# Upgrade the deployment with ingress configuration
helm upgrade <release-name> jupyterhub/jupyterhub \
    --namespace <namespace> \
    --version=3.3.7 \
    --values jupyterhub-config.yaml \
    --wait \
    --timeout=10m

```


```python
# Check ingress status
kubectl get ingress -n <namespace>

```

## Section 4.5: Advanced Configuration

### Multiple Image Profiles

You can configure multiple image options for users to choose from. Add this to your `jupyterhub-config.yaml`:



```python
singleuser:
  profileList:
  - display_name: Scipy
    kubespawner_override:
      image_spec: quay.io/jupyter/scipy-notebook:2024-04-22
    default: True
  - display_name: R
    kubespawner_override:
      image_spec: quay.io/jupyter/r-notebook:2024-04-22
  - display_name: Julia
    kubespawner_override:
      image_spec: quay.io/jupyter/julia-notebook:2024-04-22
  - display_name: Tensorflow
    kubespawner_override:
      image_spec: quay.io/jupyter/tensorflow-notebook:cuda-2024-04-22
  - display_name: Pytorch
    kubespawner_override:
      image_spec: quay.io/jupyter/pytorch-notebook:cuda12-2024-04-22
  - display_name: Datascience (scipy, Julia, R)
    kubespawner_override:
      image_spec: quay.io/jupyter/datascience-notebook:2024-04-22

```

### Resource Limits per Profile

You can also set different resource limits for different profiles:



```python
singleuser:
  profileList:
  - display_name: Small (2 CPU, 4GB RAM)
    kubespawner_override:
      image_spec: quay.io/jupyter/scipy-notebook:2024-04-22
      cpu_limit: 2
      cpu_guarantee: 2
      mem_limit: 4G
      mem_guarantee: 4G
  - display_name: Medium (4 CPU, 8GB RAM)
    kubespawner_override:
      image_spec: quay.io/jupyter/scipy-notebook:2024-04-22
      cpu_limit: 4
      cpu_guarantee: 4
      mem_limit: 8G
      mem_guarantee: 8G
  - display_name: Large (8 CPU, 16GB RAM)
    kubespawner_override:
      image_spec: quay.io/jupyter/scipy-notebook:2024-04-22
      cpu_limit: 8
      cpu_guarantee: 8
      mem_limit: 16G
      mem_guarantee: 16G

```

## Section 4.6: Managing JupyterHub

### Check JupyterHub Status



```python
# List all Helm releases in your namespace
helm list -n <namespace>

```


```python
# Check JupyterHub hub pod logs
kubectl logs -n <namespace> -l app=jupyterhub,component=hub --tail=50

```


```python
# Check all user pods
kubectl get pods -n <namespace> -l app=jupyterhub,component=singleuser-server

```

### Update JupyterHub Configuration

To update your JupyterHub configuration:

1. Edit your `jupyterhub-config.yaml` file
2. Upgrade the Helm release:



```python
# Upgrade JupyterHub with new configuration
helm upgrade <release-name> jupyterhub/jupyterhub \
    --namespace <namespace> \
    --version=3.3.7 \
    --values jupyterhub-config.yaml \
    --wait \
    --timeout=10m

```

### Uninstall JupyterHub

To remove JupyterHub (and optionally all user data):



```python
# Uninstall JupyterHub (this will delete the hub and proxy, but NOT user data)
helm uninstall <release-name> -n <namespace>

```


```python
# To also delete user PVCs (be careful - this deletes all user data!)
# kubectl delete pvc -n <namespace> -l app=jupyterhub,component=singleuser-storage

```

## Section 4.7: Troubleshooting

### Common Issues

**JupyterHub not starting:**
```bash
# Check hub pod logs
kubectl logs -n <namespace> -l app=jupyterhub,component=hub

# Check proxy pod logs
kubectl logs -n <namespace> -l app=jupyterhub,component=proxy
```

**User pods not starting:**
```bash
# Check events
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp

# Describe the failing pod
kubectl describe pod <pod-name> -n <namespace>
```

**Storage issues:**
```bash
# Check PVC status
kubectl get pvc -n <namespace>

# Check storage class
kubectl get storageclass
```
