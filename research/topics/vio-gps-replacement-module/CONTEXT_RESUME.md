# Context Resume File

**Last Updated**: 2026-05-07 (session 3)
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

All in `outputs/`:

| File | Content |
|------|---------|
| `summary.md` | Overall research summary |
| `neuromorphic_vio_deep_dive.md` | Deep dive on event cameras + neuromorphic |
| `vio_slam_technical_architecture.md` | Block-by-block RTL acceleration guide |
| `customer_landscape.md` | Profiles of ModalAI, Skydio, Flyability, Shield AI, etc. |
| `prototype_planning.md` | FPGA boards, event cameras, dev setup, budget |
| `competitive_deep_dive.md` | SynSense vs BrainChip vs Intel Loihi detailed comparison |
| `competitive_deep_dive_v2.md` | Updated competitive analysis (Jan 2026) - neuromorphic + non-neuromorphic + new entrants |
| `competitive_deep_dive_v3.md` | **Latest** competitive analysis (May 2026) - Q1-Q2 2026 updates, BrainChip AKD1500, Loihi 3 commercialization, defense market validation |
| `neuromorphic_vs_ann_vio_deep_dive.md` | Deep dive: SNN vs conventional NNs vs classical for VIO — computation models, MAC counts, hardware mapping, training comparison |
| `snn_mathematics_and_demo.md` | **New** SNN from scratch: LIF math, surrogate gradients, BPTT, working demo code (N-MNIST + DVS Gesture), KV260 deployment path |
| `fpga_board_selection.md` | Detailed FPGA board comparison with purchase plan |

## Source Materials

In `sources/`:

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

## Session 3 Key Findings (2026-05-07)

### Competitive Update (competitive_deep_dive_v3.md)
- **BrainChip AKD1500 confirmed**: Unveiled at Embedded World NA. 800 GOPS at <300mW on GF 22FDX. Volume production Q3 2026. But still wrong architecture for VIO — their defense play is counter-drone radar classification, not navigation.
- **Intel Loihi 3 commercializing Q3 2026**: Targets healthcare, autonomous vehicles, industrial. NOT going after drone VIO. Validates neuromorphic crossing from lab to product.
- **Prophesee new CEO (Jean Ferré)**: 30+ years in defense/aerospace. Signals Prophesee pushing hard into defense. Reinforces partnership opportunity — they need compute for their sensors.
- **SynSense Kumrah AI JV**: Aerospace/industrial neuromorphic vision JV (May 2025, post-v2 cutoff). Still low-res, no HD VIO timeline.
- **Hailo at XPONENTIAL 2026 (May 2026)**: Drone companion computers with detection/inference. Still no VIO backend.
- **MIT Navion**: Still unspinoff'd — confirmed May 2026.
- **No new VIO entrants**: Gap remains wide open.

### Defense Market Validation (Major)
- **GPS-denied navigation market**: $163.1M in 2026 → $334.2M by 2033 (9.4% CAGR)
- **US Army Red Dragon contract**: $17.6M for autonomous strike drone with 400km GPS-denied range (April 2026)
- **Pentagon counter-drone**: $3.1B allocated — demand on both sides (GPS-denied offense + counter-drone defense)
- GPS-denied capability shifting from optional to **baseline requirement** due to Ukraine/Middle East lessons

### Updated Priority Contacts
- **Prophesee (Jean Ferré, new CEO)**: Best near-term outreach. Defense background means accessible conversation. They need a compute partner.

---

## To Resume

Tell Claude:
> "Resume research on the VIO GPS-replacement module. Read the CONTEXT_RESUME.md file in ~/ofir/sandbox/research/topics/vio-gps-replacement-module/ to get up to speed. I want to continue with [specific topic]."

**Note (2026-08-02):** This project was renamed from "defense-drone-accelerators" to "vio-gps-replacement-module" to reflect the validated Phase 1 positioning: accelerate existing classical VIO/SLAM algorithms first, with the product framed as a GPS-protocol-compatible replacement module (not a defense-only accelerator chip). See `outputs/summary.md` for the 2026-08-02 re-verification, including a critical competitor (Theseus) that changes the differentiation claim.
