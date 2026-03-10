# 5. Custom Hosted JupyterHubs (Instructor: Daniel Diaz)

The primary access mechanism we support for NAIRR Pilot Classroom usage on NRP is via JupyterHub. In this section we will provide information on how instructors/TAs can deploy custom JupyterHub instances. We will cover configuration aspects such as controlled access, custom software stacks/containers and resource scaling.

## Overview

This section covers how to deploy and manage JupyterHub environments for groups or courses.


## Key Concepts

- **Helm Charts**: Package managers for Kubernetes applications
- **JupyterHub Helm Chart**: Pre-configured deployment for JupyterHub
- **Configuration**: Customize JupyterHub through YAML configuration files
- **Resource Management**: Set CPU, memory, and GPU limits per user
- **Storage**: Configure persistent storage for user home directories


# Install Helm
Helm is a package manager for Kubernetes. It helps you install and manage complex applications without writing every Kubernetes file by hand. Instead of manually creating many YAML manifests for things like deployments, services, and configuration, you use a Helm chart, which is a reusable bundle of templates and settings.

First, check if Helm is installed on your system:

```bash
# Check if Helm is installed
helm version

```

If not, install and confirm with 
```bash
# install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

<details>
  <summary>Click to reveal expected result</summary>

```bash
helm version
```
```
version.BuildInfo{Version:"v3.20.0", GitCommit:"b2e4314fa0f229a1de7b4c981273f61d69ee5a59", GitTreeState:"clean", GoVersion:"go1.25.6"}
```
</details>

Now we are ready to look at the Helm chart for JupyterHub.

# Add JupyterHub Helm Repository
- Jupyterhub can only be deployed once in a namespace. 
- For the tutorial, we have pre-created namespaces for the registered participants so you can follow along.
- The namespaces will be named using the first initial (F) and the last name (surname) of participants as `nairr-hub-Fsurname`, if you are having trouble locating your namespace, you can find the full list [here](https://nrp.ai/viz/namespaces/).


## Add the JupyterHub Helm repository: **Please stick to using your pre-made namespace**
```bash
# Add JupyterHub Helm repository
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/ -n <namespace>
# Update Helm repositories
helm repo update
# Verify the repository was added
helm repo list
```

<details>
<summary>Click to reveal output</summary>

```bash
jovyan@jupyter-d4diaz-40ucsd-2eedu:helm repo add jupyterhub-ddiaz-test https://jupyterhub.github.io
/helm-chart/ -n test
```
```text
"jupyterhub-ddiaz-test" has been added to your repositories
```

```bash
jovyan@jupyter-d4diaz-40ucsd-2eedu:~$ helm repo update
```
```text
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "jupyterhub-ddiaz-test" chart repository
Update Complete. ⎈Happy Helming!⎈
```

```bash
jovyan@jupyter-d4diaz-40ucsd-2eedu:~$ helm repo list
```
```text
NAME                    URL                                     
jupyterhub-ddiaz-test   https://jupyterhub.github.io/helm-chart/
```
</details>

# Basic JupyterHub Deployment

Link to full documentation: https://nrp.ai/documentation/userdocs/jupyter/jupyterhub/

Let's create a basic JupyterHub configuration. First, create a configuration file:


### Create Basic JupyterHub Configuration

- Examine the contents of `/nairr-tutorial/yamls/jhub-values.yaml`
```yaml
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

**Important**: Replace `secret_token` in the `jhub-values.yaml` file with the token generated above.


### Deploy JupyterHub

Now deploy JupyterHub using Helm. **Important**: Replace `<namespace>` with your namespace name.

```bash
# Deploy JupyterHub
# Replace <namespace> with your namespace
# Replace <release-name> with a name for your JupyterHub instance (e.g., jhub-basic)

helm upgrade --cleanup-on-fail --install <release-name> jupyterhub/jupyterhub \
    --namespace <namespace> \
    --version=3.3.7 \
    --values yamls/jhub-vals.yaml \
    --wait \
    --timeout=10m
```
<details>
<summary>Click to reveal</summary>

