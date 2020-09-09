#!/usr/bin/env python
import logging
import os
import time

import click
from kubernetes import client, config
import requests
import urllib3
from prometheus_client import Histogram, Gauge, start_http_server

VERSION = '1.2.1'


# disable the warnings regarding the insecure HTTP calls
urllib3.disable_warnings()

logging.basicConfig(
    format='%(asctime)s - %(name)s/%(threadName)s - %(levelname)s %(message)s')
log = logging.getLogger('mon')

opa_cluster_data_item_gauge = Gauge('opa_cluster_data_items',
                                    'Number of cluster scoped data items in present memory of a OPA pod',
                                    ['cluster_name', 'opa_namespace', 'opa_service', 'pod_name', 'node_name', 'data_path'])
opa_namespaced_data_item_gauge = Gauge('opa_namespaced_data_items',
                                       'Number of namespace scoped data items in present memory of a OPA pod',
                                       ['cluster_name', 'opa_namespace', 'opa_service', 'pod_name', 'node_name', 'data_path'])
opa_namespaced_data_namespaces_gauge = Gauge('opa_namespaced_data_item_namespaces',
                                             'Number of namespace scoped for namespaced data items in present memory of a OPA pod',
                                             ['cluster_name', 'opa_namespace', 'opa_service', 'pod_name', 'node_name', 'data_path'])
opa_exporter_latency = Histogram(
    'opa_data_exporter_collection_time', 'Time it takes to collect metrics', ['cluster_name'])


class OpaEndpoint(object):
    def __init__(self, ip, port, pod_name, node_name, namespace, service, cluster_name):
        self.ip = ip
        self.port = port
        self.pod_name = pod_name
        self.node_name = node_name
        self.namespace = namespace
        self.service = service
        self.cluster_name = cluster_name

    def __repr__(self):
        return f'OpaEndpoint: {self.ip}:{self.port}/{self.pod_name}@{self.node_name}'


def get_opa_endpoints(opa_namespace, opa_service, cluster_name):
    first_endpoint_subset = client.CoreV1Api().read_namespaced_endpoints(
        opa_service, opa_namespace).subsets[0]
    port = first_endpoint_subset.ports[0].port

    for address in first_endpoint_subset.addresses:
        endpoint = OpaEndpoint(
            address.ip, port, address.target_ref.name, address.node_name, opa_namespace, opa_service, cluster_name)
        log.debug(endpoint)
        yield endpoint


def get_metrics_for_opa_data_item(endpoint: OpaEndpoint, data_path, is_cluster_resource, ssl_verify):

    url = f'https://{endpoint.ip}:{endpoint.port}/v1/data/{data_path}'

    try:
        res = requests.get(url, verify=ssl_verify, timeout=30)
    except IOError as e:
        log.error(
            f'Unable to query OPA pod {endpoint.pod_name} on {endpoint.ip}:{endpoint.port}: {e}')
        return False

    if res.status_code != 200:
        log.error(
            f'Query of OPA pod {endpoint.pod_name} failed. Got HTTP status_code {status_code}')
        return False

    doc = res.json()

    # use empty hash as default to catch unknown data items
    result = doc.get('result', {})

    if is_cluster_resource:
        items = len(result)

        opa_cluster_data_item_gauge.labels(
            endpoint.cluster_name, endpoint.namespace, endpoint.service,
            endpoint.pod_name, endpoint.node_name, data_path).set(items)

        log.debug(
            f'Metrics for cluster scoped resource {data_path}: {items} resources')
    else:
        namespaces = 0
        items = 0
        for namespace in result:
            namespaces += 1
            items += len(result[namespace])

        opa_namespaced_data_item_gauge.labels(
            endpoint.cluster_name, endpoint.namespace, endpoint.service,
            endpoint.pod_name, endpoint.node_name, data_path).set(items)
        opa_namespaced_data_namespaces_gauge.labels(
            endpoint.cluster_name, endpoint.namespace, endpoint.service,
            endpoint.pod_name, endpoint.node_name, data_path).set(namespaces)

        log.debug(
            f'Metrics for namespace scoped resource {data_path}: {items} resources in {namespaces} namespaces')


def get_metrics_for_opa_pod(endpoint, cluster_data, namespaced_data, ssl_verify):

    for data in cluster_data:
        get_metrics_for_opa_data_item(endpoint, data, True, ssl_verify)

    for data in namespaced_data:
        get_metrics_for_opa_data_item(endpoint, data, False, ssl_verify)


def delete_metrics_for_opa_data_item(endpoint: OpaEndpoint, data_path, is_cluster_resource):

    if is_cluster_resource:
        opa_cluster_data_item_gauge.remove(
            endpoint.cluster_name, endpoint.namespace, endpoint.service,
            endpoint.pod_name, endpoint.node_name, data_path)
    else:
        opa_namespaced_data_item_gauge.remove(
            endpoint.cluster_name, endpoint.namespace, endpoint.service,
            endpoint.pod_name, endpoint.node_name, data_path)
        opa_namespaced_data_namespaces_gauge.remove(
            endpoint.cluster_name, endpoint.namespace, endpoint.service,
            endpoint.pod_name, endpoint.node_name, data_path)


