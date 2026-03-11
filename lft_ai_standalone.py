#!/usr/bin/env python3
"""
LFT AI - Lightweight Fog Testbed - Standalone Edition
=====================================================
Self-contained script that bundles ALL LFT functionality into a single file:
  - Network node management (Host, Switch, Controller, UE, EPC, EnB)
  - AI-powered topology generation (local models & Hugging Face API)
  - Real-time network telemetry collection
  - Live network visualization with matplotlib
  - CLI interface (generate / interactive / visualize / examples)

Usage:
  python lft_ai_standalone.py generate "Create an SDN topology with 2 hosts" -o topology.py
  python lft_ai_standalone.py interactive
  python lft_ai_standalone.py visualize --interval 1000
  python lft_ai_standalone.py examples

Dependencies are checked and installed automatically at startup.

Copyright (C) 2022-2024 Alexandre Mitsuru Kaihara - GPL v3
"""

# ============================================================================
# SECTION 0: Dependency bootstrap
# ============================================================================

import importlib
import subprocess as _sp
import sys

_REQUIRED = {
    # module_name: pip_package
    "requests": "requests>=2.25.0",
}
_OPTIONAL = {
    "docker": "docker",
    "pandas": "pandas",
    "torch": "torch>=2.0.0",
    "transformers": "transformers>=4.30.0",
    "accelerate": "accelerate>=0.20.0",
    "matplotlib": "matplotlib",
    "networkx": "networkx",
}

def _ensure_deps():
    """Check required deps and warn about optional ones."""
    missing_required = []
    for mod, pkg in _REQUIRED.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing_required.append(pkg)
    if missing_required:
        print(f"Installing required dependencies: {', '.join(missing_required)}")
        _sp.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + missing_required)

    missing_optional = []
    for mod, pkg in _OPTIONAL.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing_optional.append(pkg)
    if missing_optional:
        print(f"Note: Some optional features need: {', '.join(missing_optional)}")
        print(f"  Install with: pip install {' '.join(missing_optional)}")

_ensure_deps()

# ============================================================================
# SECTION 1: Standard library imports
# ============================================================================

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from configparser import ConfigParser
from json import load as json_load, dump as json_dump
from pathlib import Path
from typing import Optional, Dict, List, Any, Set, Tuple

# ============================================================================
# SECTION 2: Optional third-party imports (graceful fallback)
# ============================================================================

try:
    import docker
    HAS_DOCKER = True
except ImportError:
    docker = None
    HAS_DOCKER = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False

try:
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        GenerationConfig,
    )
    HAS_AI = True
except ImportError:
    HAS_AI = False

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import networkx as nx
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ============================================================================
# SECTION 3: Constants
# ============================================================================

# Docker commands
DOCKER_COMMAND = "docker"
DOCKER_RUN = DOCKER_COMMAND + " run"

# Docker run options
NETWORK = "--network"
NAME = "--name"
PRIVILEGED = "--privileged"
DNS = "--dns"
MEMORY = "--memory"
CPUS = "--cpus"

# UE config file
RF_SECTION = "rf"
DEVICE_ARGS_ATTR = "device_args"
DEVICE_NAME_ATTR = "device_name"
TX_GAIN_ATTR = "tx_gain"
RX_GAIN_ATTR = "rx_gain"
USIM_SECTION = "usim"
ALGORITHM_ATTR = "algo"
IMSI_ATTR = "imsi"

# PHY section
PHY_SECTION = "phy"
CORRECT_SYNC_ERROR = "correct_sync_error"

# EPC config file
MME_SECTION = "mme"
MME_BIND_ADDR = "mme_bind_addr"
SPGW_SECTION = "spgw"
GTPU_BIND_ADDR = "gtpu_bind_addr"
SGI_IF_ADDR = "sgi_if_addr"

# eNB config file
ENB_SECTION = "enb"
MME_ADDR = "mme_addr"
GTP_BIND_ADDR = "gtp_bind_addr"
S1C_BIND_ADDR = "s1c_bind_addr"

# ============================================================================
# SECTION 4: Exceptions
# ============================================================================

class InvalidCommandLineInput(Exception):
    pass

class MissingObjectParameter(Exception):
    pass

class NodeInstantiationFailed(Exception):
    pass

class InvalidNodeName(Exception):
    pass

class LFTException(Exception):
    pass

# ============================================================================
# SECTION 5: Node (base class for all network nodes)
# ============================================================================

# Forward declaration for type hints
class Node:
    pass