```bash
helm upgrade --cleanup-on-fail --install jhub-ddiaz-test jupyterhub/jupyterhub     --namespace test     --version=3.3.7     --values testvals.yaml   --wait --timeout=10m
```
```text
Release "jhub-ddiaz-test" does not exist. Installing it now.
NAME: jhub-ddiaz-test
LAST DEPLOYED: Tue Mar 10 03:21:43 2026
NAMESPACE: test
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
.      __                          __                  __  __          __
      / / __  __  ____    __  __  / /_  ___    _____  / / / / __  __  / /_
 __  / / / / / / / __ \  / / / / / __/ / _ \  / ___/ / /_/ / / / / / / __ \
/ /_/ / / /_/ / / /_/ / / /_/ / / /_  /  __/ / /    / __  / / /_/ / / /_/ /
\____/  \__,_/ / .___/  \__, /  \__/  \___/ /_/    /_/ /_/  \__,_/ /_.___/
              /_/      /____/

       You have successfully installed the official JupyterHub Helm chart!

### Installation info

  - Kubernetes namespace: test
  - Helm release name:    jhub-ddiaz-test
  - Helm chart version:   3.3.7
  - JupyterHub version:   4.1.5
  - Hub pod packages:     See https://github.com/jupyterhub/zero-to-jupyterhub-k8s/blob/3.3.7/images/hub/requirements.txt

### Followup links

  - Documentation:  https://z2jh.jupyter.org
  - Help forum:     https://discourse.jupyter.org
  - Social chat:    https://gitter.im/jupyterhub/jupyterhub
  - Issue tracking: https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues

### Post-installation checklist

  - Verify that created Pods enter a Running state:

      kubectl --namespace=test get pod

    If a pod is stuck with a Pending or ContainerCreating status, diagnose with:

      kubectl --namespace=test describe pod <name of pod>

    If a pod keeps restarting, diagnose with:

      kubectl --namespace=test logs --previous <name of pod>


  - Verify web based access:

    You have not configured a k8s Ingress resource so you need to access the k8s
    Service proxy-public directly.

    If your computer is outside the k8s cluster, you can port-forward traffic to
    the k8s Service proxy-public with kubectl to access it from your
    computer.

      kubectl --namespace=test port-forward service/proxy-public 8080:http

    Try insecure HTTP access: http://localhost:8080
```
</details>

Now, let's see what was deployed
```bash
# Check deployment status
kubectl get pods -n <namespace>
kubectl get services -n <namespace>
kubectl get pvc -n <namespace>
```

You should see pods for the hub, proxy, and (if a user starts a server) user pods.
- **hub**: manages authentication, user sessions, and spawning user notebook servers
- **proxy**: routes incoming traffic to the hub or the correct user notebook server
- **user pods**: run the individual Jupyter servers for each user

Additionally, you will see some persistent storage is created. A PVC for the hub is created when making the deployment and PVCs for user servers are created whenever a new server is launched. Optionally, if you have a shared storage that you would like accessible by all pods, you can create one and include it as a volume mount in the helm chart values.

<details>
<summary>Click to reveal</summary>

```bash
kubectl get pods -n test
```
```text
NAME                     READY   STATUS    RESTARTS   AGE
hub-5f5c7f8588-czp56     1/1     Running   0          26m
jupyter-admin            1/1     Running   0          13m
proxy-857f69dcbc-znhkd   1/1     Running   0          41m
```
```bash
kubectl get services -n test
```
```text
NAME           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
hub            ClusterIP   10.110.96.59    <none>        8081/TCP   5m1s
proxy-api      ClusterIP   10.106.17.152   <none>        8001/TCP   5m1s
proxy-public   ClusterIP   10.110.183.21   <none>        80/TCP     5m1s
```
```bash
kubectl get pvc -n test
```
```text 
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
claim-admin   Bound    pvc-9acc9f4d-2681-419a-963b-cb27ade541b6   5Gi        RWO            rook-ceph-block   <unset>                 14m
hub-db-dir    Bound    pvc-24ed6711-d5fc-4216-9689-f233b57818e5   1Gi        RWO            rook-ceph-block   <unset>                 42m
```
</details>

# Configure Ingress

To make JupyterHub accessible via a URL, create an Ingress resource:

### Create Ingress Configuration

Add the following to your `jhub-values.yaml` or create a separate ingress file:

```yaml
ingress:
  enabled: true
  ingressClassName: haproxy
  hosts: ["<your-jupyterhub-name>.nrp-nautilus.io"]
  pathSuffix: ''
  tls:
    - hosts:
      - <your-jupyterhub-name>.nrp-nautilus.io
```

