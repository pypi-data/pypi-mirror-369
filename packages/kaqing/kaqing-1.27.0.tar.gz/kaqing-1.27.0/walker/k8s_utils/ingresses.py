from kubernetes import client

# utility collection on ingresses; methods are all static
class Ingresses:
    def get_host(name: str, namespace: str):
        networking_v1_api = client.NetworkingV1Api()
        try:
            ingress = networking_v1_api.read_namespaced_ingress(name=name, namespace=namespace)
            return ingress.spec.rules[0].host
        except client.ApiException as e:
            print(f"Error getting Ingresses: {e}")