class Node:
    """Base superclass for all Docker-backed network nodes."""

    def __init__(self, nodeName: str) -> None:
        self.__createTmpFolder()
        self.__nodeName = nodeName
        self.memory = ''
        self.cpu = ''

    def __createTmpFolder(self) -> None:
        _sp.run("mkdir -p /tmp/lft/", shell=True)

    def instantiate(self, dockerImage="alexandremitsurukaihara/lst2.0:host", dockerCommand='', dns='8.8.8.8', memory='', cpus='', runCommand='') -> None:
        command = []

        def addDockerRun():
            command.append(DOCKER_RUN)
        def addRunOptions():
            command.append("-d")
        def addNetwork():
            command.append(NETWORK + "=none")
        def addContainerName():
            command.append(NAME + '=' + self.getNodeName())
        def addPrivileged():
            command.append(PRIVILEGED)
        def addDNS(dns):
            command.append(DNS + '=' + dns)
        def addContainerMemory(memory):
            if memory != '':
                command.append(MEMORY + '=' + memory)
        def addContainerCPUs(cpus):
            if cpus != '':
                command.append(CPUS + '=' + cpus)
        def addContainerImage(image):
            command.append(image)
        def addRunCommand(runCommand):
            command.append(runCommand)
        def buildCommand():
            return " ".join(command)

        if not self.__imageExists(dockerImage):
            logging.info(f"Image {dockerImage} not found, pulling from remote repository...")
            self.__pullImage(dockerImage)

        if dockerCommand == '':
            addDockerRun()
            addRunOptions()
            addNetwork()
            addContainerName()
            addPrivileged()
            addDNS(dns)
            addContainerMemory(memory)
            addContainerCPUs(cpus)
            addContainerImage(dockerImage)
            addRunCommand(runCommand)

        try:
            if dockerCommand != '':
                _sp.run(dockerCommand, shell=True, capture_output=True)
            else:
                _sp.run(buildCommand(), shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error while criating the container {self.getNodeName()}: {str(ex)}")
            raise NodeInstantiationFailed(f"Error while criating the container {self.getNodeName()}: {str(ex)}")

        self.__enableNamespace(self.getNodeName())

    def __imageExists(self, image: str) -> bool:
        out = _sp.run(f"docker inspect --type=image {image}", shell=True, capture_output=True)
        outJson = json.loads(out.stdout.decode('utf-8'))
        if outJson == []:
            return False
        return True

    def __pullImage(self, image):
        try:
            _sp.run(f"docker pull {image}", shell=True)
        except Exception as ex:
            logging.error(f"Error pulling non-existing {image} image: {str(ex)}")
            raise NodeInstantiationFailed(f"Error pulling non-existing {image} image: {str(ex)}")

    def delete(self) -> None:
        try:
            _sp.run(f"docker kill {self.getNodeName()} && docker rm {self.getNodeName()}", shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")
            raise NodeInstantiationFailed(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")

    def setIp(self, ip: str, mask: int, interfaceName: str) -> None:
        if not self.__interfaceExists(interfaceName):
            logging.error(f"Network interface {interfaceName} does not exist")
            raise Exception(f"Network interface {interfaceName} does not exist")
        self.__setIp(ip, mask, interfaceName)

    def connect(self, node: 'Node', interfaceName: str, peerInterfaceName: str) -> None:
        if self.__interfaceExists(interfaceName) or self.__interfaceExists(peerInterfaceName):
            logging.error(f"Cannot connect to {node.getNodeName()}, {interfaceName} or {peerInterfaceName} already exists")
            raise Exception(f"Cannot connect to {node.getNodeName()}, {interfaceName} or {peerInterfaceName} already exists")

        self.__create(interfaceName, peerInterfaceName)
        self.__setInterface(self.getNodeName(), interfaceName)
        self.__setInterface(node.getNodeName(), peerInterfaceName)

        if self.__class__.__name__ == 'Switch':
            self._Switch__createPort(self.getNodeName(), self.__getThisInterfaceName(node))
        if node.__class__.__name__ == 'Switch':
            node._Switch__createPort(node.getNodeName(), node.__getThisInterfaceName(self))

    def connectToInternet(self, hostIP: str, hostMask: int, interfaceName: str, hostInterfaceName: str) -> None:
        self.__create(interfaceName, hostInterfaceName)
        self.__setInterface(self.getNodeName(), interfaceName)
        if self.__class__.__name__ == 'Switch':
            self._Switch__createPort(self.getNodeName(), interfaceName)

        _sp.run(f"ip link set {hostInterfaceName} up", shell=True)
        _sp.run(f"ip addr add {hostIP}/{hostMask} dev {hostInterfaceName}", shell=True)

        hostGatewayInterfaceName = _sp.run(f"route | grep '^default' | grep -o '[^ ]*$'", shell=True, capture_output=True).stdout.decode('utf8').replace("\n", '')
        _sp.run(f"iptables -t nat -I POSTROUTING -o {hostGatewayInterfaceName} -j MASQUERADE", shell=True)
        _sp.run(f"iptables -t nat -I POSTROUTING -o {hostInterfaceName} -j MASQUERADE", shell=True)
        _sp.run(f"iptables -A FORWARD -i {hostInterfaceName} -o {hostGatewayInterfaceName} -j ACCEPT", shell=True)
        _sp.run(f"iptables -A FORWARD -i {hostGatewayInterfaceName} -o {hostInterfaceName} -j ACCEPT", shell=True)
        _sp.run(f"firewall-cmd --zone=trusted --add-interface={hostInterfaceName}", shell=True)

    def connectToInternetWithoutNAT(self, hostIP: str, hostMask: int, interfaceName: str, hostInterfaceName: str) -> None:
        self.__create(interfaceName, hostInterfaceName)
        self.__setInterface(self.getNodeName(), interfaceName)
        if self.__class__.__name__ == 'Switch':
            self._Switch__createPort(self.getNodeName(), interfaceName)

        _sp.run(f"ip link set {hostInterfaceName} up", shell=True)
        _sp.run(f"ip addr add {hostIP}/{hostMask} dev {hostInterfaceName}", shell=True)
        _sp.run(f"firewall-cmd --zone=trusted --add-interface={hostInterfaceName}", shell=True)

    def enableForwarding(self, interfaceName: str, otherInterfaceName: str) -> None:
        self.run(f"iptables -t nat -I POSTROUTING -o {otherInterfaceName} -j MASQUERADE")
        self.run(f"iptables -t nat -I POSTROUTING -o {interfaceName} -j MASQUERADE")
        self.run(f"iptables -A FORWARD -i {interfaceName} -o {otherInterfaceName} -j ACCEPT")
        self.run(f"iptables -A FORWARD -i {otherInterfaceName} -o {interfaceName} -j ACCEPT")

    def getNodeName(self) -> str:
        return self.__nodeName

    def addRoute(self, ip: str, mask: int, interfaceName: str):
        if not self.__interfaceExists(interfaceName):
            logging.error(f"Network interface {interfaceName} does not exist")
            raise Exception(f"Network interface {interfaceName} does not exist")
        try:
            _sp.run(f"docker exec {self.getNodeName()} ip route add {ip}/{mask} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error adding route {ip}/{mask} via {interfaceName} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error adding route {ip}/{mask} via {interfaceName} in {self.getNodeName()}: {str(ex)}")

    def addRouteOnHost(self, ip: str, mask: int, interfaceName: str, gateway="0.0.0.0") -> None:
        try:
            _sp.run(f"ip route add {ip}/{mask} via {gateway} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error adding route {ip}/{mask} via {interfaceName} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error adding route {ip}/{mask} via {interfaceName} in {self.getNodeName()}: {str(ex)}")

    def setDefaultGateway(self, destinationIp: str, interfaceName: str) -> None:
        if not self.__interfaceExists(interfaceName):
            logging.error(f"Network interface {interfaceName} does not exist")
            raise Exception(f"Network interface {interfaceName} does not exist")

        self.addRoute(destinationIp, 32, interfaceName)
        try:
            _sp.run(f"docker exec {self.getNodeName()} route add default gw {destinationIp} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while setting gateway {destinationIp} on device {interfaceName} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error while setting gateway {destinationIp} on device {interfaceName} in {self.getNodeName()}: {str(ex)}")

    def run(self, command: str) -> str:
        try:
            command = command.replace('\"', 'DOUBLEQUOTESDELIMITER')
            command = f"docker exec {self.getNodeName()} bash -c \"" + command + f"\""
            command = command.replace('DOUBLEQUOTESDELIMITER', '\\"')
            return _sp.Popen(command, shell=True, stdout=_sp.PIPE, text=True)
        except Exception as ex:
            logging.error(f"Error executing command {command} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error executing command {command} in {self.getNodeName()}: {str(ex)}")

    def runs(self, commands: list) -> list:
        return [self.run(command) for command in commands]

    def copyLocalToContainer(self, path: str, destPath: str) -> None:
        try:
            _sp.run(f"docker cp {path} {self.getNodeName()}:{destPath}", shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error copying file from {path} to {destPath}: {str(ex)}")
            raise Exception(f"Error copying file from {path} to {destPath}: {str(ex)}")

    def copyContainerToLocal(self, path: str, destPath: str) -> None:
        try:
            _sp.run(f"docker cp {self.getNodeName()}:{path} {destPath}", shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error copying file from {path} to {destPath}: {str(ex)}")
            raise Exception(f"Error copying file from {path} to {destPath}: {str(ex)}")

    def __interfaceExists(self, interfaceName: str) -> bool:
        out = _sp.run(f"docker exec {self.getNodeName()} ip link | grep {interfaceName}", shell=True, capture_output=True)
        return out.stdout.decode("utf8") != ''

    def __getThisInterfaceName(self, node: 'Node') -> str:
        return self.getNodeName() + node.getNodeName()

    def __setIp(self, ip: str, mask: int, interfaceName: str) -> None:
        try:
            _sp.run(f"ip -n {self.getNodeName()} addr add {ip}/{mask} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while setting IP {ip}/{mask} to virtual interface {interfaceName}: {str(ex)}")
            raise Exception(f"Error while setting IP {ip}/{mask} to virtual interface {interfaceName}: {str(ex)}")

    def __getOtherInterfaceName(self, node: 'Node') -> str:
        return node.getNodeName() + self.getNodeName()

    def __create(self, peer1Name: str, peer2Name: str) -> None:
        try:
            _sp.run(f"ip link add {peer1Name} type veth peer name {peer2Name}", shell=True)
        except Exception as ex:
            logging.error(f"Error while creating virtual interfaces {peer1Name} and {peer2Name}: {str(ex)}")
            raise Exception(f"Error while creating virtual interfaces {peer1Name} and {peer2Name}: {str(ex)}")

    def __setInterface(self, nodeName: str, peerName: str) -> None:
        try:
            _sp.run(f"ip link set {peerName} netns {nodeName}", shell=True)
            _sp.run(f"ip -n {nodeName} link set {peerName} up", shell=True)
        except Exception as ex:
            logging.error(f"Error while setting virtual interfaces {peerName} to {nodeName}: {str(ex)}")
            raise Exception(f"Error while setting virtual interfaces {peerName} to {nodeName}: {str(ex)}")

    def __enableNamespace(self, nodeName) -> None:
        try:
            _sp.run(f"pid=$(docker inspect -f '{{{{.State.Pid}}}}' {nodeName}); mkdir -p /var/run/netns/; ln -sfT /proc/$pid/ns/net /var/run/netns/{nodeName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")

    def __getAllIntefaces(self) -> list:
        output = _sp.run(f"docker exec {self.getNodeName()} ifconfig -a | sed 's/[ \t].*//;/^$/d'", shell=True, capture_output=True)
        interfaces = output.stdout.decode('utf8').replace(":", '').split('\n')
        return list(filter(None, interfaces))

    def __isActive(self) -> bool:
        if _sp.run(f"docker ps | grep {self.getNodeName()}'", shell=True, capture_output=True).stdout.decode('utf8') != '':
            return True
        return False

    def setMtuSize(self, interfaceName: str, mtu: int) -> None:
        self.run(f"ifconfig {interfaceName} mtu {str(mtu)}")

    def readConfigFile(self, containerPath: str) -> None:
        randomTmpName = self.getHashFromString(containerPath)
        self.copyContainerToLocal(containerPath, f"/tmp/lft/{randomTmpName}")
        config = ConfigParser()
        config.read(f"/tmp/lft/{randomTmpName}")
        return config

    def saveConfig(self, config: ConfigParser, containerPath: str) -> None:
        randomTmpName = self.getHashFromString(containerPath)
        with open(f"/tmp/lft/{randomTmpName}", "w") as f:
            config.write(f)
        self.copyLocalToContainer(f"/tmp/lft/{randomTmpName}", containerPath)

    def getHashFromString(self, anyStr: str) -> str:
        h = hashlib.md5()
        h.update(anyStr.encode('utf-8'))
        return h.hexdigest()

    def setHost(self, ip: str) -> None:
        result = self.run(f"hostname")
        hostname = result.stdout.read().replace("\n", "")
        self.run(f"HOSTNAME=$(hostname) && echo \"{ip} {hostname}\" >> /etc/hosts")

    def acceptPacketsFromInterface(self, interfaceName: str):
        self.run(f"iptables -A INPUT -i {interfaceName} -j ACCEPT")

    def setInterfaceProperties(self, interfaceName: str, throughput: str, delay: str, jitter: str) -> None:
        self.run(f"tc qdisc add dev {interfaceName} root netem delay {delay} {jitter} rate {throughput}")


# ============================================================================
# SECTION 6: Concrete node types
# ============================================================================

class Host(Node):
    """Simple network host."""
    pass


class Controller(Node):
    """SDN controller (Ryu)."""

    def __init__(self, nodeName: str) -> None:
        super().__init__(nodeName)
        self.__process = 0

    def instantiate(self, dockerImage='alexandremitsurukaihara/lst2.0:ryucontroller', dockerCommand='') -> None:
        super().instantiate(dockerImage=dockerImage, dockerCommand=dockerCommand)

    def initController(self, ip: str, port: int, command=[]):
        try:
            if len(command) == 0:
                _sp.run(f"docker exec {self.getNodeName()} ryu-manager --ofp-listen-host={ip} --ofp-tcp-listen-port={port} /home/controller.py > /dev/null 2>&1 &", shell=True)
            else:
                for c in command:
                    _sp.run(c, shell=True)
        except Exception as ex:
            logging.error(f"Error while setting up controller {self.getNodeName()} in {ip}/{port}: {str(ex)}")
            raise Exception(f"Error while setting up controller {self.getNodeName()} in {ip}/{port}: {str(ex)}")

    def instantiate_local(self, controllerIp, controllerPort):
        process = self.__getProcess()
        if process == 0:
            try:
                self.__process = _sp.Popen(f"ryu-manager --ofp-listen-host={controllerIp} --ofp-tcp-listen-port={controllerPort} controller.py > controller.log", shell=True, stdout=_sp.PIPE, stderr=_sp.STDOUT)
            except Exception as ex:
                logging.error(f"Error while creating the switch {self.getNodeName()}: {str(ex)}")
                raise NodeInstantiationFailed(f"Error while creating the switch {self.getNodeName()}: {str(ex)}")
        else:
            logging.error(f"Controller {self.getNodeName()} already instantiated")
            raise Exception(f"Controller {self.getNodeName()} already instantiated")

    def delete_local(self):
        process = self.__getProcess()
        if process != 0:
            try:
                self.__process.kill()
                _, stderr = self.__process.communicate()
            except Exception as ex:
                logging.error(f"Error while deleting the switch {self.getNodeName()}: {str(ex)}\nThreads error: {stderr}")
                raise NodeInstantiationFailed(f"Error while deleting the switch {self.getNodeName()}: {str(ex)}\nThreads error: {stderr}")
        else:
            logging.error(f"Can't delete {self.getNodeName()}. {self.getNodeName()} was not instantiated.")
            raise Exception(f"Can't delete {self.getNodeName()}. {self.getNodeName()} was not instantiated.")

    def __getProcess(self):
        return self.__process


class Switch(Node):
    """OpenFlow / OVS switch."""

    def __init__(self, name: str, hostPath='', containerPath=''):
        super().__init__(name)
        if hostPath == '' and containerPath == '':
            self.__mount = False
        elif hostPath != '' and containerPath != '':
            self.__hostPath = hostPath
            self.__containerPath = containerPath
            self.__mount = True
        else:
            raise Exception(f"Invalid hostPath and containerPath mount point on {self.getNodeName()}. hostPath and containerPath cannot be null")

    def instantiate(self, image='alexandremitsurukaihara/lst2.0:openvswitch', controllerIP='', controllerPort=-1) -> None:
        mount = ''
        if self.__mount:
            mount = f'-v {self.__hostPath}:{self.__containerPath}'
        super().instantiate(dockerCommand=f"docker run -d --network=none --privileged {mount} --name={self.getNodeName()} {image}")
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl add-br {self.getNodeName()}", shell=True)
            _sp.run(f"docker exec {self.getNodeName()} ip link set {self.getNodeName()} up", shell=True)
        except Exception as ex:
            logging.error(f"Error while creating the switch {self.getNodeName()}: {str(ex)}")
            raise NodeInstantiationFailed(f"Error while creating the switch {self.getNodeName()}: {str(ex)}")
        if controllerIP != '' and controllerPort != -1:
            self.setController(controllerIP, controllerPort)

    def setController(self, ip: str, port: int) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl set-controller {self.getNodeName()} tcp:{ip}:{str(port)}", shell=True)
        except Exception as ex:
            logging.error(f"Error connecting switch {self.getNodeName()} to controller on IP {ip}/{port}: {str(ex)}")
            raise Exception(f"Error connecting switch {self.getNodeName()} to controller on IP {ip}/{port}: {str(ex)}")

    def __createPort(self, nodeName, peerName) -> None:
        try:
            _sp.run(f"docker exec {nodeName} ovs-vsctl add-port {nodeName} {peerName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while creating port {peerName} in switch {nodeName}: {str(ex)}")
            raise Exception(f"Error while creating port {peerName} in switch {nodeName}: {str(ex)}")

    def setIp(self, ip: str, mask: int, interfaceName='') -> None:
        if interfaceName == '':
            interfaceName = self.getNodeName()
        self._Node__setIp(ip, mask, interfaceName)

    def enableNetflow(self, destIp: str, destPort: int, activeTimeout=60) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl -- set Bridge {self.getNodeName()} netflow=@nf --  --id=@nf create  NetFlow  targets=\\\"{destIp}:{destPort}\\\"  active-timeout={activeTimeout}", shell=True)
        except Exception as ex:
            logging.error(f"Error setting Netflow on {self.getNodeName()} switch: {str(ex)}")
            raise Exception(f"Error setting Netflow on {self.getNodeName()} switch: {str(ex)}")

    def clearNetflow(self) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl clear Bridge {self.getNodeName()} netflow", shell=True)
        except Exception as ex:
            logging.error(f"Error clearing Netflow on {self.getNodeName()} switch: {str(ex)}")
            raise Exception(f"Error clearing Netflow on {self.getNodeName()} switch: {str(ex)}")

    def enablesFlow(self, destIp: str, destPort: int, header=128, sampling=64, polling=10) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl -- --id=@s create sFlow agent={self.getNodeName()} target=\\\"{destIp}:{destPort}\\\" header={str(header)} sampling={str(sampling)} polling={str(polling)} -- set Bridge {self.getNodeName()} sflow=@s", shell=True)
        except Exception as ex:
            logging.error(f"Error setting sFlow on {self.getNodeName()} switch: {str(ex)}")
            raise Exception(f"Error setting sFlow on {self.getNodeName()} switch: {str(ex)}")

    def clearsFlow(self) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl clear Bridge {self.getNodeName()} sflow", shell=True)
        except Exception as ex:
            logging.error(f"Error clearing sFlow on {self.getNodeName()} switch: {str(ex)}")
            raise Exception(f"Error clearing sFlow on {self.getNodeName()} switch: {str(ex)}")

    def enableIPFIX(self, destIp: str, destPort: int, obsDomainId=123, obsPointId=456, cacheActiveTimeout=60, cacheMaxFlow=60, enableInputSampling=False, enableTunnelSampling=True) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl -- set Bridge {self.getNodeName()} ipfix=@i -- --id=@i create IPFIX targets=\\\"{destIp}:{destPort}\\\" obs_domain_id={str(obsDomainId)} obs_point_id={str(obsPointId)} cache_active_timeout={str(cacheActiveTimeout)} cache_max_flows={str(cacheMaxFlow)} other_config:enable-input-sampling={str(enableInputSampling).lower()} other_config:enable-tunnel-sampling={str(enableTunnelSampling).lower()}", shell=True)
        except Exception as ex:
            logging.error(f"Error setting IPFIX on {self.getNodeName()} switch: {str(ex)}")
            raise Exception(f"Error setting IPFIX on {self.getNodeName()} switch: {str(ex)}")

    def clearIPFIX(self) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ovs-vsctl clear Bridge {self.getNodeName()} ipfix", shell=True)
        except Exception as ex:
            logging.error(f"Error clearing IPFIX on {self.getNodeName()} switch: {str(ex)}")
            raise Exception(f"Error clearing IPFIX on {self.getNodeName()} switch: {str(ex)}")

    def collectFlows(self, nodes=[], path='', rotateInterval=60, sniffAll=False) -> None:
        try:
            interfaces = self._Node__getAllIntefaces()
            if sniffAll == False:
                if len(nodes) > 0:
                    interfaces = [self._Node__getThisInterfaceName(node) for node in nodes]
                    interfaces.append(self.getNodeName())
                else:
                    raise Exception(f"Expected at least one node reference to sniff packets on {self.getNodeName()} switch")
            interfaces = list(set(interfaces) - set(['lo', 'ovs-system']))
            options = ['-i ' + interface for interface in interfaces]
            options = ' '.join(options)
            _sp.run(f"docker exec {self.getNodeName()} tshark {options} -b duration:{rotateInterval} -w {path}/dump.pcap > /dev/null 2>&1 &", shell=True)
        except Exception as ex:
            logging.error(f"Error set the collector on {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error set the collector on {self.getNodeName()}: {str(ex)}")

    def __addDefaultRoute(self) -> None:
        try:
            _sp.run(f"docker exec {self.getNodeName()} ip route add 0.0.0.0/0 dev {self.getNodeName()}", shell=True)
        except Exception as ex:
            logging.error(f"Error adding route default route for switch {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error adding route default route for switch {self.getNodeName()}: {str(ex)}")


class Perfsonar(Node):
    """Base class for performance/measurement nodes (srsRAN)."""

    def instantiate(self, dockerImage='alexandremitsurukaihara/lft:srsran', dockerCommand='', dns='8.8.8.8', runCommand='', cpus='', memory='') -> None:
        super().instantiate(dockerImage=dockerImage, dockerCommand=dockerCommand, dns=dns, runCommand=runCommand, cpus=cpus, memory=memory)

    def readLimitFile(self, limitPath="/etc/pscheduler/limits.conf"):
        randomTmpName = self.getHashFromString(limitPath)
        self.copyContainerToLocal(limitPath, f"/tmp/lft/{randomTmpName}")
        with open(f"/tmp/lft/{randomTmpName}") as f:
            self.limitData = json_load(f)

    def saveLimitFile(self, limitPath="/etc/pscheduler/limits.conf"):
        randomTmpName = self.getHashFromString(limitPath)
        with open(f"/tmp/lft/{randomTmpName}", "w") as f:
            json_dump(self.limitData, f)
        self.copyLocalToContainer(f"/tmp/lft/{randomTmpName}", limitPath)

    def addRouteException(self, ip: str, netmask: int) -> None:
        self.limitData['identifiers'][2]['data']['exclude'].append(f"{ip}/{netmask}")


class UE(Perfsonar):
    """User Equipment for 4G/LTE (srsRAN)."""

    def __init__(self, name: str, ueConfigPath='/etc/srsran/ue.conf', buildDir='/srsRAN/build'):
        super().__init__(name)
        self.configPath = ueConfigPath
        self.config = None
        self.buildDir = buildDir

    def instantiate(self, dockerImage='alexandremitsurukaihara/lft:srsran', dockerCommand='', dns='8.8.8.8', runCommand='', cpus='', memory='') -> None:
        super().instantiate(dockerImage, dockerCommand, dns, runCommand=runCommand, cpus=cpus, memory=memory)
        self.config = self.readConfigFile(self.configPath)

    def start(self, deviceArgs='') -> None:
        super().run(f"{self.buildDir}/srsue/src/srsue {deviceArgs} > {self.buildDir}/ue.out &")

    def stop(self) -> None:
        self.run(f"pkill -f -9 srsue")

    def setConfigPath(self, path: str) -> None:
        self.configPath = path

    def getConfigPath(self) -> str:
        return self.configPath

    def setConfigurationFile(self, filePath: str, destinationPath='') -> None:
        if destinationPath == '':
            destinationPath = self.configPath
        super().copyLocalToContainer(filePath, destinationPath)

    def setDeviceArgs(self, deviceArgs: str) -> None:
        self.config[RF_SECTION][DEVICE_ARGS_ATTR] = deviceArgs
        self.saveConfig(self.config, self.configPath)

    def setDeviceName(self, deviceName: str) -> None:
        self.config[RF_SECTION][DEVICE_NAME_ATTR] = deviceName
        self.saveConfig(self.config, self.configPath)

    def setTxGain(self, txGain: int) -> None:
        self.config[RF_SECTION][TX_GAIN_ATTR] = txGain
        self.saveConfig(self.config, self.configPath)

    def setRxGain(self, rxGain: int) -> None:
        self.config[RF_SECTION][RX_GAIN_ATTR] = rxGain
        self.saveConfig(self.config, self.configPath)

    def setAuthenticationAlgorithm(self, algorithmName: str) -> None:
        self.config[USIM_SECTION][ALGORITHM_ATTR] = algorithmName
        self.saveConfig(self.config, self.configPath)

    def setUEID(self, id: str) -> None:
        self.config[USIM_SECTION][IMSI_ATTR] = id
        self.saveConfig(self.config, self.configPath)

    def setCorrectSyncError(self, enable: bool) -> None:
        self.config[PHY_SECTION][CORRECT_SYNC_ERROR] = "true" if enable else "false"
        self.saveConfig(self.config, self.configPath)


class EPC(Perfsonar):
    """Evolved Packet Core for 4G (srsRAN)."""

    def __init__(self, name: str):
        super().__init__(name)
        self.defaultEPCConfigPath = '/etc/srsran/epc.conf'
        self.configEPC = None
        self.defaultEPCUserDbPath = '/etc/srsran/user_db.csv'
        self.userDb = None
        self.buildDir = "/srsRAN/build"

    def instantiate(self, dockerImage='alexandremitsurukaihara/lft:srsran', runCommand='') -> None:
        super().instantiate(dockerImage=dockerImage, runCommand=runCommand)
        self.configEPC = self.readConfigFile(self.defaultEPCConfigPath)
        self.userDb = self.createUserDb()

    def start(self) -> None:
        self.run(f"{self.buildDir}/srsepc/src/srsepc > {self.buildDir}/epc.out &")

    def stop(self) -> None:
        self.run("pkill -f -9 srsepc")

    def setDefaultEPCConfigPath(self, path: str) -> None:
        self.defaultEPCConfigPath = path

    def getDefaultEPCConfigPath(self) -> str:
        return self.defaultEPCConfigPath

    def setEPCAddress(self, ip='127.0.1.100') -> None:
        self.configEPC[MME_SECTION][MME_BIND_ADDR] = ip
        self.configEPC[SPGW_SECTION][GTPU_BIND_ADDR] = ip
        self.saveConfig(self.configEPC, self.defaultEPCConfigPath)

    def setSgiInterfaceAddress(self, ip='172.16.0.1') -> None:
        self.configEPC[SPGW_SECTION][SGI_IF_ADDR] = ip
        self.saveConfig(self.configEPC, self.defaultEPCConfigPath)

    def addNewUE(self, name: str, ID: str, IP="dynamic") -> None:
        if not HAS_PANDAS:
            raise LFTException("pandas is required for EPC user database. Install with: pip install pandas")
        newRow = {
            "Name": name, "Auth": "mil", "IMSI": ID,
            "Key": "00112233445566778899aabbccddeeff",
            "OP_Type": "opc", "OP/OPc": "63bfa50ee6523365ff14c1f45f88737d",
            "AMF": "9001", "SQN": "000000001234", "QCI": "7", "IP_alloc": IP
        }
        self.userDb.loc[len(self.userDb)] = newRow
        self.saveUserDb()

    def createUserDb(self):
        if not HAS_PANDAS:
            return None
        return pd.DataFrame(columns=["Name", "Auth", "IMSI", "Key", "OP_Type", "OP/OPc", "AMF", "SQN", "QCI", "IP_alloc"])

    def saveUserDb(self) -> None:
        randomTmpName = self.getHashFromString(self.defaultEPCUserDbPath)
        self.userDb.to_csv(f"/tmp/lft/{randomTmpName}", header=None, index=False)
        self.copyLocalToContainer(f"/tmp/lft/{randomTmpName}", self.defaultEPCUserDbPath)


class EnB(Perfsonar):
    """eNodeB for 4G (srsRAN base station)."""

    def __init__(self, name: str, eNBConfigPath='/etc/srsran/enb.conf'):
        super().__init__(name)
        self.defaultEnBConfigPath = eNBConfigPath
        self.buildDir = '/srsRAN/build'
        self.config = None
        self.defaultMultiUEPath = self.buildDir + '/multiUE.py'
        self.defaultSingleUEPath = self.buildDir + '/singleUE.py'

    def instantiate(self, dockerImage='alexandremitsurukaihara/lft:srsran', dockerCommand='', dns='8.8.8.8', runCommand='') -> None:
        super().instantiate(dockerImage=dockerImage, dockerCommand=dockerCommand, dns=dns, runCommand=runCommand)
        self.config = self.readConfigFile(self.defaultEnBConfigPath)

    def start(self, transmitterIp="*", transmitterPort=2000, receiverIp="localhost", receiverPort=2001) -> None:
        super().run(f"{self.buildDir}/srsenb/src/srsenb --rf.device_name=zmq --rf.device_args='fail_on_disconnect=true,tx_port=tcp://{transmitterIp}:{transmitterPort},rx_port=tcp://{receiverIp}:{receiverPort},id=enb,base_srate=11.52e6' > enb.log")

    def stop(self) -> None:
        super().run("pkill -f -9 srsenb")

    def setDefaultEnBConfigPath(self, path: str) -> None:
        self.defaultEnBConfigPath = path

    def getdefaultEnBConfigPath(self) -> None:
        return self.defaultEnBConfigPath

    def setConfigurationFile(self, filePath: str, destinationPath='') -> None:
        if destinationPath == '':
            destinationPath = self.defaultEnBConfigPath
        super().copyLocalToContainer(filePath, destinationPath)

    def starGnuRadioMultiUE(self, multiUEPath='') -> None:
        if multiUEPath == '':
            multiUEPath = self.defaultMultiUEPath
        super().run(f"python3 {multiUEPath}")

    def starGnuRadioSingleUE(self, singleUEPath='') -> None:
        if singleUEPath == '':
            singleUEPath = self.defaultSingleUEPath
        super().run(f"python3 {singleUEPath}")

    def stopGnuRadioMultiUE(self) -> None:
        super().run(f"pkill -f -9 multiUE")

    def setMultiUEEnBAddr(self, txIP: str, txPort: int, rxIP: str, rxPort: int, multiUEPath='') -> None:
        if multiUEPath == '':
            multiUEPath = self.defaultMultiUEPath
        self.run(f"sed -i \"/zeromq_req_source_2/s@'tcp://.*'@'tcp://{txIP}:{txPort}'@\" {multiUEPath}")
        self.run(f"sed -i \"/zeromq_rep_sink_0/s@'tcp://.*'@'tcp://{rxIP}:{rxPort}'@\" {multiUEPath}")

    def setMultiUEUE1Addr(self, UEIP: str, txPort: int, eNBIP: str, rxPort: int, multiUEPath='') -> None:
        if multiUEPath == '':
            multiUEPath = self.defaultMultiUEPath
        self.run(f"sed -i \"/zeromq_req_source_1/s@'tcp://.*'@'tcp://{UEIP}:{txPort}'@\" {multiUEPath}")
        self.run(f"sed -i \"/zeromq_rep_sink_2/s@'tcp://.*'@'tcp://{eNBIP}:{rxPort}'@\" {multiUEPath}")

    def setMultiUEUE2Addr(self, UEIP: str, txPort: int, eNBIP: str, rxPort: int, multiUEPath='') -> None:
        if multiUEPath == '':
            multiUEPath = self.defaultMultiUEPath
        self.run(f"sed -i \"/zeromq_req_source_0/s@'tcp://.*'@'tcp://{UEIP}:{txPort}'@\" {multiUEPath}")
        self.run(f"sed -i \"/zeromq_rep_sink_1/s@'tcp://.*'@'tcp://{eNBIP}:{rxPort}'@\" {multiUEPath}")

    def setSingleUEEnBAddr(self, txIP: str, txPort: int, rxIP: str, rxPort: int) -> None:
        self.run(f"sed -i \"/zeromq_req_source_enb/s@'tcp://.*'@'tcp://{txIP}:{txPort}'@\" {self.defaultSingleUEPath}")
        self.run(f"sed -i \"/zeromq_rep_sink_enb/s@'tcp://.*'@'tcp://{rxIP}:{rxPort}'@\" {self.defaultSingleUEPath}")

    def setSingleUEUEAddr(self, UEIP: str, txPort: int, eNBIP: str, rxPort: int) -> None:
        self.run(f"sed -i \"/zeromq_req_source_ue/s@'tcp://.*'@'tcp://{UEIP}:{txPort}'@\" {self.defaultSingleUEPath}")
        self.run(f"sed -i \"/zeromq_rep_sink_ue/s@'tcp://.*'@'tcp://{eNBIP}:{rxPort}'@\" {self.defaultSingleUEPath}")

    def setDeviceArgs(self, deviceArgs: str) -> None:
        self.config[RF_SECTION][DEVICE_ARGS_ATTR] = deviceArgs
        self.saveConfig(self.config, self.defaultEnBConfigPath)

    def setDeviceName(self, deviceName: str) -> None:
        self.config[RF_SECTION][DEVICE_NAME_ATTR] = deviceName
        self.saveConfig(self.config, self.defaultEnBConfigPath)

    def setEPCAddress(self, ip: str) -> None:
        self.config[ENB_SECTION][MME_ADDR] = ip
        self.saveConfig(self.config, self.defaultEnBConfigPath)

    def setEnBAddress(self, ip: str) -> None:
        self.config[ENB_SECTION][GTP_BIND_ADDR] = ip
        self.config[ENB_SECTION][S1C_BIND_ADDR] = ip
        self.saveConfig(self.config, self.defaultEnBConfigPath)


class CICFlowMeter(Node):
    """Flow analysis tool for PCAP files."""

    def __init__(self, name: str, hostPath='', containerPath=''):
        super().__init__(name)
        self.__mount = False
        if hostPath != '' and containerPath != '':
            self.__hostPath = hostPath
            self.__containerPath = containerPath
            self.__mount = True
        else:
            raise Exception(f"Invalid hostPath and containerPath mount point on {self.getNodeName()}. hostPath and containerPath cannot be null")

    def instantiate(self, image='alexandremitsurukaihara/lst2.0:cicflowmeter') -> None:
        mount = ''
        if self.__mount:
            mount = f'-v {self.__hostPath}:{self.__containerPath}'
        super().instantiate(dockerCommand=f"docker run -d --network=none --privileged {mount} --name={self.getNodeName()} {image}")

    def analyze(self, pcapPath: str, destPath) -> None:
        self.run(f'./TCPDUMP_and_CICFlowMeter-master/convert_pcap_csv.sh {pcapPath}')
        self.run('find /TCPDUMP_and_CICFlowMeter-master/csv -type f -exec mv {}' + f' {destPath} \\;')


# ============================================================================
# SECTION 7: Telemetry
# ============================================================================

def get_docker_client():
    """Create a Docker client from the environment, or return None."""
    if not HAS_DOCKER:
        return None
    try:
        return docker.from_env()
    except Exception:
        return None


def guess_node_type(name: str) -> str:
    """Guess LFT node type from container name (fallback heuristic)."""
    if name.startswith('h') and len(name) <= 3:
        return 'host'
    elif name.startswith('s') and len(name) <= 3:
        return 'switch'
    elif name.startswith('c') or 'controller' in name.lower():
        return 'controller'
    elif name.startswith('ue'):
        return 'ue'
    elif name.startswith('enb'):
        return 'enb'
    elif name.startswith('epc'):
        return 'epc'
    return 'unknown'


class TelemetryStore:
    """Thread-safe rolling time-series store for telemetry data."""

    def __init__(self, maxlen: int = 300):
        self.maxlen = maxlen
        self._lock = threading.Lock()
        self._data: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=maxlen))
        )

    def append(self, node: str, metric: str, value: float, timestamp: float = None):
        if timestamp is None:
            timestamp = time.time()
        with self._lock:
            self._data[node][metric].append((timestamp, value))

    def get(self, node: str, metric: str) -> List[Tuple[float, float]]:
        with self._lock:
            if node in self._data and metric in self._data[node]:
                return list(self._data[node][metric])
            return []

    def get_latest(self, node: str, metric: str) -> Optional[Tuple[float, float]]:
        with self._lock:
            if node in self._data and metric in self._data[node]:
                d = self._data[node][metric]
                return d[-1] if d else None
            return None

    def nodes(self) -> List[str]:
        with self._lock:
            return list(self._data.keys())

    def metrics(self, node: str) -> List[str]:
        with self._lock:
            if node in self._data:
                return list(self._data[node].keys())
            return []

    def clear(self):
        with self._lock:
            self._data.clear()

    def export_csv(self, filepath: str):
        with self._lock:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'node', 'metric', 'value'])
                for node in sorted(self._data):
                    for metric in sorted(self._data[node]):
                        for ts, val in self._data[node][metric]:
                            writer.writerow([ts, node, metric, val])

    def export_json(self, filepath: str):
        with self._lock:
            out = {}
            for node in self._data:
                out[node] = {}
                for metric in self._data[node]:
                    out[node][metric] = [
                        {'timestamp': ts, 'value': val}
                        for ts, val in self._data[node][metric]
                    ]
            serialized = json.dumps(out, indent=2)
        with open(filepath, 'w') as f:
            f.write(serialized)