- Now update your deployment
```yaml
helm upgrade <release-name> jupyterhub/jupyterhub \
    --namespace <namespace> \
    --version=3.3.7 \
    --values yamls/jhub-vals.yaml \
    --wait \
    --timeout=10m
```

Let's see what has changed

```bash
kubectl get pods -n <namespace>
# Check ingress status
kubectl get ingress -n <namespace>
```

<details>
<summary>Click to reveal</summary>

```bash
helm upgrade jhub-ddiaz-test jupyterhub/jupyterhub     --namespace test     --version=3.3.7     --values testvals.yaml   --wait --timeout=10m
```
```text
Release "jhub-ddiaz-test" has been upgraded. Happy Helming!
NAME: jhub-ddiaz-test
LAST DEPLOYED: Tue Mar 10 03:35:39 2026
NAMESPACE: test
STATUS: deployed
REVISION: 2
TEST SUITE: None
NOTES:
.      __                          __                  __  __          __
      / / __  __  ____    __  __  / /_  ___    _____  / / / / __  __  / /_
 __  / / / / / / / __ \  / / / / / __/ / _ \  / ___/ / /_/ / / / / / / __ \
/ /_/ / / /_/ / / /_/ / / /_/ / / /_  /  __/ / /    / __  / / /_/ / / /_/ /
\____/  \__,_/ / .___/  \__, /  \__/  \___/ /_/    /_/ /_/  \__,_/ /_.___/
              /_/      /____/

       You have successfully installed the official JupyterHub Helm chart!

### Installation info

  - Kubernetes namespace: test
  - Helm release name:    jhub-ddiaz-test
  - Helm chart version:   3.3.7
  - JupyterHub version:   4.1.5
  - Hub pod packages:     See https://github.com/jupyterhub/zero-to-jupyterhub-k8s/blob/3.3.7/images/hub/requirements.txt

### Followup links

  - Documentation:  https://z2jh.jupyter.org
  - Help forum:     https://discourse.jupyter.org
  - Social chat:    https://gitter.im/jupyterhub/jupyterhub
  - Issue tracking: https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues

### Post-installation checklist

  - Verify that created Pods enter a Running state:

      kubectl --namespace=test get pod

    If a pod is stuck with a Pending or ContainerCreating status, diagnose with:

      kubectl --namespace=test describe pod <name of pod>

    If a pod keeps restarting, diagnose with:

      kubectl --namespace=test logs --previous <name of pod>


  - Verify web based access:

    Try insecure HTTP access: http://jhub-ddiaz-test.nrp-nautilus.io/
    Try secure HTTPS access: https://jhub-ddiaz-test.nrp-nautilus.io/
```
```bash
kubectl get ingress -n test
```
```text
NAME         CLASS     HOSTS                             ADDRESS   PORTS     AGE
jupyterhub   haproxy   jhub-ddiaz-test.nrp-nautilus.io             80, 443   2m30s
```
</details>

# Advanced Configuration

### Multiple Image Profiles

You can configure multiple image options for users to choose from.

```yaml
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

```yaml
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

 Try adding one or more of these profiles to your `jhub-values.yaml` and re-deploy. The change will be reflected in the spawner page

 ### Shared Storage

 If you have a shared storage that you want to use, you can add an *extraVolumes* section to your helm values file:
```yaml

  storage:
    type: dynamic
    extraLabels: {}
    # Change starts here
    extraVolumes:
      - name: jupyterhub-shared
        persistentVolumeClaim:
          claimName: jupyterhub-shared-volume
    extraVolumeMounts:
      - name: jupyterhub-shared
        mountPath: /home/shared
    # Change Ends
    capacity: 5Gi
    homeMountPath: /home/jovyan
    dynamic:
      storageClass: rook-ceph-block
      pvcNameTemplate: claim-{username}{servername}
      volumeNameTemplate: volume-{username}{servername}
      storageAccessModes: [ReadOnlyMany]
```

# Managing JupyterHub

### Check JupyterHub Status

```bash
# List all Helm releases in your namespace
helm list -n <namespace>

```
<details>
<summary>Click to reveal</summary>

```bash
helm list -n test
```
```text
NAME           	NAMESPACE	REVISION	UPDATED                             	STATUS  	CHART           	APP VERSION
jhub-ddiaz-test	test     	2       	2026-03-10 03:35:39.476432 -0400 EDT	deployed	jupyterhub-3.3.7	4.1.5 
```
</details>

