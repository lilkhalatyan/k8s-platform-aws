#!/usr/bin/env python3
"""Generate a cluster status report using kubectl."""

import json
import subprocess
import sys


def run_kubectl(args):
    """Run a kubectl command and return the output."""
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip(), result.returncode == 0
    except FileNotFoundError:
        print("Error: kubectl not found. Please install kubectl.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        return "Command timed out", False


def get_nodes():
    """Get node information."""
    output, ok = run_kubectl(["get", "nodes", "-o", "json"])
    if not ok:
        return []
    data = json.loads(output)
    nodes = []
    for node in data.get("items", []):
        name = node["metadata"]["name"]
        status = "Ready"
        for condition in node["status"]["conditions"]:
            if condition["type"] == "Ready":
                status = "Ready" if condition["status"] == "True" else "NotReady"
        capacity = node["status"]["capacity"]
        nodes.append({
            "name": name,
            "status": status,
            "cpu": capacity.get("cpu", "N/A"),
            "memory": capacity.get("memory", "N/A"),
        })
    return nodes


def get_pods(namespace=None):
    """Get pod information."""
    cmd = ["get", "pods", "-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])
    else:
        cmd.append("--all-namespaces")
    output, ok = run_kubectl(cmd)
    if not ok:
        return []
    data = json.loads(output)
    pods = []
    for pod in data.get("items", []):
        ns = pod["metadata"].get("namespace", "default")
        name = pod["metadata"]["name"]
        phase = pod["status"].get("phase", "Unknown")
        restarts = 0
        for cs in pod["status"].get("containerStatuses", []):
            restarts += cs.get("restartCount", 0)
        pods.append({
            "namespace": ns,
            "name": name,
            "status": phase,
            "restarts": restarts,
        })
    return pods


def get_resource_usage():
    """Get resource usage via kubectl top."""
    output, ok = run_kubectl(["top", "nodes", "--no-headers"])
    if not ok:
        return None
    return output


def main():
    print("=" * 70)
    print("  K8s Platform - Cluster Status Report")
    print("=" * 70)

    # Nodes
    print("\n  NODES")
    print("  " + "-" * 66)
    nodes = get_nodes()
    if nodes:
        print(f"  {'NAME':40s} {'STATUS':10s} {'CPU':6s} {'MEMORY':10s}")
        for node in nodes:
            print(f"  {node['name']:40s} {node['status']:10s} {node['cpu']:6s} {node['memory']:10s}")
    else:
        print("  Unable to retrieve node information")

    # Resource usage
    print("\n  RESOURCE USAGE")
    print("  " + "-" * 66)
    usage = get_resource_usage()
    if usage:
        print(f"  {usage}")
    else:
        print("  Metrics server not available (install metrics-server for resource usage)")

    # Pods by namespace
    for ns in ["microservices", "monitoring", "argocd", "kube-system"]:
        print(f"\n  PODS - {ns}")
        print("  " + "-" * 66)
        pods = get_pods(ns)
        if pods:
            print(f"  {'NAME':45s} {'STATUS':12s} {'RESTARTS':10s}")
            for pod in pods:
                print(f"  {pod['name']:45s} {pod['status']:12s} {pod['restarts']:<10d}")
        else:
            print(f"  No pods found in {ns}")

    # Summary
    all_pods = get_pods()
    running = sum(1 for p in all_pods if p["status"] == "Running")
    total = len(all_pods)
    print(f"\n  SUMMARY")
    print("  " + "-" * 66)
    print(f"  Nodes:        {len(nodes)}")
    print(f"  Pods Running: {running}/{total}")
    print("=" * 70)


if __name__ == "__main__":
    main()
