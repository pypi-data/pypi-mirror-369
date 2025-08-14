from typing import List
from kubernetes import client

from .kube_context import KubeContext

# utility collection on services; methods are all static
class Services:
    def list_services(label_selector=None) -> List[client.V1Service]:
        v1 = client.CoreV1Api()
        if ns := KubeContext.in_cluster_namespace():
            services = v1.list_namespaced_service(ns, label_selector=label_selector)
        else:
            services = v1.list_service_for_all_namespaces(label_selector=label_selector)

        return services.items

    def list_svc_name_and_ns(label_selector=None):
        return [(service.metadata.name, service.metadata.namespace) for service in Services.list_services(label_selector=label_selector)]

    def list_svc_names(label_selector=None, show_namespace = True):
        if show_namespace:
            return [f"{svc}@{ns}" for svc, ns in Services.list_svc_name_and_ns(label_selector=label_selector)]
        else:
            return [f"{svc}" for svc, _ in Services.list_svc_name_and_ns(label_selector=label_selector)]