class ContainerCollector:
    """Collects per-container metrics via the Docker API."""

    def __init__(self, docker_client):
        self.client = docker_client
        self.logger = logging.getLogger(__name__)

    def collect(self, container_name: str) -> Dict[str, float]:
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)

            cpu_delta = (stats['cpu_stats']['cpu_usage']['total_usage']
                         - stats['precpu_stats']['cpu_usage']['total_usage'])
            system_delta = (stats['cpu_stats']['system_cpu_usage']
                            - stats['precpu_stats']['system_cpu_usage'])
            cpu_pct = (cpu_delta / system_delta * 100.0) if system_delta > 0 else 0.0

            mem_usage = stats['memory_stats'].get('usage', 0)
            mem_limit = stats['memory_stats'].get('limit', 1)
            mem_pct = (mem_usage / mem_limit) * 100.0
            mem_mb = mem_usage / (1024 * 1024)

            networks = stats.get('networks', {})
            rx_bytes = sum(n.get('rx_bytes', 0) for n in networks.values())
            tx_bytes = sum(n.get('tx_bytes', 0) for n in networks.values())
            rx_packets = sum(n.get('rx_packets', 0) for n in networks.values())
            tx_packets = sum(n.get('tx_packets', 0) for n in networks.values())
            rx_errors = sum(n.get('rx_errors', 0) for n in networks.values())
            tx_errors = sum(n.get('tx_errors', 0) for n in networks.values())
            rx_dropped = sum(n.get('rx_dropped', 0) for n in networks.values())
            tx_dropped = sum(n.get('tx_dropped', 0) for n in networks.values())

            return {
                'cpu_pct': cpu_pct, 'mem_pct': mem_pct, 'mem_mb': mem_mb,
                'rx_bytes': rx_bytes, 'tx_bytes': tx_bytes,
                'rx_packets': rx_packets, 'tx_packets': tx_packets,
                'rx_errors': rx_errors, 'tx_errors': tx_errors,
                'rx_dropped': rx_dropped, 'tx_dropped': tx_dropped,
            }
        except Exception as e:
            self.logger.debug(f"Container stats failed for {container_name}: {e}")
            return {}


