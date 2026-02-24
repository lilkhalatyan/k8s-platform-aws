#!/usr/bin/env python3
"""Generate architecture diagram for k8s-platform-aws."""

from PIL import Image, ImageDraw, ImageFont
import os

WIDTH = 1400
HEIGHT = 1000
BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
BLUE = "#58a6ff"
GREEN = "#3fb950"
ORANGE = "#d29922"
PURPLE = "#bc8cff"
RED = "#f85149"
TEAL = "#39d2c0"
PINK = "#f778ba"

def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_box(draw, x, y, w, h, label, color, fill_alpha=None, sublabel=None, icon=None):
    fill = color + "18"
    rounded_rect(draw, (x, y, x+w, y+h), radius=8, fill=fill, outline=color, width=2)
    font = get_font(14)
    font_small = get_font(11)
    if icon:
        draw.text((x+10, y+8), icon, fill=color, font=get_font(16))
        draw.text((x+30, y+10), label, fill=color, font=font)
    else:
        draw.text((x+10, y+10), label, fill=color, font=font)
    if sublabel:
        draw.text((x+10, y+28), sublabel, fill=TEXT_DIM, font=font_small)

def draw_arrow(draw, x1, y1, x2, y2, color=TEXT_DIM, label=None, dashed=False):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
    # Arrowhead
    import math
    angle = math.atan2(y2-y1, x2-x1)
    arrow_len = 10
    ax1 = x2 - arrow_len * math.cos(angle - math.pi/6)
    ay1 = y2 - arrow_len * math.sin(angle - math.pi/6)
    ax2 = x2 - arrow_len * math.cos(angle + math.pi/6)
    ay2 = y2 - arrow_len * math.sin(angle + math.pi/6)
    draw.polygon([(x2, y2), (int(ax1), int(ay1)), (int(ax2), int(ay2))], fill=color)
    if label:
        mx, my = (x1+x2)//2, (y1+y2)//2
        font = get_font(10)
        draw.text((mx+4, my-12), label, fill=TEXT_DIM, font=font)

