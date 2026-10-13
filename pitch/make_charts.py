import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Ellipse

# ---- palette (validated default, dataviz skill references/palette.md) ----
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

BLUE = "#2a78d6"       # categorical slot 1 - Classical VIO
ORANGE = "#eb6834"     # categorical slot 8 - GPU-class learned VIO
VIOLET = "#4a3aa7"     # categorical slot 5 - Our target / the gap

SEQ_300 = "#6da7ec"    # sequential step 300
SEQ_550 = "#1c5cab"    # sequential step 550

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["text.color"] = INK_PRIMARY
plt.rcParams["axes.edgecolor"] = BASELINE
plt.rcParams["axes.labelcolor"] = INK_SECONDARY
plt.rcParams["xtick.color"] = INK_MUTED
plt.rcParams["ytick.color"] = INK_MUTED

# =====================================================================
# Chart 1 — Market growth (single sequential hue, two ordinal steps)
# =====================================================================
fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

years = ["2026", "2033"]
values = [163.1, 334.2]
colors = [SEQ_300, SEQ_550]
x = [0, 1]
bar_width = 0.42

bars = ax.bar(x, values, width=bar_width, color=colors, zorder=3)

# direct labels at the cap
for xi, v in zip(x, values):
    ax.text(xi, v + 10, f"${v:,.1f}M", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color=INK_PRIMARY)

ax.text(0.5, -70, "9.4% CAGR", ha="center", va="top", fontsize=11.5,
        color=INK_SECONDARY, transform=ax.transData)

ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=12, color=INK_SECONDARY)
ax.set_ylim(0, 400)
ax.set_yticks([0, 100, 200, 300, 400])
ax.set_yticklabels(["0", "100", "200", "300", "$400M"], fontsize=10)
ax.grid(axis="y", color=GRIDLINE, linewidth=1, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(BASELINE)
ax.tick_params(axis="both", length=0)
ax.set_title("GPS-denied navigation market", fontsize=14, fontweight="bold",
             color=INK_PRIMARY, loc="left", pad=14)

plt.tight_layout()
plt.savefig("/home/ofir-hadad/ofir/sandbox/pitch/assets/market_growth.png",
            facecolor=SURFACE, bbox_inches="tight")
plt.close()

# =====================================================================
# Chart 2 — Power vs accuracy positioning (categorical, 3 series)
# =====================================================================
fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

# log-scale-ish power axis via manual positions (mW -> W)
# x positions are illustrative, not a strict log scale, chosen for readability
points = [
    # (label, x, y_accuracy(0-10), color, xytext, ha, va)
    ("Classical VIO\n(ORB-SLAM3, MIT Navion)", 0.55, 4.6, BLUE, (14, -6), "left", "top"),
    ("GPU-class learned VIO\n(DPVO, DROID-SLAM, Jetson)", 8.6, 8.6, ORANGE, (-14, 14), "right", "bottom"),
]
target_zone = (2.4, 7.0)  # x, y center of the open gap we target

for label, xx, yy, color, xytext, ha, va in points:
    ax.scatter([xx], [yy], s=170, color=color, zorder=4,
               edgecolors=SURFACE, linewidths=2)
    ax.annotate(label, (xx, yy), textcoords="offset points",
                xytext=xytext, ha=ha, va=va, fontsize=10,
                color=INK_SECONDARY, linespacing=1.35)

# highlight the open gap as a dashed ellipse in the target hue
ellipse = Ellipse(target_zone, width=2.6, height=2.6, fill=False,
                   edgecolor=VIOLET, linewidth=2.2, linestyle=(0, (4, 3)),
                   zorder=3)
ax.add_patch(ellipse)
ax.scatter([target_zone[0]], [target_zone[1]], s=170, color=VIOLET, zorder=4,
           edgecolors=SURFACE, linewidths=2, marker="*")
ax.annotate("Open gap\n(our target)", target_zone, textcoords="offset points",
            xytext=(0, 16), ha="center", fontsize=10, fontweight="bold",
            color=VIOLET, linespacing=1.3)

ax.set_xlim(0, 11)
ax.set_ylim(3, 11)
ax.set_xticks([0.5, 2, 4, 6, 8, 10])
ax.set_xticklabels(["0.5W", "2W", "4W", "6W", "8W", "10W+"], fontsize=10)
ax.set_yticks([])
ax.set_xlabel("Power (inference)", fontsize=11, color=INK_SECONDARY)
ax.set_ylabel("Accuracy / robustness  →", fontsize=11, color=INK_SECONDARY)
ax.grid(axis="x", color=GRIDLINE, linewidth=1, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color(BASELINE)
ax.spines["bottom"].set_color(BASELINE)
ax.tick_params(axis="both", length=0)

# simple legend (3 series present)
legend_items = [("Classical VIO", BLUE), ("GPU-class learned VIO", ORANGE),
                ("Our target", VIOLET)]
for i, (lab, col) in enumerate(legend_items):
    ax.scatter([], [], s=90, color=col, label=lab)
ax.legend(loc="lower right", frameon=False, fontsize=9.5, labelcolor=INK_SECONDARY)

ax.set_title("Nothing efficient sits between cheap classical VIO and\npower-hungry GPU-class learned VIO",
             fontsize=13, fontweight="bold", color=INK_PRIMARY, loc="left", pad=14)

plt.tight_layout()
plt.savefig("/home/ofir-hadad/ofir/sandbox/pitch/assets/power_accuracy_gap.png",
            facecolor=SURFACE, bbox_inches="tight")
plt.close()

print("Charts written.")