class OVSCollector:
    """Collects OpenFlow / OVS statistics from switch containers."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def collect_port_stats(self, switch_name: str) -> Dict[str, Dict[str, int]]:
        try:
            result = _sp.run(
                ['docker', 'exec', switch_name, 'ovs-ofctl', 'dump-ports', switch_name],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return {}
            return self._parse_port_stats(result.stdout)
        except Exception as e:
            self.logger.debug(f"OVS port stats failed for {switch_name}: {e}")
            return {}

    def collect_flow_count(self, switch_name: str) -> int:
        try:
            result = _sp.run(
                ['docker', 'exec', switch_name, 'ovs-ofctl', 'dump-flows', switch_name],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return 0
            lines = [l for l in result.stdout.strip().split('\n')
                     if l and 'NXST_FLOW' not in l and 'OFPST_FLOW' not in l]
            return len(lines)
        except Exception as e:
            self.logger.debug(f"OVS flow count failed for {switch_name}: {e}")
            return 0

    def _parse_port_stats(self, output: str) -> Dict[str, Dict[str, int]]:
        ports = {}
        current_port = None
        for line in output.split('\n'):
            port_match = re.match(
                r'\s+port\s+(\S+):\s+rx\s+pkts=(\d+),\s+bytes=(\d+),\s+drop=(\d+),\s+errs=(\d+)', line)
            if port_match:
                current_port = port_match.group(1)
                ports[current_port] = {
                    'rx_packets': int(port_match.group(2)),
                    'rx_bytes': int(port_match.group(3)),
                    'rx_drops': int(port_match.group(4)),
                    'rx_errors': int(port_match.group(5)),
                }
                continue
            tx_match = re.match(
                r'\s+tx\s+pkts=(\d+),\s+bytes=(\d+),\s+drop=(\d+),\s+errs=(\d+)', line)
            if tx_match and current_port:
                ports[current_port].update({
                    'tx_packets': int(tx_match.group(1)),
                    'tx_bytes': int(tx_match.group(2)),
                    'tx_drops': int(tx_match.group(3)),
                    'tx_errors': int(tx_match.group(4)),
                })
        return ports


class LatencyCollector:
    """Measures RTT/latency between node pairs using ping."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def measure(self, src_container: str, dst_ip: str, count: int = 3) -> Dict[str, float]:
        try:
            result = _sp.run(
                ['docker', 'exec', src_container, 'ping', '-c', str(count), '-W', '2', dst_ip],
                capture_output=True, text=True, timeout=count * 3 + 5
            )
            return self._parse_ping(result.stdout)
        except _sp.TimeoutExpired:
            return {'rtt_avg': -1, 'packet_loss': 100.0}
        except Exception as e:
            self.logger.debug(f"Ping failed {src_container} -> {dst_ip}: {e}")
            return {}

    def _parse_ping(self, output: str) -> Dict[str, float]:
        stats = {}
        loss_match = re.search(r'(\d+(?:\.\d+)?)%\s+packet\s+loss', output)
        if loss_match:
            stats['packet_loss'] = float(loss_match.group(1))
        rtt_match = re.search(
            r'rtt\s+min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
        if rtt_match:
            stats['rtt_min'] = float(rtt_match.group(1))
            stats['rtt_avg'] = float(rtt_match.group(2))
            stats['rtt_max'] = float(rtt_match.group(3))
            stats['rtt_mdev'] = float(rtt_match.group(4))
        return stats


class TelemetryCollector:
    """Main telemetry collector that orchestrates all sub-collectors."""

    def __init__(self, store: TelemetryStore, docker_client=None, max_workers: int = 4):
        self.store = store
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

        self._docker_client = docker_client or get_docker_client()

        self._container_collector = ContainerCollector(self._docker_client) if self._docker_client else None
        self._ovs_collector = OVSCollector()
        self._latency_collector = LatencyCollector()

        self._pool = ThreadPoolExecutor(max_workers=max_workers)

        self._containers: Dict[str, str] = {}
        self._link_keys: Set[str] = set()
        self._links: List[Dict[str, str]] = []

        self._bg_thread: Optional[threading.Thread] = None
        self._bg_stop = threading.Event()
        self._bg_interval = 1.0

    def register_container(self, name: str, node_type: str = 'host'):
        self._containers[name] = node_type

    def register_link(self, src: str, dst: str, src_ip: str):
        key = f"{src}->{dst}"
        if key not in self._link_keys:
            self._link_keys.add(key)
            self._links.append({'src': src, 'dst': dst, 'src_ip': src_ip})

    def auto_discover(self):
        if not self._docker_client:
            return
        try:
            for container in self._docker_client.containers.list():
                name = container.name
                labels = container.labels
                node_type = labels.get('lft.type', guess_node_type(name))
                self._containers[name] = node_type
        except Exception as e:
            self.logger.warning(f"Auto-discover failed: {e}")

    def collect_all(self):
        ts = time.time()
        futures = {}

        if self._container_collector:
            for name in self._containers:
                futures[self._pool.submit(self._container_collector.collect, name)] = ('container', name)

        for name, ntype in self._containers.items():
            if ntype == 'switch':
                futures[self._pool.submit(self._ovs_collector.collect_port_stats, name)] = ('ovs_ports', name)
                futures[self._pool.submit(self._ovs_collector.collect_flow_count, name)] = ('ovs_flows', name)

        for link in self._links:
            futures[self._pool.submit(
                self._latency_collector.measure, link['src'], link['src_ip']
            )] = ('latency', f"{link['src']}->{link['dst']}")

        for future in as_completed(futures):
            kind, key = futures[future]
            try:
                result = future.result()
            except Exception as e:
                self.logger.debug(f"Collection failed for {kind}/{key}: {e}")
                continue

            if kind == 'container' and result:
                for metric, value in result.items():
                    self.store.append(key, metric, value, ts)
            elif kind == 'ovs_ports' and result:
                for port, stats in result.items():
                    for metric, value in stats.items():
                        self.store.append(key, f"port_{port}_{metric}", value, ts)
            elif kind == 'ovs_flows':
                self.store.append(key, 'flow_count', result, ts)
            elif kind == 'latency' and result:
                for metric, value in result.items():
                    self.store.append(key, metric, value, ts)

    def start_background(self, interval: float = 1.0):
        if self._bg_thread and self._bg_thread.is_alive():
            return
        self._bg_interval = interval
        self._bg_stop.clear()
        self._bg_thread = threading.Thread(target=self._bg_loop, daemon=True)
        self._bg_thread.start()

    def stop_background(self):
        self._bg_stop.set()
        if self._bg_thread:
            self._bg_thread.join(timeout=5)
            self._bg_thread = None
        self._pool.shutdown(wait=False)

    @property
    def is_running(self) -> bool:
        return self._bg_thread is not None and self._bg_thread.is_alive()

    def _bg_loop(self):
        while not self._bg_stop.is_set():
            t0 = time.monotonic()
            try:
                self.collect_all()
            except Exception as e:
                self.logger.debug(f"Background collection error: {e}")
            elapsed = time.monotonic() - t0
            remaining = max(0, self._bg_interval - elapsed)
            if remaining > 0:
                self._bg_stop.wait(timeout=remaining)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        out = {}
        for node in self.store.nodes():
            out[node] = {}
            for metric in self.store.metrics(node):
                latest = self.store.get_latest(node, metric)
                if latest:
                    out[node][metric] = latest[1]
        return out

    def print_summary(self):
        s = self.summary()
        if not s:
            print("No telemetry data collected.")
            return
        for node in sorted(s):
            print(f"\n--- {node} ({self._containers.get(node, '?')}) ---")
            for metric in sorted(s[node]):
                val = s[node][metric]
                if isinstance(val, float):
                    print(f"  {metric}: {val:.2f}")
                else:
                    print(f"  {metric}: {val}")


# ============================================================================
# SECTION 8: Network Visualizer
# ============================================================================

class NetworkVisualizer:
    """Real-time network topology and traffic visualizer."""

    _LAYOUT_PARAMS = dict(k=2, iterations=50, seed=42)

    NODE_TYPE_COLORS = {
        'host': '#4CAF50', 'switch': '#2196F3', 'controller': '#FF9800',
        'ue': '#9C27B0', 'enb': '#E91E63', 'epc': '#F44336', 'unknown': '#9E9E9E'
    }

    def __init__(self, update_interval=1000, telemetry_store=None):
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for visualization. "
                              "Install with: pip install matplotlib networkx")

        self.update_interval = update_interval
        self.graph = nx.Graph()

        self._docker_client = get_docker_client()

        self.store = telemetry_store or TelemetryStore()
        self.collector = TelemetryCollector(
            self.store, docker_client=self._docker_client
        )

        self.fig = None
        self.ax_topology = None
        self.ax_cpu = None
        self.ax_memory = None
        self.ax_network = None
        self.ax_latency = None
        self.animation_obj = None
        self._cached_layout = None

    def detect_network_topology(self):
        if not self._docker_client:
            return
        try:
            containers = self._docker_client.containers.list()
            self.graph.clear()
            for container in containers:
                name = container.name
                labels = container.labels
                node_type = labels.get('lft.type', guess_node_type(name))
                self.graph.add_node(name, type=node_type, container_id=container.id, status=container.status)
                self.collector.register_container(name, node_type)
            self._detect_connections()
            if len(self.graph.nodes()) > 0:
                self._cached_layout = nx.spring_layout(self.graph, **self._LAYOUT_PARAMS)
            else:
                self._cached_layout = None
        except Exception as e:
            print(f"Error detecting topology: {e}")

    def _detect_connections(self):
        nodes = list(self.graph.nodes())
        hosts = [n for n in nodes if self.graph.nodes[n]['type'] == 'host']
        switches = [n for n in nodes if self.graph.nodes[n]['type'] == 'switch']
        controllers = [n for n in nodes if self.graph.nodes[n]['type'] == 'controller']

        if switches:
            for host in hosts:
                self.graph.add_edge(host, switches[0], weight=1.0)
            for switch in switches:
                for controller in controllers:
                    self.graph.add_edge(switch, controller, weight=1.0)

        ues = [n for n in nodes if self.graph.nodes[n]['type'] == 'ue']
        enbs = [n for n in nodes if self.graph.nodes[n]['type'] == 'enb']
        epcs = [n for n in nodes if self.graph.nodes[n]['type'] == 'epc']

        for ue in ues:
            if enbs:
                self.graph.add_edge(ue, enbs[0], weight=1.0)
        for enb in enbs:
            if epcs:
                self.graph.add_edge(enb, epcs[0], weight=1.0)

    def _build_legend(self, ax):
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label=nt.capitalize(),
                       markerfacecolor=c, markersize=10)
            for nt, c in self.NODE_TYPE_COLORS.items() if nt != 'unknown'
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    def _node_color(self, node):
        ntype = self.graph.nodes.get(node, {}).get('type', 'unknown')
        return self.NODE_TYPE_COLORS.get(ntype, '#9E9E9E')

    def setup_figure(self):
        self.fig = plt.figure(figsize=(18, 12))
        self.fig.suptitle('LFT Network Real-Time Monitoring', fontsize=16, fontweight='bold')
        gs = self.fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.35, wspace=0.3)
        self.ax_topology = self.fig.add_subplot(gs[0, :])
        self.ax_cpu = self.fig.add_subplot(gs[1, 0])
        self.ax_memory = self.fig.add_subplot(gs[1, 1])
        self.ax_network = self.fig.add_subplot(gs[2, 0])
        self.ax_latency = self.fig.add_subplot(gs[2, 1])

    def update_plot(self, frame):
        if frame > 0 and frame % 10 == 0:
            self.detect_network_topology()
        self.ax_topology.clear()
        self.draw_topology()
        self._draw_cpu()
        self._draw_memory()
        self._draw_network()
        self._draw_latency()
        return self.ax_topology, self.ax_cpu, self.ax_memory, self.ax_network, self.ax_latency

    def draw_topology(self):
        if len(self.graph.nodes()) == 0:
            self.ax_topology.text(0.5, 0.5, 'No network detected\nRun a topology first!',
                                 ha='center', va='center', fontsize=14, color='red')
            self.ax_topology.set_xlim([0, 1])
            self.ax_topology.set_ylim([0, 1])
            return

        pos = self._cached_layout
        if pos is None:
            pos = nx.spring_layout(self.graph, **self._LAYOUT_PARAMS)

        nx.draw_networkx_edges(self.graph, pos, edge_color='#CCCCCC', width=2.0, alpha=0.6, ax=self.ax_topology)
        node_colors = [self._node_color(n) for n in self.graph.nodes()]
        node_sizes = [2000 if self.graph.nodes[n].get('type') == 'switch' else 1500 for n in self.graph.nodes()]
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, ax=self.ax_topology)
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold', ax=self.ax_topology)

        for node, (x, y) in pos.items():
            status = self.graph.nodes[node].get('status', 'unknown')
            status_color = '#4CAF50' if status == 'running' else '#F44336'
            self.ax_topology.plot(x, y + 0.08, 'o', color=status_color, markersize=8,
                                 markeredgecolor='white', markeredgewidth=2, zorder=10)

        self.ax_topology.set_title('Network Topology', fontsize=14, fontweight='bold')
        self.ax_topology.axis('off')
        self._build_legend(self.ax_topology)

    def _draw_timeseries(self, ax, metric, title, ylabel, ylim=None, filter_fn=None):
        ax.clear()
        ax.set_title(title, fontsize=12)
        ax.set_xlabel('Samples')
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(ylim)
        ax.grid(True, alpha=0.3)

        has_data = False
        for node in self.store.nodes():
            series = self.store.get(node, metric)
            if series:
                values = [v for _, v in series]
                if filter_fn:
                    values = [v for v in values if filter_fn(v)]
                if values:
                    ax.plot(values, label=node, color=self._node_color(node), linewidth=2)
                    has_data = True
        if has_data:
            ax.legend(loc='upper right', fontsize=8)

    def _draw_cpu(self):
        self._draw_timeseries(self.ax_cpu, 'cpu_pct', 'CPU Usage (%)', 'CPU %', ylim=[0, 100])

    def _draw_memory(self):
        self._draw_timeseries(self.ax_memory, 'mem_mb', 'Memory Usage (MB)', 'MB')

    def _draw_network(self):
        ax = self.ax_network
        ax.clear()
        ax.set_title('Network Throughput (KB/s)', fontsize=12)
        ax.set_xlabel('Samples')
        ax.set_ylabel('KB/s')
        ax.grid(True, alpha=0.3)

        has_data = False
        for node in self.store.nodes():
            rx = self.store.get(node, 'rx_bytes')
            tx = self.store.get(node, 'tx_bytes')
            if len(rx) > 1 and len(tx) > 1:
                throughput = []
                for i in range(1, min(len(rx), len(tx))):
                    dt = rx[i][0] - rx[i - 1][0]
                    if dt > 0:
                        db = (rx[i][1] + tx[i][1]) - (rx[i - 1][1] + tx[i - 1][1])
                        throughput.append(db / dt / 1024)
                    else:
                        throughput.append(0)
                if throughput:
                    ax.plot(throughput, label=node, color=self._node_color(node), linewidth=2)
                    has_data = True
        if has_data:
            ax.legend(loc='upper right', fontsize=8)

    def _draw_latency(self):
        self._draw_timeseries(self.ax_latency, 'rtt_avg', 'Latency (ms)', 'RTT ms', filter_fn=lambda v: v >= 0)

    def start(self):
        try:
            matplotlib.use('TkAgg')
        except Exception:
            pass

        print("Starting LFT Network Visualizer...")
        print("Detecting network topology...")
        self.detect_network_topology()

        if len(self.graph.nodes()) == 0:
            print("Warning: No network detected. Make sure containers are running.")
        else:
            print(f"Detected {len(self.graph.nodes())} nodes and {len(self.graph.edges())} connections")

        self.collector.start_background(interval=self.update_interval / 1000.0)
        self.setup_figure()

        self.animation_obj = animation.FuncAnimation(
            self.fig, self.update_plot, interval=self.update_interval,
            blit=False, cache_frame_data=False
        )

        print("Visualization started! Close the window to stop.")
        try:
            plt.show()
        except KeyboardInterrupt:
            print("\nStopping visualization...")
        finally:
            self.stop()

    def stop(self):
        self.collector.stop_background()
        if self.animation_obj and hasattr(self.animation_obj, 'event_source') and self.animation_obj.event_source:
            self.animation_obj.event_source.stop()
        plt.close('all')
        print("Visualization stopped.")


