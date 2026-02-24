#!/usr/bin/env python3
"""Health checker for all microservices. Exits non-zero if any service is unhealthy."""

import json
import subprocess
import sys
from urllib.error import URLError
from urllib.request import urlopen

SERVICES = {
    "api-gateway": {"namespace": "microservices", "port": 8000},
    "order-service": {"namespace": "microservices", "port": 8001},
    "notification-service": {"namespace": "microservices", "port": 8002},
}


def get_service_url(name, config):
    """Get the cluster-internal URL for a service via kubectl port-forward or direct URL."""
    return f"http://localhost:{config['port']}/health"


def check_health_via_kubectl(name, config):
    """Check service health using kubectl exec."""
    namespace = config["namespace"]
    port = config["port"]
    try:
        result = subprocess.run(
            [
                "kubectl", "exec", "-n", namespace,
                f"deploy/{name}", "--",
                "python", "-c",
                f"import urllib.request; print(urllib.request.urlopen('http://localhost:{port}/health').read().decode())"
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return data.get("status") == "healthy", data
        return False, {"error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return False, {"error": "timeout"}
    except Exception as e:
        return False, {"error": str(e)}


def check_health_direct(url):
    """Check service health via direct HTTP call (when port-forwarded)."""
    try:
        response = urlopen(url, timeout=5)
        data = json.loads(response.read().decode())
        return data.get("status") == "healthy", data
    except (URLError, json.JSONDecodeError) as e:
        return False, {"error": str(e)}


def main():
    print("=" * 60)
    print("  K8s Platform - Service Health Check")
    print("=" * 60)

    all_healthy = True
    use_kubectl = "--kubectl" in sys.argv

    for name, config in SERVICES.items():
        if use_kubectl:
            healthy, details = check_health_via_kubectl(name, config)
        else:
            url = get_service_url(name, config)
            healthy, details = check_health_direct(url)

        status = "HEALTHY" if healthy else "UNHEALTHY"
        icon = "[OK]" if healthy else "[FAIL]"
        print(f"  {icon} {name:30s} {status}")

        if not healthy:
            print(f"       Details: {details}")
            all_healthy = False

    print("=" * 60)

    if all_healthy:
        print("  All services are healthy!")
        sys.exit(0)
    else:
        print("  Some services are unhealthy!")
        sys.exit(1)


if __name__ == "__main__":
    main()