```bash
# Check JupyterHub hub pod logs
kubectl logs -n <namespace> -l app=jupyterhub,component=hub --tail=50
```
<details>
<summary>Click to reveal</summary>

```bash
kubectl logs -n test -l app=jupyterhub,component=hub --tail=50
```
```text
Loading /usr/local/etc/jupyterhub/secret/values.yaml
No config at /usr/local/etc/jupyterhub/existing-secret/values.yaml
[I 2026-03-10 07:37:18.459 JupyterHub app:2885] Running JupyterHub version 4.1.5
[I 2026-03-10 07:37:18.459 JupyterHub app:2915] Using Authenticator: jupyterhub.auth.DummyAuthenticator-4.1.5
[I 2026-03-10 07:37:18.459 JupyterHub app:2915] Using Spawner: kubespawner.spawner.KubeSpawner-6.2.0
[I 2026-03-10 07:37:18.459 JupyterHub app:2915] Using Proxy: jupyterhub.proxy.ConfigurableHTTPProxy-4.1.5
[W 2026-03-10 07:37:18.627 JupyterHub auth:193] Allowed set contains single-character names: ['(', ')', 'e', 's', 't']; did you mean set(['()est']) instead of set('()est')?
[W 2026-03-10 07:37:18.627 JupyterHub app:1966] 
    JupyterHub.admin_users is deprecated since version 0.7.2.
    Use Authenticator.admin_users instead.
[I 2026-03-10 07:37:18.956 JupyterHub app:2954] Initialized 0 spawners in 0.002 seconds
[I 2026-03-10 07:37:18.962 JupyterHub metrics:279] Found 0 active users in the last ActiveUserPeriods.twenty_four_hours
[I 2026-03-10 07:37:18.962 JupyterHub metrics:279] Found 0 active users in the last ActiveUserPeriods.seven_days
[I 2026-03-10 07:37:18.963 JupyterHub metrics:279] Found 0 active users in the last ActiveUserPeriods.thirty_days
[I 2026-03-10 07:37:18.963 JupyterHub app:3168] Not starting proxy
[I 2026-03-10 07:37:19.088 JupyterHub app:3204] Hub API listening on http://:8081/hub/
[I 2026-03-10 07:37:19.088 JupyterHub app:3206] Private Hub API connect url http://hub:8081/hub/
[I 2026-03-10 07:37:19.088 JupyterHub app:3215] Starting managed service jupyterhub-idle-culler
[I 2026-03-10 07:37:19.088 JupyterHub service:386] Starting service 'jupyterhub-idle-culler': ['python3', '-m', 'jupyterhub_idle_culler', '--url=http://localhost:8081/hub/api', '--timeout=3600', '--cull-every=600', '--concurrency=10']
[I 2026-03-10 07:37:19.089 JupyterHub service:134] Spawning python3 -m jupyterhub_idle_culler --url=http://localhost:8081/hub/api --timeout=3600 --cull-every=600 --concurrency=10
[I 2026-03-10 07:37:19.145 JupyterHub app:3273] JupyterHub is now running, internal Hub API at http://hub:8081/hub/
[I 2026-03-10 07:37:19.506 JupyterHub log:192] 200 GET /hub/api/ (jupyterhub-idle-culler@::1) 272.37ms
[I 2026-03-10 07:37:19.526 JupyterHub log:192] 200 GET /hub/api/users?state=[secret] (jupyterhub-idle-culler@::1) 18.51ms
[I 2026-03-10 07:37:57.353 JupyterHub log:192] 302 GET / -> /hub/ (@::ffff:10.244.222.188) 0.74ms
[I 2026-03-10 07:37:57.892 JupyterHub log:192] 302 GET /hub/ -> /hub/login?next=%2Fhub%2F (@::ffff:10.244.222.188) 0.69ms
[I 2026-03-10 07:37:58.435 JupyterHub _xsrf_utils:125] Setting new xsrf cookie for b'None:L8Kt1fCCYBcN-zuHgbqlpzFQ5gxohPFAkpTQyWZuEaY=' {'path': '/hub/', 'max_age': 3600}
[I 2026-03-10 07:37:58.471 JupyterHub log:192] 200 GET /hub/login?next=%2Fhub%2F (@::ffff:10.244.222.188) 36.63ms
[I 2026-03-10 07:47:19.515 JupyterHub log:192] 200 GET /hub/api/ (jupyterhub-idle-culler@::1) 193.60ms
[I 2026-03-10 07:47:19.519 JupyterHub log:192] 200 GET /hub/api/users?state=[secret] (jupyterhub-idle-culler@::1) 3.38ms
```
</details>