# ============================================================================
# SECTION 9: AI Topology Generator
# ============================================================================

class ModernAITopologyGenerator:
    """AI topology generator using robust open-source models."""

    _GEN_PARAMS = {
        'max_new_tokens': 2048,
        'temperature': 0.7,
        'top_p': 0.9,
        'do_sample': True,
        'repetition_penalty': 1.1,
    }

    SUPPORTED_MODELS = {
        "deepseek-r1": "deepseek-ai/DeepSeek-R1-0528",
        "deepseek-r1-8b": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        "phi3-mini": "microsoft/Phi-3-mini-4k-instruct",
        "qwen2-7b": "Qwen/Qwen2-7B-Instruct",
        "gemma2-9b": "google/gemma2-9b-it",
        "stable-code-3b": "stabilityai/stable-code-3b",
        "code-llama-7b": "codellama/CodeLlama-7b-Instruct-hf",
        "deepseek-coder-7b": "deepseek-ai/deepseek-coder-7b-instruct",
        "stable-code-3b-instruct": "stabilityai/stable-code-3b",
        "phi3": "microsoft/Phi-3-mini-4k-instruct"
    }

    def __init__(self, model_name: str = "deepseek-r1", use_hf_api: bool = False,
                 api_token: Optional[str] = None, device: str = "auto",
                 load_in_8bit: bool = True, load_in_4bit: bool = False):
        if not HAS_AI and not use_hf_api:
            raise LFTException(
                "torch/transformers/accelerate are required for local AI inference. "
                "Install with: pip install torch transformers accelerate\n"
                "Or use --local=False for Hugging Face API."
            )

        self.model_name = model_name
        self.use_hf_api = use_hf_api
        self.api_token = api_token or os.getenv('HF_TOKEN') or os.getenv('HUGGING_FACE_HUB_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
        self.device = device
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit

        self.logger = logging.getLogger(__name__)

        if use_hf_api and not self.api_token:
            raise LFTException(
                "Hugging Face API token required when use_hf_api=True. "
                "Set HF_TOKEN environment variable or pass api_token parameter."
            )

        self.model = None
        self.tokenizer = None
        self.generation_config = None

        if not use_hf_api:
            self._setup_local_model()

    def _setup_local_model(self):
        try:
            if self.model_name in self.SUPPORTED_MODELS:
                model_path = self.SUPPORTED_MODELS[self.model_name]
            else:
                model_path = self.model_name

            self.logger.info(f"Loading model: {model_path}")

            quantization_config = None
            if self.load_in_4bit:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif self.load_in_8bit:
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)

            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, use_fast=True)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=quantization_config,
                dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.device,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )

            self.generation_config = GenerationConfig(
                **self._GEN_PARAMS,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

            self.logger.info(f"Model loaded successfully: {model_path}")

        except Exception as e:
            raise LFTException(f"Failed to setup local model: {str(e)}")

    def _get_system_prompt(self) -> str:
        return """You are an expert network engineer specializing in the Lightweight Fog Testbed (LFT) framework.

Generate Python code to create network topologies using LFT components.

Available LFT Components:
- Host: Network hosts with IP configuration
- Switch: OpenFlow switches for SDN
- Controller: SDN controllers (OpenDaylight, ONOS)
- UE: User Equipment for wireless networks
- EPC: Evolved Packet Core for 4G networks
- EnB: eNodeB for 4G base stations

Key LFT Methods:
- instantiate(): Create and start the node
- connect(node, interface1, interface2): Connect two nodes
- setIp(ip, prefix, interface): Configure IP address
- setDefaultGateway(gateway, interface): Set default gateway

IMPORTANT: Generate ONLY executable Python code. Start with 'from profissa_lft import *' and create a complete, runnable topology. No explanations, no markdown, just Python code."""

    def _format_prompt(self, user_prompt: str) -> str:
        system_prompt = self._get_system_prompt()
        return f"{system_prompt}\n\nUser request: {user_prompt}\n\nPython code:\n"

    def _call_local_model(self, prompt: str) -> str:
        try:
            formatted_prompt = self._format_prompt(prompt)
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt", truncation=True, max_length=4096)

            if self.device == "auto" and torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            try:
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs, **self._GEN_PARAMS,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
            except Exception as gen_error:
                self.logger.warning(f"Standard generation failed: {gen_error}, trying fallback...")
                with torch.no_grad():
                    outputs = self.model.generate(**inputs, max_new_tokens=1024, do_sample=False, num_beams=1)

            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            response_start = generated_text.find("Python code:")
            if response_start != -1:
                generated_text = generated_text[response_start + len("Python code:"):]

            return generated_text.strip()

        except Exception as e:
            raise LFTException(f"Local model inference failed: {str(e)}")

    def _call_hf_api(self, prompt: str) -> str:
        try:
            import requests

            formatted_prompt = self._format_prompt(prompt)
            model_path = self.SUPPORTED_MODELS.get(self.model_name, self.model_name)
            api_url = f"https://api-inference.huggingface.co/models/{model_path}"

            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": formatted_prompt,
                "parameters": dict(self._GEN_PARAMS),
            }

            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            else:
                return result.get("generated_text", "")

        except Exception as e:
            raise LFTException(f"Hugging Face API call failed: {str(e)}")

    # LFT node constructors — shared between validation and truncation
    _LFT_CONSTRUCTORS = ('Host(', 'Switch(', 'Controller(', 'UE(', 'EPC(', 'EnB(')

    # Patterns that signal the model has started hallucinating beyond the topology
    _HALLUCINATION_MARKERS = re.compile(
        r'^(?:'
        r'#!/'                        # shebang line
        r'|"""'                       # docstring start (new file / module)
        r"|'''"                       # alternate docstring
        r'|\S+/\S+\.\w+'             # file path like test/scripts/foo.py
        r'|class\s+\w+.*:'           # new class definition (not LFT)
        r'|if\s+__name__\s*=='       # if __name__ == "__main__"
        r')'
    )

    # Lines that look like natural language prose, not Python code
    _PROSE_LINE = re.compile(
        r'^(?:Let me|I need|I\'ll|We\'ll|We will|Note:|Please|Sure|Here|'
        r'The user|However|But wait|Looking at|In the|After |'
        r'This |That |Also|Now |Ok |Okay )'
    )

    _LFT_IMPORTS = re.compile(
        r'^(?:from\s+profissa_lft|import\s+profissa_lft)'
    )

    def validate_generated_code(self, code: str) -> bool:
        if not code or len(code.strip()) < 50:
            return False
        lft_indicators = ('from profissa_lft', 'lft.') + self._LFT_CONSTRUCTORS
        return any(indicator in code for indicator in lft_indicators)

    def _clean_generated_code(self, code: str) -> str:
        """Clean and format the generated code, truncating hallucinated content."""
        code = code.replace("```python", "").replace("```", "").strip()
        code = self._truncate_hallucinations(code)
        if "from profissa_lft" not in code:
            code = "from profissa_lft import *\n\n" + code
        return code

    # Max consecutive comment/blank lines before we consider it reasoning drift
    _MAX_COMMENT_RUN = 5

    def _truncate_hallucinations(self, code: str) -> str:
        """Detect where the model drifts away from LFT topology code and cut."""
        lines = code.split('\n')
        seen_lft = False
        seen_code = False
        cut_index = len(lines)
        comment_run = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not seen_lft:
                if self._LFT_IMPORTS.match(stripped) or any(
                    ind in stripped for ind in self._LFT_CONSTRUCTORS
                ):
                    seen_lft = True
                continue

            if not stripped or stripped.startswith('#'):
                if seen_code:
                    comment_run += 1
                    if comment_run > self._MAX_COMMENT_RUN:
                        cut_index = i - comment_run + 1
                        break
                continue
            else:
                comment_run = 0
                seen_code = True

            if stripped.startswith(('import ', 'from ')) and not self._LFT_IMPORTS.match(stripped):
                cut_index = i
                break

            if self._HALLUCINATION_MARKERS.match(stripped):
                cut_index = i
                break

            if self._PROSE_LINE.match(stripped):
                cut_index = i
                break

        if not seen_lft:
            return ''

        return '\n'.join(lines[:cut_index]).rstrip()

    def generate_topology(self, prompt: str, output_file: Optional[str] = None) -> str:
        try:
            self.logger.info(f"Generating topology for prompt: {prompt}")

            if self.use_hf_api:
                generated_code = self._call_hf_api(prompt)
            else:
                generated_code = self._call_local_model(prompt)

            if not self.validate_generated_code(generated_code):
                raise LFTException("Generated code does not contain valid LFT components")

            cleaned_code = self._clean_generated_code(generated_code)

            if output_file:
                with open(output_file, 'w') as f:
                    f.write(cleaned_code)
                self.logger.info(f"Topology saved to: {output_file}")

            return cleaned_code

        except Exception as e:
            raise LFTException(f"Failed to generate topology: {str(e)}")

    def list_available_models(self) -> List[str]:
        return list(self.SUPPORTED_MODELS.keys())

    def get_model_info(self) -> Dict[str, Any]:
        if not self.model:
            return {"status": "No model loaded"}
        return {
            "model_name": self.model_name,
            "model_type": type(self.model).__name__,
            "device": str(next(self.model.parameters()).device),
            "dtype": str(next(self.model.parameters()).dtype),
            "parameters": sum(p.numel() for p in self.model.parameters())
        }


