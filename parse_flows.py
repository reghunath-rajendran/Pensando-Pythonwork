import netmiko
import logging
import re
import sys
import os
import time
import logging

logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

class Dsm_Flows:
    def __init__(self,flows):
        self.tcp_count = 0
        self.udp_count = 0
        self.icmp_count = 0
        self.others_count = 0
        f = flows.splitlines()
        j = re.compile("^[0-9].*")
        flows = list(filter(j.match, f))
        for i in flows:
            flows_split = re.split("(\s+)", i)
            if flows_split[14] == "TCP":
                self.tcp_count += 1
            elif flows_split[14] == "UDP":
                self.udp_count += 1
            elif flows_split[14] == "ICMP":
                self.icmp_count += 1
            else:
                self.others_count += 1
        #return (tcp_count, udp_count, icmp_count, others_count)

router_ip = "10.30.22.13"
r_username = "admin"
r_password = "N0isystem$"
ssh = netmiko.ConnectHandler(
    **{'device_type': 'aruba_os', 'ip': router_ip, 'username': r_username, 'password': r_password})
ssh.send_command("diag", expect_string="#")
ssh.send_command("diag dsm console 1/1", expect_string="$")
cli_output_flow_pre_change = ssh.send_command_timing("pdsctl show flow", read_timeout=0)
dsm1_pre_flows=Dsm_Flows(cli_output_flow_pre_change)
ssh.send_command("exit",expect_string="$")
ssh.send_command("diag", expect_string="#")
ssh.send_command("diag dsm console 1/2", expect_string="$")
cli_output_flow_pre_change = ssh.send_command_timing("pdsctl show flow", read_timeout=0)
dsm2_pre_flows=Dsm_Flows(cli_output_flow_pre_change)
ssh.send_command("exit",expect_string="$")
time.sleep(90)
ssh.send_command("diag", expect_string="#")
ssh.send_command("diag dsm console 1/1", expect_string="$")
cli_output_flow_post_change = ssh.send_command_timing("pdsctl show flow", read_timeout=0)
dsm1_post_flows = Dsm_Flows(cli_output_flow_post_change)
ssh.send_command("exit",expect_string="$")
ssh.send_command("diag", expect_string="#")
ssh.send_command("diag dsm console 1/2", expect_string="$")
cli_output_flow_post_change = ssh.send_command_timing("pdsctl show flow", read_timeout=0)
dsm2_post_flows = Dsm_Flows(cli_output_flow_post_change)
ssh.send_command("exit",expect_string="$")

if dsm1_pre_flows.udp_count != dsm1_post_flows.udp_count:
    print("DSM1: UDP flows count not matching : \n Pre: " + udp_count_pre + "\n Post: " + udp_count_post)
if dsm1_pre_flows.icmp_count != dsm1_post_flows.icmp_count:
    print("DSM1: ICMP flows count not matching : \n Pre: " + icmp_count_pre + "\n Post: " + icmp_count_post)
if dsm1_pre_flows.others_count != dsm1_post_flows.others_count:
    print("DSM1: Other flows count not matching : \n Pre: " + others_count_pre + "\n Post: " + others_count_post)
else:
    print("DSM1: FLows matching before and after")

if dsm2_pre_flows.udp_count != dsm2_post_flows.udp_count:
    print("DSM2: UDP flows count not matching : \n Pre: " + udp_count_pre + "\n Post: " + udp_count_post)
if dsm2_pre_flows.icmp_count != dsm2_post_flows.icmp_count:
    print("DSM2: ICMP flows count not matching : \n Pre: " + icmp_count_pre + "\n Post: " + icmp_count_post)
if dsm2_pre_flows.others_count != dsm2_post_flows.others_count:
    print("DSM2: Other flows count not matching : \n Pre: " + others_count_pre + "\n Post: " + others_count_post)
else:
    print("DSM2: FLows matching before and after")