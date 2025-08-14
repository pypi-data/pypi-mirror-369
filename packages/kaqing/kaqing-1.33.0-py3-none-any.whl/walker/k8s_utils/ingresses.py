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

    def create_ingress(name: str, namespace: str, host: str, port: int):
        networking_v1_api = client.NetworkingV1Api()

        body = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(name=name, annotations={
                'kubernetes.io/ingress.class': 'nginx',
                'nginx.ingress.kubernetes.io/use-regex': 'true'
                # "nginx.ingress.kubernetes.io/rewrite-target": "/"
            }),
            spec=client.V1IngressSpec(
                rules=[client.V1IngressRule(
                    host=host,
                    http=client.V1HTTPIngressRuleValue(
                        paths=[client.V1HTTPIngressPath(
                            # /iopsr/iopsr($|/)
                            path="/c3/ops($|/)",
                            path_type="ImplementationSpecific",
                            backend=client.V1IngressBackend(
                                service=client.V1IngressServiceBackend(
                                    port=client.V1ServiceBackendPort(
                                        number=port,
                                    ),
                                    name=name)
                                )
                        )]
                    )
                )
                ]
            )
        )
        # Creation of the Deployment in specified namespace
        # (Can replace "default" with a namespace you may have created)
        networking_v1_api.create_namespaced_ingress(
            namespace=namespace,
            body=body
        )