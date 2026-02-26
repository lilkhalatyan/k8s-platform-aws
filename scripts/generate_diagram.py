#!/usr/bin/env python3
"""Generate a polished architecture diagram for k8s-platform-aws."""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# Canvas
W, H = 1600, 1050

# Color palette (dark theme)
BG       = "#0d1117"
SURFACE  = "#161b22"
BORDER   = "#30363d"
TEXT_W   = "#e6edf3"
TEXT_DIM = "#8b949e"

# Accent colors
AWS_ORG  = "#FF9900"
K8S_BLUE = "#326CE5"
ARGO_RED = "#EF7B4D"
PROM_RED = "#E6522C"
GRAF_ORG = "#F46800"
LOKI_YEL = "#F2CC0C"
GH_WHITE = "#ffffff"
PY_BLUE  = "#3776AB"
GREEN    = "#3fb950"
TEAL     = "#56d4dd"
PURPLE   = "#bc8cff"
PINK     = "#f778ba"


def font(size):
    """Load Arial or fallback font."""
    for name in ["arial.ttf", "arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def font_bold(size):
    for name in ["arialbd.ttf", "C:/Windows/Fonts/arialbd.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def rrect(draw, xy, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def hex_to_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def draw_arrow(draw, pts, color=TEXT_DIM, width=2, arrow_size=9, dashed=False):
    """Draw an arrow along a list of (x, y) points."""
    # Draw line segments
    for i in range(len(pts) - 1):
        if dashed:
            _draw_dashed_line(draw, pts[i], pts[i + 1], color, width)
        else:
            draw.line([pts[i], pts[i + 1]], fill=color, width=width)
    # Arrowhead at last segment
    x1, y1 = pts[-2]
    x2, y2 = pts[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    ax1 = x2 - arrow_size * math.cos(angle - math.pi / 6)
    ay1 = y2 - arrow_size * math.sin(angle - math.pi / 6)
    ax2 = x2 - arrow_size * math.cos(angle + math.pi / 6)
    ay2 = y2 - arrow_size * math.sin(angle + math.pi / 6)
    draw.polygon([(x2, y2), (int(ax1), int(ay1)), (int(ax2), int(ay2))], fill=color)


def _draw_dashed_line(draw, p1, p2, color, width, dash=10, gap=6):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    dx, dy = (x2 - x1) / dist, (y2 - y1) / dist
    pos = 0
    while pos < dist:
        end = min(pos + dash, dist)
        draw.line(
            [(x1 + dx * pos, y1 + dy * pos), (x1 + dx * end, y1 + dy * end)],
            fill=color, width=width,
        )
        pos = end + gap


def arrow_label(draw, x, y, text, color=TEXT_DIM):
    draw.text((x, y), text, fill=color, font=font(10))


def node(draw, x, y, w, h, title, subtitle, color, icon_text=None):
    """Draw a component node box."""
    rrect(draw, (x, y, x + w, y + h), r=6, fill=SURFACE, outline=color, width=2)
    # Color accent bar on top
    rrect(draw, (x + 1, y + 1, x + w - 1, y + 5), r=3, fill=color)
    ty = y + 12
    if icon_text:
        draw.text((x + 10, ty), icon_text, fill=color, font=font_bold(13))
        draw.text((x + 28, ty), title, fill=TEXT_W, font=font_bold(13))
    else:
        draw.text((x + 10, ty), title, fill=TEXT_W, font=font_bold(13))
    if subtitle:
        draw.text((x + 10, ty + 18), subtitle, fill=TEXT_DIM, font=font(10))


def section_box(draw, x, y, w, h, label, color, dashed=False):
    """Draw a labeled section outline."""
    rrect(draw, (x, y, x + w, y + h), r=10, fill=None, outline=color, width=2 if not dashed else 1)
    # Label background
    tw = len(label) * 8 + 16
    rrect(draw, (x + 12, y - 10, x + 12 + tw, y + 12), r=4, fill=BG)
    draw.text((x + 20, y - 8), label, fill=color, font=font_bold(12))


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════
    # TITLE
    # ═══════════════════════════════════════════════
    draw.text((W // 2 - 250, 16), "K8s Platform AWS", fill=TEXT_W, font=font_bold(28))
    draw.text((W // 2 + 30, 24), "Architecture Overview", fill=TEXT_DIM, font=font(18))
    draw.line([(50, 55), (W - 50, 55)], fill=BORDER, width=1)

    # ═══════════════════════════════════════════════
    # USER / CLIENT
    # ═══════════════════════════════════════════════
    node(draw, 60, 75, 130, 50, "User / Client", "HTTPS", TEXT_DIM)

    # ═══════════════════════════════════════════════
    # GITHUB SECTION
    # ═══════════════════════════════════════════════
    section_box(draw, 260, 65, 520, 70, "GitHub", GH_WHITE)
    node(draw, 275, 80, 140, 42, "Repository", "main branch", PURPLE)
    node(draw, 430, 80, 110, 42, "CI Pipeline", "test + lint", GREEN)
    node(draw, 555, 80, 110, 42, "Build & Push", "Docker > ECR", AWS_ORG)
    node(draw, 680, 80, 85, 42, "TF CI/CD", "plan/apply", PURPLE)

    # Arrows repo -> CI, Build, TF
    draw_arrow(draw, [(415, 101), (430, 101)], GREEN, width=1)
    draw_arrow(draw, [(415, 101), (555, 101)], AWS_ORG, width=1)
    draw_arrow(draw, [(415, 101), (680, 101)], PURPLE, width=1)

    # ═══════════════════════════════════════════════
    # AWS CLOUD
    # ═══════════════════════════════════════════════
    section_box(draw, 50, 155, W - 100, 870, "AWS Cloud  (us-east-1)", AWS_ORG)

    # ECR + Terraform State (top-right of AWS)
    node(draw, 830, 172, 150, 45, "ECR", "3 repos, scan on push", AWS_ORG)
    node(draw, 1010, 172, 150, 45, "S3 + DynamoDB", "Terraform state + lock", AWS_ORG)

    # ═══════════════════════════════════════════════
    # VPC
    # ═══════════════════════════════════════════════
    section_box(draw, 70, 240, W - 140, 770, "VPC  10.0.0.0/16", K8S_BLUE)

    # ── Public Subnets ──
    section_box(draw, 90, 270, 230, 150, "Public Subnets (3 AZs)", K8S_BLUE, dashed=True)
    node(draw, 105, 290, 195, 50, "Application LB", "internet-facing, ALB class", K8S_BLUE)
    node(draw, 105, 350, 195, 50, "NAT Gateway", "single (cost optimized)", K8S_BLUE)

    # ═══════════════════════════════════════════════
    # EKS CLUSTER
    # ═══════════════════════════════════════════════
    section_box(draw, 340, 270, W - 410, 725, "EKS Cluster  v1.29   |   SPOT t3.medium x2   |   IRSA enabled", TEAL)

    # ── namespace: microservices ──
    section_box(draw, 365, 305, 450, 310, "namespace: microservices", GREEN)

    svc_x = 385
    svc_y = 330

    node(draw, svc_x, svc_y, 195, 55, "API Gateway", "FastAPI :8000  /metrics", PY_BLUE, icon_text="")
    node(draw, svc_x + 220, svc_y, 175, 55, "Order Service", "FastAPI :8001  /metrics", PY_BLUE, icon_text="")
    node(draw, svc_x, svc_y + 75, 195, 55, "Notification Svc", "FastAPI :8002  /metrics", PY_BLUE, icon_text="")

    # HPA / probe info box
    rrect(draw, (svc_x + 220, svc_y + 75, svc_x + 420, svc_y + 145), r=6, fill=SURFACE, outline=BORDER, width=1)
    draw.text((svc_x + 230, svc_y + 80), "HPA: 2-5 replicas @ 70% CPU", fill=GREEN, font=font(10))
    draw.text((svc_x + 230, svc_y + 95), "Liveness + Readiness probes", fill=TEXT_DIM, font=font(10))
    draw.text((svc_x + 230, svc_y + 110), "Resource requests & limits", fill=TEXT_DIM, font=font(10))
    draw.text((svc_x + 230, svc_y + 125), "ConfigMap env injection", fill=TEXT_DIM, font=font(10))

    # Inter-service arrows
    draw_arrow(draw, [(svc_x + 195, svc_y + 28), (svc_x + 220, svc_y + 28)], GREEN, width=1)
    draw_arrow(draw, [(svc_x + 97, svc_y + 55), (svc_x + 97, svc_y + 75)], GREEN, width=1)

    # Ingress
    node(draw, 365, 530, 200, 50, "Ingress (ALB Class)", "path: / -> api-gateway:80", K8S_BLUE)

    # ── namespace: monitoring ──
    section_box(draw, 840, 305, 440, 310, "namespace: monitoring", PROM_RED)

    obs_x = 865
    obs_y = 330

    node(draw, obs_x, obs_y, 185, 55, "Prometheus", "kube-prometheus-stack", PROM_RED)
    node(draw, obs_x + 210, obs_y, 185, 55, "Grafana", "Dashboards + alerts", GRAF_ORG)
    node(draw, obs_x, obs_y + 75, 185, 55, "Loki", "Log aggregation (7d)", LOKI_YEL)
    node(draw, obs_x + 210, obs_y + 75, 185, 55, "Promtail", "DaemonSet log shipper", PINK)

    # Dashboard info
    rrect(draw, (obs_x, obs_y + 150, obs_x + 400, obs_y + 215), r=6, fill=SURFACE, outline=BORDER, width=1)
    draw.text((obs_x + 10, obs_y + 155), "Custom Grafana Dashboards:", fill=GRAF_ORG, font=font_bold(11))
    draw.text((obs_x + 10, obs_y + 172), "Cluster Overview  -  CPU, memory, pod count, disk, network", fill=TEXT_DIM, font=font(10))
    draw.text((obs_x + 10, obs_y + 187), "Microservices  -  request rate, latency p95, error rate, orders", fill=TEXT_DIM, font=font(10))

    # Monitoring arrows
    draw_arrow(draw, [(obs_x + 185, obs_y + 28), (obs_x + 210, obs_y + 28)], GRAF_ORG, width=1)  # prom -> grafana
    draw_arrow(draw, [(obs_x + 185, obs_y + 103), (obs_x + 210, obs_y + 103)], PINK, width=1)  # loki -> promtail (reversed visually)
    draw_arrow(draw, [(obs_x + 92, obs_y + 55), (obs_x + 92, obs_y + 75)], LOKI_YEL, width=1)  # visual link

    # Loki -> Grafana
    draw_arrow(draw, [(obs_x + 92, obs_y + 55), (obs_x + 302, obs_y + 55)], GRAF_ORG, width=1, dashed=True)

    # ── namespace: argocd ──
    section_box(draw, 365, 650, 450, 105, "namespace: argocd", ARGO_RED)

    node(draw, 385, 675, 200, 55, "ArgoCD Server", "App-of-Apps pattern", ARGO_RED)

    # ArgoCD details
    rrect(draw, (600, 675, 795, 730), r=6, fill=SURFACE, outline=BORDER, width=1)
    draw.text((610, 680), "Projects:", fill=ARGO_RED, font=font_bold(11))
    draw.text((610, 695), "microservices  (3 apps, auto-sync)", fill=TEXT_DIM, font=font(10))
    draw.text((610, 710), "observability  (prometheus + loki)", fill=TEXT_DIM, font=font(10))

    # ── namespace: kube-system ──
    section_box(draw, 840, 640, 440, 105, "namespace: kube-system", TEXT_DIM)
    node(draw, 865, 665, 130, 55, "CoreDNS", "Service discovery", TEXT_DIM)
    node(draw, 1010, 665, 130, 55, "kube-proxy", "Network proxy", TEXT_DIM)
    node(draw, 1155, 665, 105, 55, "VPC CNI", "Pod networking", TEXT_DIM)

    # ── Terraform provisioned label ──
    rrect(draw, (365, 770, 820, 820), r=6, fill=SURFACE, outline=PURPLE, width=1)
    draw.text((380, 775), "Provisioned by Terraform:", fill=PURPLE, font=font_bold(12))
    draw.text((380, 793), "VPC (3 AZ)  +  EKS Cluster  +  3 ECR Repos  +  ArgoCD (Helm)  +  IAM/OIDC  +  Addons", fill=TEXT_DIM, font=font(10))

    # ── CI/CD Flow label ──
    rrect(draw, (860, 770, 1260, 820), r=6, fill=SURFACE, outline=GREEN, width=1)
    draw.text((875, 775), "CI/CD Flow (GitHub Actions):", fill=GREEN, font=font_bold(12))
    draw.text((875, 793), "PR: lint+test+plan  |  Merge: build+push ECR, tf apply, ArgoCD sync", fill=TEXT_DIM, font=font(10))

    # ═══════════════════════════════════════════════
    # FLOW ARROWS (main connections)
    # ═══════════════════════════════════════════════

    # User -> ALB
    draw_arrow(draw, [(190, 100), (230, 100), (230, 315), (300, 315)], K8S_BLUE, width=2)
    arrow_label(draw, 195, 82, "HTTPS", K8S_BLUE)

    # ALB -> Ingress
    draw_arrow(draw, [(300, 315), (365, 555)], K8S_BLUE, width=2)

    # Ingress -> API Gateway
    draw_arrow(draw, [(475, 530), (475, svc_y + 55)], K8S_BLUE, width=2)
    arrow_label(draw, 480, 495, "route /", K8S_BLUE)

    # GitHub -> ArgoCD (GitOps)
    draw_arrow(draw, [(330, 135), (330, 675), (385, 700)], ARGO_RED, width=2, dashed=True)
    arrow_label(draw, 255, 430, "GitOps sync", ARGO_RED)

    # ArgoCD -> microservices namespace
    draw_arrow(draw, [(485, 650), (485, 615)], ARGO_RED, width=1, dashed=True)
    arrow_label(draw, 492, 622, "deploy", ARGO_RED)

    # ECR -> EKS (pull images)
    draw_arrow(draw, [(905, 217), (905, 270)], AWS_ORG, width=2, dashed=True)
    arrow_label(draw, 915, 230, "pull images", AWS_ORG)

    # Build & Push -> ECR
    draw_arrow(draw, [(610, 122), (610, 150), (830, 150), (830, 172)], AWS_ORG, width=1, dashed=True)
    arrow_label(draw, 690, 133, "push images", AWS_ORG)

    # Microservices -> Prometheus (metrics scrape)
    draw_arrow(draw, [(815, svc_y + 28), (865, obs_y + 28)], PROM_RED, width=2, dashed=True)
    arrow_label(draw, 820, svc_y + 12, "/metrics", PROM_RED)

    # Promtail -> microservices (log collection)
    draw_arrow(draw, [(obs_x + 302, obs_y + 130), (obs_x + 415, obs_y + 130), (obs_x + 415, obs_y + 230),
                       (815, obs_y + 230), (815, svc_y + 55 + 75)], PINK, width=1, dashed=True)
    arrow_label(draw, 825, obs_y + 218, "collect logs", PINK)

    # ═══════════════════════════════════════════════
    # LEGEND
    # ═══════════════════════════════════════════════
    leg_y = 855
    section_box(draw, 70, leg_y, W - 140, 150, "Technology Stack", BORDER)

    col1, col2, col3, col4 = 100, 420, 740, 1100
    row1, row2, row3, row4 = leg_y + 20, leg_y + 48, leg_y + 76, leg_y + 104

    def legend_item(x, y, color, label, detail):
        rrect(draw, (x, y + 2, x + 10, y + 12), r=2, fill=color)
        draw.text((x + 16, y), label, fill=TEXT_W, font=font_bold(11))
        draw.text((x + 16, y + 15), detail, fill=TEXT_DIM, font=font(9))

    legend_item(col1, row1, K8S_BLUE, "Amazon EKS", "Managed Kubernetes (v1.29)")
    legend_item(col1, row2, AWS_ORG, "AWS Services", "VPC, ALB, ECR, NAT, S3, DynamoDB")
    legend_item(col1, row3, PURPLE, "Terraform", "IaC - modular architecture")
    legend_item(col1, row4, GREEN, "GitHub Actions", "3 workflows: CI, build, deploy")

    legend_item(col2, row1, ARGO_RED, "ArgoCD", "GitOps - app-of-apps pattern")
    legend_item(col2, row2, PROM_RED, "Prometheus", "Metrics collection (7d retention)")
    legend_item(col2, row3, GRAF_ORG, "Grafana", "Dashboards + visualization")
    legend_item(col2, row4, LOKI_YEL, "Loki + Promtail", "Centralized log aggregation")

    legend_item(col3, row1, PY_BLUE, "Python FastAPI", "3 microservices with /metrics")
    legend_item(col3, row2, TEAL, "EKS Addons", "CoreDNS, kube-proxy, VPC CNI")
    legend_item(col3, row3, PINK, "Log Pipeline", "Promtail DaemonSet -> Loki")
    legend_item(col3, row4, TEXT_DIM, "Helm Charts", "ArgoCD, kube-prometheus, loki-stack")

    # Key stats
    rrect(draw, (col4, row1, col4 + 370, row4 + 25), r=6, fill=SURFACE, outline=TEAL, width=1)
    draw.text((col4 + 10, row1 + 5), "Key Highlights", fill=TEAL, font=font_bold(12))
    stats = [
        "SPOT instances  ~60% cost savings",
        "Single NAT GW   saves ~$65/mo",
        "HPA auto-scaling  2-5 replicas",
        "IRSA  fine-grained pod IAM",
        "Full GitOps  auto-sync + self-heal",
        "3 pillars  metrics, logs, dashboards",
    ]
    for i, s in enumerate(stats):
        parts = s.split("  ", 1)
        draw.text((col4 + 15, row1 + 24 + i * 15), parts[0], fill=TEXT_W, font=font_bold(10))
        if len(parts) > 1:
            draw.text((col4 + 15 + len(parts[0]) * 7, row1 + 24 + i * 15), parts[1], fill=TEXT_DIM, font=font(10))

    # ═══════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════
    output = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "architecture-diagram.png")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    img.save(output, "PNG")
    print(f"Saved: {output}")
    print(f"Size: {W}x{H}")


if __name__ == "__main__":
    main()
