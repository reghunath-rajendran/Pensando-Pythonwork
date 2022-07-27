import netmiko
import logging
import re
import sys
import os
import time
import logging

logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

router_ip = "192.168.68.128"
r_username = "admin"
r_password = "Pensando!2345"
ssh = netmiko.ConnectHandler(
    **{'device_type': 'aruba_os', 'ip': router_ip, 'username': r_username, 'password': r_password})
ssh.send_command("start-shell", expect_string="$")
def parse_vrf_hwid(vrfname):
    vrfs=ssh.send_command_timing("curl localhost:9007/api/vrfs/ | jq .", read_timeout=0)
    ssh.send_command("exit",expect_string="$")
    vrf_regex=vrfname+".*(.*\n){6}"
    vrf_search=re.search(vrf_regex,vrfs).group(0)
    vrf_uuid_line=re.search("uuid.*", vrf_search).group(0)
    vrf_uuid_l=re.split(":\s", vrf_uuid_line)
    vrf_uuid=re.findall('"([^"]*)"',vrf_uuid_l[1])
    ssh.send_command("diag", expect_string="#")
    ssh.send_command("diag dsm console 1/2", expect_string="$")
    vrf_out = ssh.send_command_timing("pdsctl show vpc --status -i " + vrf_uuid[0], read_timeout=0)
    vrf=[]
    table_header =  re.search(r'-+\n(.*)\n-+', vrf_out).group(1)
    table_data = re.search(r'^[a-f0-9].*',vrf_out,re.MULTILINE).group(0)
    vrf_data=table_data.split()
    header_names = table_header.split()
    vrf.append(dict(zip(header_names, vrf_data)))
    vrf_hw_id=vrf[0]["H/W"]
    return(vrf_hw_id)
vrf_hwid=parse_vrf_hwid("pod1")
vrf_flows = ssh.send_command_timing("pdsctl show flow --vpcid " + vrf_hwid, read_timeout=0)
print(vrf_flows)