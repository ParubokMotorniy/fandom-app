import consul
import os
import json
import random

def get_consul_client():
    return consul.Consul(
        host=os.environ.get("CONSUL_HOST", "localhost"), #let's go with these defaults for now
        port=int(os.environ.get("CONSUL_PORT", 8500)),
    )


def register_consul_service(
    service_name: str,
    service_id: str,
    service_address: str,
    service_port: int,
    timeout: int = None,
    interval: int = None,
    health_endpoint: str = None,
):
    """
    Registers a service in Consul, optionally with an HTTP health check.

    Args:
        service_name: Name of the service
        service_id: Unique ID for the service
        service_address: Address of the service
        service_port: Port number
        timeout: Timeout for health check in seconds (required if health_endpoint is set)
        interval: Interval for health check in seconds (required if health_endpoint is set)
        health_endpoint: Endpoint to be polled for health checking (with e.g., "/health")
    """
    c = get_consul_client()

    check = None
    if health_endpoint:
        if timeout is None or interval is None:
            raise ValueError(
                "Both `timeout` and `interval` must be set if `health_endpoint` is provided."
            )
        
        print(f"http://{service_address}:{service_port}{health_endpoint}")
        check = consul.Check.http(
            url=f"http://{service_address}:{service_port}{health_endpoint}",
            interval=f"{interval}s",
            timeout=f"{timeout}s",
            deregister="2m",
        )

    c.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=service_address,
        port=int(service_port),
        check=check,
    )

    print(
        f"Registered service `{service_name}` with ID `{service_id}` at {service_address}:{service_port}"
    )


def query_consul_services(service_name_to_query: str):
    """
    Returns all healthy service instances for a given service name.

    Returns:
        List of (address, port, service_id) for healthy services.
    """
    c = get_consul_client()
    _, available_nodes = c.health.service(service_name_to_query)

    hosts = []
    for node in available_nodes:
        service = node["Service"]
        checks = node["Checks"]
        if all(check["Status"] == "passing" for check in checks):
            hosts.append((service["Address"], service["Port"], service["ID"]))

    return hosts


def get_random_service(service_name: str):
    """
    Returns a random healthy instance (address, port, service_id) for the given service name.
    Returns None if no healthy service is available.

    Returns:
        Tuple (address, port, service_id) or None
    """
    available_services = query_consul_services(service_name)
    if not available_services:
        return None
    return random.choice(available_services)


def read_value_for_key(key: str):
    """
    Reads and parses the value stored for a key in Consul's KV store.

    Returns:
        Dictionary if valid JSON is detected, None otherwise.
    """
    c = get_consul_client()
    _, data = c.kv.get(key)

    if data and data["Value"]:
        try:
            return json.loads(data["Value"].decode())
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for key: {key}")
            return None
    return None
