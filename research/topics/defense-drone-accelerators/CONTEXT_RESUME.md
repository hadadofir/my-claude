# Context Resume File

**Last Updated**: 2026-01-27 (session 2)
**Purpose**: Resume research session after break

---

## Research Goal

Find a **disruptive accelerator chip opportunity** in the defense drone market for an **experienced logic designer**. User is:
- Not fixed on ASIC (FPGA IP is acceptable)
- No direct defense contacts
- Prefers commercial-first strategy
- Flexible on product vs IP licensing business model

---

## Key Conclusions Reached

### Primary Opportunity: Neuromorphic VIO Accelerator

**Thesis**: Event cameras + neuromorphic processing = 25-100x power reduction for visual navigation. The gap is that **nobody has productized an integrated solution**.

**Recommended Path**:
1. **Year 1-2**: FPGA IP for event-based VIO
2. **Year 2-3**: Small module product
3. **Year 3-5**: ASIC if volume justifies
4. **Commercial first** → Defense later

### Secondary Opportunity: Frame-Based VIO IP

More conservative, faster to market, but less differentiated.

---

## Completed Outputs

All in `/media/external/Ofir/sandbox/research/topics/defense-drone-accelerators/outputs/`:

| File | Content |
|------|---------|
| `summary.md` | Overall research summary |
| `neuromorphic_vio_deep_dive.md` | Deep dive on event cameras + neuromorphic |
| `vio_slam_technical_architecture.md` | Block-by-block RTL acceleration guide |
| `customer_landscape.md` | Profiles of ModalAI, Skydio, Flyability, Shield AI, etc. |
| `prototype_planning.md` | FPGA boards, event cameras, dev setup, budget |
| `competitive_deep_dive.md` | SynSense vs BrainChip vs Intel Loihi detailed comparison |
| `competitive_deep_dive_v2.md` | Updated competitive analysis (Jan 2026) - neuromorphic + non-neuromorphic + new entrants |
| `fpga_board_selection.md` | Detailed FPGA board comparison with purchase plan |

## Source Materials

In `/media/external/Ofir/sandbox/research/topics/defense-drone-accelerators/sources/`:

| File | Content |
|------|---------|
| `landscape_research.md` | Initial market research |
| `opportunity_analysis.md` | Initial opportunity scoring |
| `commercial_first_strategy.md` | Refined strategy for commercial entry |

---

## Key Technical Findings

### What to Accelerate (VIO Pipeline)

| Block | Priority | Hardware Fit |
|-------|----------|--------------|
| FAST corner detection | P1 | ★★★★★ |
| Optical flow (Lucas-Kanade) | P1 | ★★★★★ |
| ORB/BRIEF descriptors | P1 | ★★★★★ |
| Event camera interface | P2 | ★★★★★ |
| IMU preintegration | P3 | ★★★☆☆ |
| State estimation (EKF) | P3 | ★★☆☆☆ |

### Neuromorphic Key Numbers

| Metric | Conventional | Neuromorphic |
|--------|--------------|--------------|
| Power (VIO) | 5-15W | 50-200mW |
| Latency | 20-50ms | <5ms |
| Data bandwidth | 30 MB/s | 0.3-3 MB/s |

### FPGA Resource Estimate (Full VIO Front-End)

- LUTs: ~80,000 (36% of ZU15EG)
- BRAM: ~3 MB (52%)
- DSPs: ~200 (19%)
- Power: ~2W

---

## Priority Customers

### Tier 1 (Immediate)
1. **ModalAI** - Platform company, IP licensing target
2. **Prophesee** - Event camera partner, joint development
3. **Flyability** - GPS-denied validation use case

### Tier 2 (Medium-term)
4. **Auterion** - PX4 ecosystem
5. **Corvus Robotics** - Warehouse drones
6. **AeroVironment** - Defense bridge

---

## Open Questions / Next Steps

If continuing research:

1. **Deeper technical**: Specific SNN architectures for event-based feature extraction
2. **Business model**: Detailed financial model for FPGA IP licensing
3. ~~**Competitive**: Deeper analysis of SynSense, BrainChip capabilities~~ DONE (competitive_deep_dive_v2.md)
4. **Partnership**: How to approach Prophesee for co-development
5. ~~**Prototyping**: What FPGA dev board to start with~~ DONE (fpga_board_selection.md) - Answer: AMD Kria KV260

---

## Key Sources Used

- [UZH Robotics & Perception Group](https://rpg.ifi.uzh.ch/research_dvs.html)
- [MIT Navion Paper](https://eems.mit.edu/wp-content/uploads/2018/12/2019_jssc_navion.pdf)
- [eSLAM FPGA Acceleration](https://arxiv.org/abs/1906.05096)
- [ESVO2 Event-Based VIO](https://arxiv.org/html/2410.09374v1)
- [Prophesee Event Cameras](https://www.prophesee.ai/)
- [SynSense Speck](https://www.synsense.ai/products/speck-2/)
- [ModalAI VOXL 2](https://www.modalai.com/products/voxl-2)

---

## Session 2 Key Findings (2026-01-27)

### Competitive Update (competitive_deep_dive_v2.md)
- **SynSense** acquired iniVation (event camera maker) in Feb 2024 - most vertically integrated neuromorphic vision company, but still stuck at 128x128 resolution. HD VIO years away.
- **BrainChip** financially fragile: $1.31M revenue, $3.8M/quarter burn, ~3 quarters runway. AKD1500 taping out, first silicon Q3 2026. Defense deals are classification, not VIO.
- **Intel Loihi 3** reportedly announced Jan 2026 (8M neurons, 4nm) - still research only, no commercial path.
- **MIT Navion** - NO spinoff found after 5+ years. 2mW VIO ASIC remains uncommercialized. This IS the opportunity.
- **Hailo-8** demonstrated on drones (CES 2025) but only for CNN inference, not VIO.
- **Real competition**: Qualcomm RB5 (5-10W) and NVIDIA Orin Nano (7-15W). The 100x power gap for micro-drones is the wedge.
- **Lattice FPGAs**: Platform, not competitor. CrossLink-NX as MIPI bridge in production architecture.

### FPGA Board Decision (fpga_board_selection.md)
- **Winner: AMD Kria KV260** ($199-250) - 117K LUTs, 7.1MB BRAM, 1248 DSPs, free tools
- **Prophesee sells an official Metavision Kria Starter Kit** with IMX636 HD event camera
- Open-source GitHub repo exists: LogicTronixInc/Kria-Prophesee-Event-VitisAI
- AMD refreshed KV260 in 2025 (auto-focus upgrade), no successor announced
- K26 SOM standalone: ~$406 commercial, ~$562 industrial
- **Total prototype cost: ~$800-1,300** (KV260 + Prophesee kit + IMU)
- PolarFire SoC is secondary option for defense/security production (flash-based, RISC-V, secure)

---

## To Resume

Tell Claude:
> "Resume research on defense drone accelerators. Read the CONTEXT_RESUME.md file in /media/external/Ofir/sandbox/research/topics/defense-drone-accelerators/ to get up to speed. I want to continue with [specific topic]."
