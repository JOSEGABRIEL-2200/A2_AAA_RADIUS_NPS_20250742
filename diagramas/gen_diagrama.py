import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(17, 12), dpi=150)
ax.set_xlim(0, 170); ax.set_ylim(0, 120); ax.axis("off")
fig.patch.set_facecolor("white")

INK = "#1f2937"; MUTED = "#6b7280"
C_R = "#0f766e"; C_SRV = "#0369a1"; C_ADM = "#7c3aed"; C_RAD = "#dc2626"; C_SSH = "#16a34a"; C_MG = "#9ca3af"


def box(x, y, w, h, title, lines, color, fs=9.0, tfs=12, face="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.8",
                                linewidth=2, edgecolor=color, facecolor=face, zorder=3))
    ax.text(x + w/2, y + h - 3.0, title, ha="center", va="center", fontsize=tfs, fontweight="bold", color=color, zorder=4)
    for i, t in enumerate(lines):
        ax.text(x + w/2, y + h - 6.8 - i*3.1, t, ha="center", va="center", fontsize=fs,
                color=INK, family="DejaVu Sans Mono", zorder=4)


def link(p1, p2, label=None, color=INK, lw=2.2, ls="-", off=(0, 1.8), fs=8.3):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, ls=ls, zorder=2, solid_capstyle="round")
    if label:
        ax.text((p1[0]+p2[0])/2 + off[0], (p1[1]+p2[1])/2 + off[1], label, ha="center", va="center",
                fontsize=fs, color=MUTED, zorder=5, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))


def flow(p1, p2, color, rad=0.0, lw=2.4):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=16, color=color, lw=lw,
                                 ls=(0, (5, 3)), connectionstyle=f"arc3,rad={rad}", zorder=2))


ax.text(85, 117, "Asignación 2 — AAA con RADIUS (Windows Server NPS) en Cisco IOS",
        ha="center", fontsize=17, fontweight="bold", color=INK)
ax.text(85, 113.2, "Jose Gabriel Feliz Maria · Matrícula 2025-0742 · Seguridad de Redes (ITLA)",
        ha="center", fontsize=10.5, color=MUTED)

# R1
box(60, 84, 50, 25, "R1 (Cisco IOL) · cliente RADIUS", [
    "e0/0.10  10.7.42.1/25    VLAN 10",
    "e0/0.20  10.7.42.129/29  VLAN 20",
    "e0/0.99  10.7.42.137/29  VLAN 99",
    "DHCP VLAN 10 · SSH v2 (solo VLAN 10)",
    "RADIUS desde e0/0.20",
    "accounting exec start-stop"], C_R, tfs=11.5)

# SW1
box(60, 52, 50, 22, "SW1 (Cisco IOL L2) · cliente RADIUS", [
    "e0/0 trunk 10,20,99 · nativa 999",
    "Vlan99  10.7.42.138/29",
    "port-security · BPDU guard",
    "SSH v2 (solo VLAN 10)"], C_R, tfs=11.5)

# Servidor
box(6, 14, 50, 30, "WINDOWS SERVER 2022", [
    "DC jose.gabriel · 10.7.42.130/29",
    "NPS = servidor RADIUS",
    "UDP 1812 / 1813",
    "AD: OU AAA_Red",
    "GRP_NIVEL_0 / 5 / 10",
    "VLAN 20 · NET-SERVIDOR (VMnet4)"], C_SRV, fs=8.6, tfs=11.5)

# PC admin
box(114, 14, 50, 30, "PC ADMINISTRADOR (host)", [
    "DHCP reservado 10.7.42.20/25",
    "cliente SSH (OpenSSH)",
    "usuario0   -> nivel 0",
    "usuario5   -> nivel 5",
    "usuario10  -> nivel 10",
    "VLAN 10 · NET-ADMIN (VMnet8)"], C_ADM, fs=8.6, tfs=11.5)

# Enlaces fisicos
link((85, 83.5), (85, 74.5), "e0/0 ↔ e0/0 (trunk)", off=(12, 0))
link((70, 51.5), (40, 44.5), "e0/1 (VLAN 20)", off=(-4, 2.2))
link((100, 51.5), (130, 44.5), "e0/2 (VLAN 10)", off=(4, 2.2))

# Flujos
flow((59.5, 96), (22, 44.5), C_RAD, rad=0.25)
flow((59.5, 62), (40, 44.8), C_RAD, rad=0.15, lw=2.0)
ax.text(19, 75, "RADIUS\nAccess-Request / Accept / Reject\nshell:priv-lvl = 0 · 5 · 10",
        ha="center", fontsize=9.2, color=C_RAD, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_RAD, lw=1), zorder=5)
flow((148, 44.5), (110.5, 96), C_SSH, rad=0.25)
flow((130, 44.8), (110.5, 62), C_SSH, rad=0.15, lw=2.0)
ax.text(152, 75, "SSH v2\n(solo desde VLAN 10)\nR1 10.7.42.1 · SW1 10.7.42.138",
        ha="center", fontsize=9.2, color=C_SSH, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_SSH, lw=1), zorder=5)

# Leyenda
ax.add_patch(FancyBboxPatch((2, 0.5), 166, 9.5, boxstyle="round,pad=0.4,rounding_size=1.5",
                            linewidth=1.2, edgecolor=C_MG, facecolor="#f9fafb", zorder=1))
rows = [
    (C_SSH, "VTY (SSH):  lista VTY-RADIUS", "solo RADIUS · si el NPS no responde, nadie entra por SSH"),
    (C_RAD, "Consola y AUX:  lista CON-AUX", "RADIUS primero · usuario local de recuperación solo si el NPS no responde"),
]
for i, (c, a, b) in enumerate(rows):
    y = 7.2 - i*3.8
    ax.text(4.5, y, a, fontsize=9.6, fontweight="bold", color=c, va="center")
    ax.text(62, y, b, fontsize=9.2, color=INK, va="center")

plt.savefig("topologia_a2_aaa.png", bbox_inches="tight", facecolor="white")
print("ok")
