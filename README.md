# Introduction

This repo contains the sourcecode for a Prometheus exporter of Open Policy Agent 'Data' metrics. Data refers to OPA's internal cache of [External Data](https://www.openpolicyagent.org/docs/latest/external-data) as pushed by [kube-mgmt](https://github.com/open-policy-agent/kube-mgmt) or other means. This exporter (sample output below) should be deployed in a Kubernetes cluster (see example k8s yamls below).

In a high available OPA + kube-mgmt deployment multiple OPA instances run, without any cross communication. Each OPA instance gets data pushed by its own dedicated kube-mgmt instance. Data of all OPA instances should be in sync, but sometimes this is not the case. This may result in different decisions between OPA instances. This exporter does periodic counts of the data objects and exposes them for Prometheus to scrape.

# Usage & help

```bash
$ docker run -ti opa-data-metrics-exporter -h

Usage: exporter.py [OPTIONS]

Options:
  -d, --debug                 Enable DEBUG verbosity
  -t, --timeout INTEGER       Request timeout in seconds
  --prometheus-port INTEGER   Prometheus HTTP listener port
  --opa-namespace TEXT        OPA namespace  [required]
  --opa-service TEXT          OPA service (for discoverying OPA pods)
                              [required]
  --ssl-verify                Disable SSL server verification
  --interval INTEGER          Metric collection interval in seconds
  --opa-cluster-data TEXT     OPA kubernetes cluster scoped data items to
                              count, comma seperated. Example:
                              kubernetes/namespaces
  --opa-namespaced-data TEXT  OPA kuberentes namespace scoped data items to
                              count, comma seperated. Example:
                              kubernetes/ingresses
  --cluster-name TEXT         Name of Kubernetes cluster (to be used in
                              metrics)  [required]
  --context TEXT              Kubernetes context to use (for local development
  --single                    Do a single run and exit (for local development)
  -h, --help                  Show this message and exit.
```


# Example Prometheus exporter output

```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 415.0
python_gc_objects_collected_total{generation="1"} 43.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 1.4317904e+07
python_gc_collections_total{generation="1"} 1.301627e+06
python_gc_collections_total{generation="2"} 118329.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="8",patchlevel="5",version="3.8.5"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 2.14102016e+08
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 5.7847808e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.59714108073e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 41545.41
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 6.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1.048576e+06
# HELP opa_cluster_data_items Number of cluster scoped data items in present memory of a OPA pod
# TYPE opa_cluster_data_items gauge
opa_cluster_data_items{cluster_name="cluster42",data_path="kubernetes/namespaces",node_name="gke-cluster42-internal3-81e24bc8-yhzj",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-hbtm4"} 453.0
opa_cluster_data_items{cluster_name="cluster42",data_path="kubernetes/namespaces",node_name="gke-cluster42-internal3-81e24bc8-tgvn",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-99wmn"} 453.0
opa_cluster_data_items{cluster_name="cluster42",data_path="kubernetes/namespaces",node_name="gke-cluster42-platform3-e054cd13-e04k",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-sqswt"} 453.0
opa_cluster_data_items{cluster_name="cluster42",data_path="kubernetes/namespaces",node_name="gke-cluster42-platform3-8cc2b449-lbj2",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-jt5jh"} 453.0
opa_cluster_data_items{cluster_name="cluster42",data_path="kubernetes/namespaces",node_name="gke-cluster42-internal3-75de1dd0-tirk",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-69lst"} 453.0
opa_cluster_data_items{cluster_name="cluster42",data_path="kubernetes/namespaces",node_name="gke-cluster42-platform3-e8feff8e-vrb5",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-6mcwp"} 453.0
# HELP opa_namespaced_data_items Number of namespace scoped data items in present memory of a OPA pod
# TYPE opa_namespaced_data_items gauge
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-internal3-81e24bc8-yhzj",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-hbtm4"} 524.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-internal3-81e24bc8-yhzj",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-hbtm4"} 991.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-internal3-81e24bc8-tgvn",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-99wmn"} 524.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-internal3-81e24bc8-tgvn",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-99wmn"} 991.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-platform3-e054cd13-e04k",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-sqswt"} 524.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-platform3-e054cd13-e04k",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-sqswt"} 991.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-platform3-8cc2b449-lbj2",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-jt5jh"} 524.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-platform3-8cc2b449-lbj2",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-jt5jh"} 991.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-internal3-75de1dd0-tirk",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-69lst"} 524.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-internal3-75de1dd0-tirk",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-69lst"} 991.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-platform3-e8feff8e-vrb5",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-6mcwp"} 524.0
opa_namespaced_data_items{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-platform3-e8feff8e-vrb5",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-6mcwp"} 991.0
# HELP opa_namespaced_data_item_namespaces Number of namespace scoped for namespaced data items in present memory of a OPA pod
# TYPE opa_namespaced_data_item_namespaces gauge
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-internal3-81e24bc8-yhzj",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-hbtm4"} 239.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-internal3-81e24bc8-yhzj",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-hbtm4"} 314.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-internal3-81e24bc8-tgvn",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-99wmn"} 239.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-internal3-81e24bc8-tgvn",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-99wmn"} 314.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-platform3-e054cd13-e04k",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-sqswt"} 239.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-platform3-e054cd13-e04k",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-sqswt"} 314.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-platform3-8cc2b449-lbj2",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-jt5jh"} 239.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-platform3-8cc2b449-lbj2",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-jt5jh"} 314.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-internal3-75de1dd0-tirk",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-69lst"} 239.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-internal3-75de1dd0-tirk",opa_namespace="opa",opa_service="opa-service",pod_name="opa-internal-59496d7c7d-69lst"} 314.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/ingresses",node_name="gke-cluster42-platform3-e8feff8e-vrb5",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-6mcwp"} 239.0
opa_namespaced_data_item_namespaces{cluster_name="cluster42",data_path="kubernetes/services",node_name="gke-cluster42-platform3-e8feff8e-vrb5",opa_namespace="opa",opa_service="opa-service",pod_name="opa-platform-5f95d4c9c4-6mcwp"} 314.0
# HELP opa_data_exporter_collection_time Time it takes to collect metrics
# TYPE opa_data_exporter_collection_time histogram
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.005"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.01"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.025"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.05"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.075"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.1"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.25"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.5"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="0.75"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="1.0"} 0.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="2.5"} 83207.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="5.0"} 83210.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="7.5"} 83210.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="10.0"} 83210.0
opa_data_exporter_collection_time_bucket{cluster_name="cluster42",le="+Inf"} 83210.0
opa_data_exporter_collection_time_count{cluster_name="cluster42"} 83210.0
opa_data_exporter_collection_time_sum{cluster_name="cluster42"} 146743.03542901413
# TYPE opa_data_exporter_collection_time_created gauge
opa_data_exporter_collection_time_created{cluster_name="cluster42"} 1.5971410833229024e+09
```