# Backward compatibility
AITopologyGenerator = ModernAITopologyGenerator

# ============================================================================
# SECTION 10: CLI
# ============================================================================

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def handle_generate(args, logger):
    try:
        generator = AITopologyGenerator(
            model_name=args.model,
            use_hf_api=not args.local,
            api_token=args.token
        )

        logger.info("Generating topology...")
        generated_code = generator.generate_topology(args.description, output_file=args.output)

        if args.validate:
            if generator.validate_generated_code(generated_code):
                logger.info("Generated code validation: PASSED")
            else:
                logger.warning("Generated code validation: FAILED")

        if args.output:
            print(f"Topology generated and saved to: {args.output}")
        else:
            print("\n" + "=" * 50)
            print("GENERATED TOPOLOGY CODE")
            print("=" * 50)
            print(generated_code)
            print("=" * 50)

        return 0

    except LFTException as e:
        logger.error(f"LFT Error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


def handle_interactive(args, logger):
    try:
        generator = AITopologyGenerator(
            model_name=args.model,
            use_hf_api=not args.local,
            api_token=args.token
        )

        print("LFT AI Topology Generator - Interactive Mode")
        print("=" * 50)
        print("Type 'quit' to exit, 'help' for examples, 'clear' to clear screen")
        print()

        while True:
            try:
                description = input("Describe your topology: ").strip()

                if description.lower() == 'quit':
                    print("Goodbye!")
                    break
                elif description.lower() == 'help':
                    handle_examples()
                    continue
                elif description.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif not description:
                    continue

                logger.info("Generating topology...")
                generated_code = generator.generate_topology(description)

                if generator.validate_generated_code(generated_code):
                    logger.info("Generated code validation: PASSED")
                else:
                    logger.warning("Generated code validation: FAILED")

                print("\n" + "=" * 50)
                print("GENERATED TOPOLOGY CODE")
                print("=" * 50)
                print(generated_code)
                print("=" * 50)

                save = input("\nSave to file? (y/n): ").strip().lower()
                if save in ['y', 'yes']:
                    filename = input("Enter filename (default: generated_topology.py): ").strip()
                    if not filename:
                        filename = "generated_topology.py"
                    with open(filename, 'w') as f:
                        f.write(generated_code)
                    print(f"Topology saved to: {filename}")

                print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                print()

        return 0

    except LFTException as e:
        logger.error(f"LFT Error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


def handle_visualize(args):
    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required. Install with: pip install matplotlib networkx")
        return 1

    # Static visualization from a topology file
    if args.file:
        return _visualize_topology_file(args.file)

    # Live visualization from Docker containers
    if not HAS_DOCKER:
        print("Warning: docker-py not found. Container monitoring will be limited.")

    store = TelemetryStore()
    visualizer = NetworkVisualizer(update_interval=args.interval, telemetry_store=store)

    try:
        visualizer.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        visualizer.stop()
    finally:
        if args.export_csv:
            store.export_csv(args.export_csv)
            print(f"Telemetry exported to {args.export_csv}")
        if args.export_json:
            store.export_json(args.export_json)
            print(f"Telemetry exported to {args.export_json}")

    return 0


def _visualize_topology_file(filepath: str):
    """Parse a generated topology .py file and render a static graph."""
    try:
        with open(filepath) as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}")
        return 1

    import matplotlib.pyplot as plt
    import networkx as nx

    G = nx.Graph()

    # Node patterns: var = Type("name", ...) or var = Type(name=expr, ...)
    node_pattern = re.compile(
        r'(\w+)\s*=\s*(Host|Switch|Controller|UE|EPC|EnB)\s*\('
    )
    # Extract string literal from first positional or name= keyword arg
    name_literal = re.compile(r'["\']([^"\']+)["\']')
    # Connect patterns: connect(var1, ..., var2, ...) — grab first and last variable names
    connect_pattern = re.compile(
        r'connect\s*\(([^)]+)\)'
    )

    var_to_name = {}
    var_to_type = {}

    for match in node_pattern.finditer(code):
        var, node_type = match.group(1), match.group(2)
        # Try to find the name from the constructor args
        rest = code[match.end():]
        paren_end = rest.find(')')
        arg_str = rest[:paren_end] if paren_end != -1 else rest[:50]
        name_match = name_literal.search(arg_str)
        name = name_match.group(1) if name_match else var
        var_to_name[var] = name
        var_to_type[var] = node_type.lower()
        G.add_node(name, type=node_type.lower())

    for match in connect_pattern.finditer(code):
        args_str = match.group(1)
        # Extract variable names (skip string literals and method calls)
        tokens = [t.strip().split('.')[0] for t in args_str.split(',')]
        var_refs = [t for t in tokens if t.isidentifier() and t in var_to_name]
        # Connect first node to second node found
        if len(var_refs) >= 2:
            G.add_edge(var_to_name[var_refs[0]], var_to_name[var_refs[1]])

    if not G.nodes:
        print("No LFT nodes found in the topology file.")
        return 1

    # Colors matching NetworkVisualizer
    type_colors = {
        'host': '#4CAF50', 'switch': '#2196F3', 'controller': '#FF9800',
        'ue': '#9C27B0', 'enb': '#E91E63', 'epc': '#F44336', 'unknown': '#9E9E9E'
    }

    node_colors = [type_colors.get(G.nodes[n].get('type', 'unknown'), '#9E9E9E') for n in G.nodes]
    node_sizes = [2000 if G.nodes[n].get('type') == 'switch' else 1500 for n in G.nodes]

    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    nx.draw_networkx_edges(G, pos, edge_color='#CCCCCC', width=2.0, alpha=0.6, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)

    # Legend
    seen_types = set(G.nodes[n].get('type', 'unknown') for n in G.nodes)
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label=t.capitalize(),
                   markerfacecolor=type_colors.get(t, '#9E9E9E'), markersize=12)
        for t in sorted(seen_types)
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=11)

    ax.set_title(f'LFT Topology: {os.path.basename(filepath)}', fontsize=14, fontweight='bold')
    ax.axis('off')

    print(f"Topology: {len(G.nodes)} nodes, {len(G.edges)} connections")
    for n in G.nodes:
        print(f"  {n} ({G.nodes[n].get('type', '?')})")

    plt.tight_layout()
    plt.show()
    return 0