def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    title_font = get_font(24)
    subtitle_font = get_font(13)
    section_font = get_font(16)
    label_font = get_font(12)
    small_font = get_font(10)

    # Title
    draw.text((WIDTH//2 - 200, 15), "K8s Platform AWS - Architecture", fill=TEXT, font=title_font)
    draw.text((WIDTH//2 - 180, 48), "EKS + ArgoCD + Prometheus + Grafana + Loki", fill=TEXT_DIM, font=subtitle_font)

    # ── GitHub Section (top) ──
    gh_y = 80
    rounded_rect(draw, (50, gh_y, 1350, gh_y+120), radius=10, fill="#161b2233", outline=BORDER, width=2)
    draw.text((60, gh_y+5), "GitHub", fill=TEXT, font=section_font)

    # Repo box
    draw_box(draw, 70, gh_y+30, 200, 75, "Git Repository", BLUE, sublabel="apps/ terraform/ kubernetes/")

    # CI workflows
    draw_box(draw, 320, gh_y+30, 180, 35, "CI Pipeline", GREEN, sublabel=None)
    draw.text((330, gh_y+48), "pytest, black, tflint", fill=TEXT_DIM, font=small_font)

    draw_box(draw, 520, gh_y+30, 180, 35, "Build & Push", ORANGE, sublabel=None)
    draw.text((530, gh_y+48), "Docker build → ECR", fill=TEXT_DIM, font=small_font)

    draw_box(draw, 720, gh_y+30, 180, 35, "Terraform CI/CD", PURPLE, sublabel=None)
    draw.text((730, gh_y+48), "Plan on PR, Apply on merge", fill=TEXT_DIM, font=small_font)

    # ArgoCD sync label
    draw_box(draw, 950, gh_y+30, 180, 35, "ArgoCD Sync", RED, sublabel=None)
    draw.text((960, gh_y+48), "GitOps auto-sync", fill=TEXT_DIM, font=small_font)

    # Arrows from repo to workflows
    draw_arrow(draw, 270, gh_y+65, 320, gh_y+48, GREEN, "PR")
    draw_arrow(draw, 270, gh_y+65, 520, gh_y+48, ORANGE, "merge")
    draw_arrow(draw, 270, gh_y+65, 720, gh_y+48, PURPLE)

    # ── AWS Cloud Section ──
    aws_y = 220
    rounded_rect(draw, (50, aws_y, 1350, 970), radius=10, fill="#161b2211", outline="#f0883e", width=2)
    draw.text((60, aws_y+5), "AWS Cloud", fill="#f0883e", font=section_font)

    # ECR
    draw_box(draw, 70, aws_y+35, 160, 50, "ECR", ORANGE, sublabel="Docker images")

    # ── VPC Section ──
    vpc_y = aws_y + 100
    rounded_rect(draw, (70, vpc_y, 1330, 950), radius=10, fill="#1c2333", outline=BLUE, width=2)
    draw.text((80, vpc_y+5), "VPC  10.0.0.0/16", fill=BLUE, font=section_font)

    # Public Subnets
    pub_y = vpc_y + 35
    rounded_rect(draw, (90, pub_y, 500, pub_y+100), radius=8, fill="#0d2137", outline="#1f6feb", width=1)
    draw.text((100, pub_y+5), "Public Subnets (3 AZs)", fill="#1f6feb", font=label_font)
    draw_box(draw, 110, pub_y+28, 160, 55, "ALB", BLUE, sublabel="Ingress Controller")
    draw_box(draw, 290, pub_y+28, 160, 55, "NAT Gateway", BLUE, sublabel="Single (cost opt.)")

    # Private Subnets
    priv_y = vpc_y + 35
    rounded_rect(draw, (520, priv_y, 1310, priv_y+590), radius=8, fill="#0d2117", outline="#238636", width=1)
    draw.text((530, priv_y+5), "Private Subnets (3 AZs)", fill="#238636", font=label_font)

    # ── EKS Cluster ──
    eks_y = priv_y + 30
    rounded_rect(draw, (540, eks_y, 1290, eks_y+545), radius=8, fill="#161b22", outline=TEAL, width=2)
    draw.text((555, eks_y+5), "EKS Cluster (v1.29)  —  Spot Instances (t3.medium x2)", fill=TEAL, font=section_font)

    # ── Microservices namespace ──
    ms_y = eks_y + 35
    rounded_rect(draw, (560, ms_y, 900, ms_y+200), radius=8, fill="#1a1520", outline=PURPLE, width=1)
    draw.text((570, ms_y+5), "namespace: microservices", fill=PURPLE, font=label_font)

    # Services
    svc_w, svc_h = 150, 80
    svc_y = ms_y + 28

    draw_box(draw, 575, svc_y, svc_w, svc_h, "api-gateway", GREEN, sublabel="FastAPI :8000\n/health /metrics")
    draw_box(draw, 740, svc_y, svc_w, svc_h, "order-service", GREEN, sublabel="FastAPI :8001\n/health /metrics")

    draw_box(draw, 575, svc_y+90, svc_w, svc_h, "notification-svc", GREEN, sublabel="FastAPI :8002\n/health /metrics")

    # HPA labels
    draw.text((740, svc_y+90+5), "HPA: 2-5 replicas", fill=TEXT_DIM, font=small_font)
    draw.text((740, svc_y+90+20), "CPU target: 70%", fill=TEXT_DIM, font=small_font)
    draw.text((740, svc_y+90+35), "Liveness + Readiness", fill=TEXT_DIM, font=small_font)
    draw.text((740, svc_y+90+50), "Resource limits set", fill=TEXT_DIM, font=small_font)

    # ── Monitoring namespace ──
    mon_y = eks_y + 35
    rounded_rect(draw, (920, mon_y, 1270, mon_y+200), radius=8, fill="#1a1a10", outline=ORANGE, width=1)
    draw.text((930, mon_y+5), "namespace: monitoring", fill=ORANGE, font=label_font)

    obs_y = mon_y + 28
    draw_box(draw, 935, obs_y, 140, 50, "Prometheus", RED, sublabel="Metrics (7d ret.)")
    draw_box(draw, 1095, obs_y, 140, 50, "Grafana", ORANGE, sublabel="Dashboards")

    draw_box(draw, 935, obs_y+60, 140, 50, "Loki", PINK, sublabel="Log aggregation")
    draw_box(draw, 1095, obs_y+60, 140, 50, "Promtail", PINK, sublabel="Log collector")

    # Custom dashboards label
    draw.text((1095, obs_y+120), "Custom Dashboards:", fill=TEXT_DIM, font=small_font)
    draw.text((1095, obs_y+135), "- Cluster Overview", fill=TEXT_DIM, font=small_font)
    draw.text((1095, obs_y+150), "- Microservices Metrics", fill=TEXT_DIM, font=small_font)

    # ── ArgoCD namespace ──
    argo_y = eks_y + 260
    rounded_rect(draw, (560, argo_y, 900, argo_y+100), radius=8, fill="#1a1015", outline=RED, width=1)
    draw.text((570, argo_y+5), "namespace: argocd", fill=RED, font=label_font)

    draw_box(draw, 575, argo_y+28, 180, 55, "ArgoCD Server", RED, sublabel="App-of-Apps pattern")
    draw.text((775, argo_y+33), "Projects:", fill=TEXT_DIM, font=small_font)
    draw.text((775, argo_y+48), "- microservices (3 apps)", fill=TEXT_DIM, font=small_font)
    draw.text((775, argo_y+63), "- observability (prom + loki)", fill=TEXT_DIM, font=small_font)

    # ── kube-system ──
    ks_y = eks_y + 260
    rounded_rect(draw, (920, ks_y, 1270, ks_y+100), radius=8, fill="#111518", outline=TEXT_DIM, width=1)
    draw.text((930, ks_y+5), "namespace: kube-system", fill=TEXT_DIM, font=label_font)
    draw.text((940, ks_y+28), "CoreDNS", fill=TEXT_DIM, font=small_font)
    draw.text((940, ks_y+43), "kube-proxy", fill=TEXT_DIM, font=small_font)
    draw.text((940, ks_y+58), "vpc-cni", fill=TEXT_DIM, font=small_font)
    draw.text((940, ks_y+73), "AWS ALB Ingress Controller", fill=TEXT_DIM, font=small_font)

    # ── IRSA label ──
    draw.text((560, eks_y + 385), "IRSA enabled  |  Cluster logging: api, audit, authenticator", fill=TEAL, font=small_font)

    # ── Arrows ──
    # ALB → api-gateway
    draw_arrow(draw, 270, pub_y+55, 575, svc_y+40, BLUE, "traffic")

    # ArgoCD ← GitHub (GitOps sync)
    draw_arrow(draw, 1040, gh_y+65, 665, argo_y, RED, "auto-sync")

    # Prometheus scrapes microservices
    draw_arrow(draw, 935, obs_y+25, 900, svc_y+40, RED, "/metrics")

    # Promtail → Loki
    draw_arrow(draw, 1095, obs_y+85, 1075, obs_y+85, PINK)

    # api-gateway → order & notification
    draw_arrow(draw, 725, svc_y+40, 740, svc_y+40, GREEN)
    draw_arrow(draw, 650, svc_y+80, 650, svc_y+90, GREEN)

    # ECR → EKS
    draw_arrow(draw, 230, aws_y+60, 540, eks_y+10, ORANGE, "pull images")

    # ── Legend ──
    leg_y = 895
    rounded_rect(draw, (90, leg_y, 500, leg_y+45), radius=6, fill="#161b22", outline=BORDER, width=1)
    draw.text((100, leg_y+5), "Terraform", fill=PURPLE, font=small_font)
    draw.text((170, leg_y+5), "GitHub Actions", fill=GREEN, font=small_font)
    draw.text((270, leg_y+5), "ArgoCD GitOps", fill=RED, font=small_font)
    draw.text((370, leg_y+5), "Prometheus", fill=ORANGE, font=small_font)
    draw.text((100, leg_y+22), "Python FastAPI", fill=GREEN, font=small_font)
    draw.text((210, leg_y+22), "Loki + Promtail", fill=PINK, font=small_font)
    draw.text((330, leg_y+22), "Helm Charts", fill=TEAL, font=small_font)

    # Save
    output = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "architecture-diagram.png")
    img.save(output, "PNG", quality=95)
    print(f"Saved to {output}")

if __name__ == "__main__":
    main()