# Example k8s deployment

The following example keeps track of the following resources:

- namespaces
- services, per namespace
- ingresses, per namespace

```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: endpoint-reader
  namespace: opa
rules:
- apiGroups: [""]
  resources: ["endpoints"]
  verbs: ["get"]
  
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: opa-monitoring-endpoint-reader
subjects:
- kind: ServiceAccount
  name: opa-monitoring
  namespace: opa
roleRef:
  kind: Role
  name: endpoint-reader
  apiGroup: rbac.authorization.k8s.io
    
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: opa-data-exporter
  namespace: opa
spec:
  selector:
    matchLabels:
      app: opa-data-exporter
  replicas: 1
  template:
    metadata:
      labels:
        app: opa-data-exporter
    spec:
      containers:
      - name: opa-data-exporter
        image: your-registry/opa-mon-data-exporter:latest
        env:
        - name: TZ
          value: Europe/Amsterdam
        - name: APP_OPA_NAMESPACE
          value: opa
        - name: APP_OPA_SERVICE
          value: opa-service
        - name: APP_INTERVAL
          value: '30'
        - name: APP_PROMETHEUS_PORT
          value: '9998'
        - name: APP_OPA_CLUSTER_DATA
          value: kubernetes/namespaces
        - name: APP_OPA_NAMESPACED_DATA
          value: kubernetes/services,kubernetes/ingresses
        - name: APP_CLUSTER_NAME
          value: cluster-name
        ports:
        - containerPort: 9998
      securityContext:
        fsGroup: 1000
        runAsUser: 1000
      serviceAccountName: opa-monitoring
      
---
apiVersion: v1
kind: Service
metadata:
  name: opa-data-exporter
  namespace: opa
  labels:
    app: opa-data-exporter
spec:
  type: ClusterIP
  clusterIP: None		# headless
  ports:
  - name: http-9998
    port: 9998
    targetPort: 9998
    protocol: TCP
  selector:
    app: opa-data-exporter
```