def delete_metrics_for_opa_pod(endpoint, cluster_data, namespaced_data):
    for data in cluster_data:
        delete_metrics_for_opa_data_item(endpoint, data, True)

    for data in namespaced_data:
        delete_metrics_for_opa_data_item(endpoint, data, False)


def configure_kubernetes_client(context, debug):
    try:
        config.load_incluster_config()
        log.info('Configured in-cluster Kubernetes client')
    except config.config_exception.ConfigException:
        if not context:
            log.error(
                'No in-cluster Kubernetes client possible. And no context specified. Specify context and retry')
            return False
        try:
            config.load_kube_config(
                os.path.join(os.environ["HOME"], '.kube/config'),
                context)
            log.info(f'Configured Kubernetes client for context {context}')
        except FileNotFoundError:
            log.error(
                'Can not create Kubernetes client config: no in-cluster config nor $HOME/.kube/config file found')
            return False

    if debug:
        c = client.Configuration()
        c.debug = True
        log.debug('Enabling DEBUG on Kubernetes client')
        client.Configuration.set_default(c)

    return True


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.pass_context
@click.option('-d', '--debug', is_flag=True, help='Enable DEBUG verbosity')
@click.option('-t', '--timeout', type=int, default=30, help='Request timeout in seconds')
@click.option('--prometheus-port', type=int, default=9999, help='Prometheus HTTP listener port')
@click.option('--opa-namespace', help='OPA namespace', default='opa', required=True)
@click.option('--opa-service', help='OPA service (for discoverying OPA pods)', required=True)
@click.option('--ssl-verify', is_flag=True, default=False, help='Disable SSL server verification')
@click.option('--interval', type=int, default=30, help='Metric collection interval in seconds')
@click.option('--opa-cluster-data', help='OPA kubernetes cluster scoped data items to count, comma seperated. Example: kubernetes/namespaces')
@click.option('--opa-namespaced-data', help='OPA kuberentes namespace scoped data items to count, comma seperated. Example: kubernetes/ingresses')
@click.option('--cluster-name', help='Name of Kubernetes cluster (to be used in metrics)', required=True)
@click.option('--context', help='Kubernetes context to use (for local development')
@click.option('--single', is_flag=True, default=False, help='Do a single run and exit (for local development)')
def cli(ctx, debug, timeout, prometheus_port, opa_namespace, opa_service, ssl_verify, interval, opa_cluster_data, opa_namespaced_data, cluster_name, context, single):
    if debug:
        log.setLevel(logging.DEBUG)
        log.debug('Debug logging enabled')
    else:
        log.setLevel(logging.INFO)

    log.info(f'Starting version {VERSION}')
    if single:
        log.info('Running in single mode. Prometheus listener will not be started and exporter will exit after a single collection run')

    if not opa_cluster_data and not opa_namespaced_data:
        log.fatal(
            'No data items configured. Use --opa-cluster-data and/or --opa-namespaced-data')
        return

    opa_cluster_data = opa_cluster_data.split(',')
    opa_namespaced_data = opa_namespaced_data.split(',')
    log.debug(
        f'opa_cluster_data={opa_cluster_data}, opa_namespaced_data={opa_namespaced_data}')

    if not configure_kubernetes_client(context, debug):
        log.fatal('Unable to create Kubernetes client')
        return

    # ping kubernetes
    try:
        client.VersionApi().get_code()
    except:
        log.fatal('Unable to ping Kubernetes cluster')
        return

    if not single:
        log.info(
            f'Starting Prometheus HTTP listener on port {prometheus_port}')
        start_http_server(prometheus_port)

    log.info(
        f'Starting collecting metrics for OPA data resources for all pods backing service {opa_namespace}/{opa_service}, every {interval} seconds.')

    known_pods = {}
    while 1:
        start_time = time.perf_counter()

        active_pods = []
        try:
            for endpoint in get_opa_endpoints(opa_namespace, opa_service, cluster_name):
                get_metrics_for_opa_pod(
                    endpoint, opa_cluster_data, opa_namespaced_data, ssl_verify)
                if endpoint.pod_name not in known_pods:
                    known_pods[endpoint.pod_name] = endpoint
                    log.info(f'Detected new OPA pod: {endpoint.pod_name}')
                active_pods.append(endpoint.pod_name)
        except client.rest.ApiException as e:
            log.fatal(f'Unable to query OPA endpoints: {e}')
            break

        if single:
            break

        duration = time.perf_counter() - start_time
        opa_exporter_latency.labels(cluster_name).observe(duration)

        for known_pod in set(known_pods):
            if known_pod in active_pods:
                continue
            log.info(f'Detected deleted OPA pod: {known_pod}')
            delete_metrics_for_opa_pod(
                known_pods[known_pod], opa_cluster_data, opa_namespaced_data)
            del known_pods[known_pod]

        log.info(f'Metrics collection run took {duration} sec')

        if duration < interval:
            time.sleep(float(interval) - duration)

    log.info('End')


if __name__ == '__main__':
    cli(auto_envvar_prefix='APP')  # pylint: disable=all
