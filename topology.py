from profissa_lft import *

# Define host names
host1_name = "h1"
host2_name = "h2"

# Define switch name
switch_name = "s1"

# Instantiate hosts and switch
h1 = Host(name=host1_name)
h2 = Host(name=host2_name)

s1 = Switch(name=switch_name)

# Configure IPs and gateways for hosts
setIp("192.168.1.1", "24", h1.interface(0))
setIp("192.168.1.2", "24", h2.interface(0))

# Connect hosts to switch
connect(h1, s1.gn(0), s1.gn(1))   # This line is incorrect; gn() method does not exist for Switch.