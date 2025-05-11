import consul
import os
import json
import numpy as np

def register_consul_service(
    service_name: str,
    service_id: str,
    service_address: str,
    service_port: int,
    timeout: int = None,
    interval: int = None,
    health_endpoint: str = None
):
    c = consul.Consul(host=os.environ['CONSUL_HOST'], port=os.environ['CONSUL_PORT'])

    check = None
    if health_endpoint:
        check = consul.Check.http(f"http://{service_address}:{service_port}{health_endpoint}", interval=f"{interval}s", timeout=f"{timeout}s", deregister="1m")
        
    c.agent.service.register(
        name=service_name,
        service_id=service_id,
        address=service_address,
        port=int(service_port),
        check=check
    )
    
    print(f"Registered a service `{service_name}` wtih id `{service_id}` at {service_address}:{service_port}")
    
def query_consul_services(
    service_name_to_query:str
):
    c = consul.Consul(host=os.environ['CONSUL_HOST'], port=os.environ['CONSUL_PORT'])
    
    index, available_nodes = c.health.service(service_name_to_query)
        
    hosts = []
    
    for node in available_nodes:
        service = node['Service']
        checks = node['Checks']
                
        if all(check['Status'] == 'passing' for check in checks):
            hosts.append((service['Address'],service['Port'], service['ID']))

    return hosts

def get_random_service(service_name: str):
    available_services = query_consul_services(service_name)
    
    if len(available_services) == 0:
        return ""
    
    host, port, id = available_services[np.random.choice(len(available_services))]
    return host, port, id

def read_value_for_key(
    key: str
):
    c = consul.Consul(host=os.environ['CONSUL_HOST'], port=os.environ['CONSUL_PORT'])
    
    index, data = c.kv.get(key)
    
    value = None
    if data and data['Value']:
        try:
            value = json.loads(data['Value'].decode())
        except json.JSONDecodeError as e:
            print("JSON parsing error occurred!")
            value = None
        
    return value