import netifaces as ni
import os
import re

Sistema_operativo = "Linux" if os.name == "posix" else "Windows"

if Sistema_operativo == "Windows":
	import _winreg as wr

def get_connection_name_from_guid(iface_guids):
	iface_names = []
	reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
	reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
	for i in range(len(iface_guids)):
		try:
			reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + r'\Connection')
			iface_names.append(wr.QueryValueEx(reg_subkey, 'Name')[0].encode())
		except:
			pass
	return iface_names

def datos_interfaces():
	interfaces = ni.interfaces()
	lista_datos_iface = []
	for i in interfaces:
		if Sistema_operativo == "Windows":
			if get_connection_name_from_guid([i]):
				try:
					if ni.ifaddresses(i)[2][0]['netmask']:
						lista_datos_iface.append(get_connection_name_from_guid([i]) + [i] + ni.ifaddresses(i)[2])
				except:
					try:
						if ni.ifaddresses(i)[2]:
							lista_datos_iface.append(get_connection_name_from_guid([i]) + [i])
							lista_datos_iface[-1].append({})
					except:
						pass
		else:
			try:
				if ni.ifaddresses(i)[2][0]['netmask']:
					lista_datos_iface.append([i] + [i] + ni.ifaddresses(i)[2])
			except:
				try:
					if ni.ifaddresses(i)[2]:
						lista_datos_iface.append([i])
				except:
					pass

	gateways = ni.gateways()

	#OBTER GATEWAY
	
	for i in lista_datos_iface:
		for x in gateways[ni.AF_INET]:
			if i[1] in x:
				i[2]['gateway'] = x[0]
		if not 'gateway' in i[2]:
			i[2]['gateway'] = ""
				
	#OBTER DNS
	
	if Sistema_operativo == "Windows":
			for i in lista_datos_iface:
				dns_info = os.popen("netsh interface ipv4 show dns name="+i[0]).read()
				dns = re.findall("\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}",dns_info)
				if dns:
					i[2]['dns'] = dns
				else:
					i[2]['dns'] = ""
	
	for i in lista_datos_iface:
		print i
	
	return [i for i in lista_datos_iface if i[0] != "lo"]
	
for interface in datos_interfaces():
	print interface

	#### DNS

	#nslookup_info = os.popen("nslookup").read()
	#dns = re.findall('Address:(.+)',nslookup_info)