def handle_examples():
    examples = [
        {"title": "Simple SDN Topology",
         "description": "Create a simple SDN topology with 2 hosts connected to a switch"},
        {"title": "4G Wireless Network",
         "description": "Create a 4G wireless network with 2 UEs connected to an eNodeB and EPC"},
        {"title": "Multi-Switch SDN",
         "description": "Create an SDN topology with 3 switches, 1 controller, and 4 hosts"},
        {"title": "Fog Computing Network",
         "description": "Create a fog computing network with edge nodes, fog nodes, and cloud connection"},
        {"title": "Enterprise Network",
         "description": "Create an enterprise network with multiple VLANs, switches, and a gateway"},
        {"title": "IoT Network",
         "description": "Create an IoT network with sensors, gateways, and cloud connectivity"},
    ]

    print("Example Topology Descriptions")
    print("=" * 50)
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
        print(f"   {example['description']}")
        print()

    print("Usage:")
    print("  python lft_ai_standalone.py generate \"<description>\" -o output.py")
    print("  python lft_ai_standalone.py interactive")
    print("  python lft_ai_standalone.py visualize")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="LFT AI - Lightweight Fog Testbed (Standalone)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  generate     Generate topology from natural language description
  interactive  Interactive topology generation
  visualize    Real-time network visualization
  examples     Show example topology descriptions
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate topology from description')
    gen_parser.add_argument('description', help='Natural language description of the desired topology')
    gen_parser.add_argument('-o', '--output', help='Output file path')
    gen_parser.add_argument('--local', action='store_true', help='Use local model instead of Hugging Face API')
    gen_parser.add_argument('--model', default='deepseek-ai/DeepSeek-R1-0528', help='Model name')
    gen_parser.add_argument('--token', help='Hugging Face API token (or set HF_TOKEN env var)')
    gen_parser.add_argument('--validate', action='store_true', help='Validate generated code')
    gen_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # Interactive command
    int_parser = subparsers.add_parser('interactive', help='Interactive topology generation')
    int_parser.add_argument('--local', action='store_true', help='Use local model')
    int_parser.add_argument('--model', default='deepseek-ai/DeepSeek-R1-0528', help='Model name')
    int_parser.add_argument('--token', help='Hugging Face API token')
    int_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Real-time network visualization')
    viz_parser.add_argument('--file', '-f', type=str, default=None,
                           help='Visualize a generated topology .py file (static graph)')
    viz_parser.add_argument('--interval', type=int, default=1000, help='Update interval in ms (default: 1000)')
    viz_parser.add_argument('--export-csv', type=str, default=None, help='Export telemetry to CSV on exit')
    viz_parser.add_argument('--export-json', type=str, default=None, help='Export telemetry to JSON on exit')

    # Examples command
    subparsers.add_parser('examples', help='Show example topology descriptions')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if hasattr(args, 'verbose') and args.verbose:
        setup_logging(True)
    else:
        setup_logging(False)

    logger = logging.getLogger(__name__)

    try:
        if args.command == 'generate':
            return handle_generate(args, logger)
        elif args.command == 'interactive':
            return handle_interactive(args, logger)
        elif args.command == 'visualize':
            return handle_visualize(args)
        elif args.command == 'examples':
            return handle_examples()
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


# ============================================================================
# SECTION 11: Public API (for import usage)
# ============================================================================

__all__ = [
    'Node', 'Host', 'Controller', 'Switch', 'UE', 'EPC', 'EnB',
    'Perfsonar', 'CICFlowMeter',
    'AITopologyGenerator', 'ModernAITopologyGenerator',
    'TelemetryStore', 'TelemetryCollector', 'NetworkVisualizer',
    'LFTException', 'NodeInstantiationFailed',
]

if __name__ == "__main__":
    sys.exit(main())