```bash
# Check all user pods
kubectl get pods -n <namespace> -l app=jupyterhub,component=singleuser-server
```
<details>
<summary>Click to reveal</summary>

```bash
kubectl get pods -n test -l app=jupyterhub,component=singleuser-server
```
```text
NAME            READY   STATUS              RESTARTS   AGE
jupyter-admin   0/1     ContainerCreating   0          43s
```
</details>

# Uninstall JupyterHub

To remove JupyterHub (and optionally all user data):

```bash
# Uninstall JupyterHub (this will delete the hub and proxy, but NOT user data)
helm uninstall <release-name> -n <namespace>
```

```bash
# To also delete user PVCs (be careful - this deletes all user data!)
# kubectl delete pvc -n <namespace> -l app=jupyterhub,component=singleuser-storage
```

# Troubleshooting

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

# Advanced Topic: Building in GitLab

## Overview

NRP provides GitLab integration for building container images and automating CI/CD pipelines. This section covers how to use GitLab for building and deploying container images on NRP.

For comprehensive documentation, see: [https://nrp.ai/documentation/userdocs/development/gitlab/](https://nrp.ai/documentation/userdocs/development/gitlab/)

## Key Features

- **Container Image Building**: Build Docker images directly in GitLab CI/CD
- **Kubernetes Integration**: Deploy applications to your namespace from GitLab pipelines
- **Automated Workflows**: Set up CI/CD pipelines for your projects
- **Private Repositories**: Support for private GitLab repositories
- **Custom Images**: Build and use custom images in JupyterHub and other services

## Prerequisites

- ✅ Access to NRP GitLab instance
- ✅ Namespace admin privileges (for deploying to Kubernetes)
- ✅ Understanding of Git and GitLab CI/CD basics
- ✅ Docker/container image concepts

## Getting Started with GitLab

### Access GitLab

NRP provides a GitLab instance for building images and managing repositories. Access it through:
- The NRP Portal
- Direct link provided by your namespace administrator

### Create a Project

1. Create a new GitLab project or use an existing one
2. Add your code and Dockerfile
3. Configure CI/CD pipeline using `.gitlab-ci.yml`

## Building Container Images

### Basic GitLab CI/CD Pipeline

Create a `.gitlab-ci.yml` file in your repository:

```yaml
image: ghcr.io/osscontainertools/kaniko:debug

stages:
- build-and-push

build-and-push-job:
  stage: build-and-push
  variables:
    GODEBUG: "http2client=0"
  script:
  - echo "{\"auths\":{\"$CI_REGISTRY\":{\"username\":\"$CI_REGISTRY_USER\",\"password\":\"$CI_REGISTRY_PASSWORD\"}}}" > /kaniko/.docker/config.json
  - /kaniko/executor --cache=true --push-retry=10 --context $CI_PROJECT_DIR --dockerfile $CI_PROJECT_DIR/Dockerfile --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA --destination $CI_REGISTRY_IMAGE:latest
```

### Using Built Images

Once your image is built, you can use it in:
- **JupyterHub**: Configure custom images in your JupyterHub deployment
- **Kubernetes Pods**: Reference the image in your pod specifications
- **Jobs**: Use in batch jobs and other workloads

## Kubernetes Integration

GitLab can deploy directly to your Kubernetes namespace:

1. **Create Service Account**: Set up a service account with appropriate permissions
2. **Configure GitLab**: Add Kubernetes cluster information to GitLab
3. **Deploy Pipeline**: Add deployment stages to your CI/CD pipeline

For detailed steps, see the [GitLab Kubernetes Integration documentation](https://nrp.ai/documentation/userdocs/development/gitlab/).

## Best Practices

- **Use Tags**: Tag your images with version numbers or commit SHAs
- **Cache Layers**: Optimize Docker builds with layer caching
- **Security**: Keep your GitLab tokens and credentials secure
- **Testing**: Test images before deploying to production
- **Documentation**: Document your build process and image usage

## Resources

- [NRP GitLab Documentation](https://nrp.ai/documentation/userdocs/development/gitlab/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)


---
