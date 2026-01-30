# Competitive Deep Dive v2 - Neuromorphic & Edge AI for VIO

> Updated analysis: neuromorphic players, new entrants, and non-neuromorphic competitors
> Supersedes: `competitive_deep_dive.md`

**Updated**: 2026-01-27
**Sources**: Web research Jan 2026 + prior analysis

---

## Executive Summary

| Competitor | Can Do VIO? | Power | Commercial? | Event Camera? | Threat |
|-----------|------------|-------|-------------|---------------|--------|
| **SynSense Speck** | No (128x128) | <5 mW | Yes | Built-in, low-res | Low |
| **BrainChip Akida** | No (wrong arch) | <1W | IP licensing | No | Low |
| **Intel Loihi 2/3** | Research demos | ~1W | No | Research only | None |
| **Innatera T1** | No | sub-mW | Early | No | None |
| **Hailo-8** | Partial (CNN only) | 2.5W | Yes, volume | No | Medium |
| **Qualcomm RB5** | Yes (full) | 5-10W | Yes | No | **High** (power gap) |
| **NVIDIA Orin Nano** | Yes (full) | 7-15W | Yes | No | **High** (power gap) |
| **Lattice FPGA** | Custom RTL | 0.5-2W | Yes | Possible | **Medium** (DIY) |
| **MIT Navion** | Yes (designed for it) | 2 mW | No (academic) | No | Validates market |

**Bottom line**: No commercial product exists for low-power (<1W) VIO with event camera support. The neuromorphic hype has NOT translated into VIO-capable products. The real competition is Qualcomm/NVIDIA driving power down in general-purpose platforms.

---

## 1. SynSense (Zurich/Shanghai)

### Latest Developments (2025-2026)

**Major news**: SynSense acquired **iniVation AG** (Switzerland) in February 2024, merging event camera sensors (DAVIS/DVS) with neuromorphic processing. This creates the most vertically integrated neuromorphic vision company.

**Partnership with Prophesee**: Co-developing single-chip event sensor integrating Prophesee's Metavision sensor with SynSense's DYNAP-CNN processor. Still demo-stage, not volume production.

**Funding**: $10M Pre-B+ round (2023, led by Ausvic Capital). Total raised ~$30M+.

### Product Line

| Product | Status | Specs | Power | VIO Relevance |
|---------|--------|-------|-------|---------------|
| **Speck (SNN51)** | Shipping | 128x128 DVS + 328K SNN neurons | <5 mW | **Too low resolution** |
| **Speck 2E** | Announced, unclear shipping | Higher res than Speck | Low mW | Still likely insufficient |
| **Xylo (SNN71)** | Shipping | Audio-focused, 1000 neurons | ~100 uW | Irrelevant (audio) |
| **Xylo-A2** | Shipping | Analog-digital hybrid audio | Sub-100 uW | Irrelevant (audio) |

### HD Resolution Roadmap

SynSense has publicly stated plans to "move in the direction of higher resolution pixel arrays with Prophesee." However:
- They acknowledge that higher-resolution sensor + processing doesn't fit on one die
- Solution would require stacked architecture or multi-chip bonding
- **No specific HD product announced with timeline or specs**
- The iniVation acquisition gives them sensor technology but doesn't solve the processing bottleneck

### SDK Assessment

| Tool | Rating | Notes |
|------|--------|-------|
| **SINABS** (SNN training) | 4/10 for production, 6/10 for research | PyTorch-based, requires SNN expertise |
| **Samna** (hardware interface) | 4/10 | Works for dev kits, not production-grade |
| **Rockpool** | Deprecated | Legacy, replaced by SINABS |

**You need SNN PhDs to use these tools.** Not suitable for product engineering teams.

### VIO Assessment: **LOW THREAT**

The iniVation acquisition is strategically interesting but doesn't change the fundamental gap: **128x128 pixels cannot do VIO** (need 640x480+). Even if they deliver "Speck HD" at 320x320, that's still marginal. A stacked multi-chip HD solution would take 2-3 years minimum and would be expensive.

**Watch for**: CES/ISSCC 2026-2027 announcements of HD event-based SoC.

---

## 2. BrainChip (ASX: BRN)

### Latest Developments (2025-2026)

**AKD1500 tape-out**: BrainChip has begun tape-out for the AKD1500 chip. Cost: ~$2.3M. First chips expected **Q3 2026**. This is a significant milestone - first time moving beyond AKD1000.

**Financial reality check**:
- Revenue: **US$1.31M** (tiny)
- Cash burn: ~$3.8M/quarter
- ~3 quarters of runway remaining (as of late 2025)
- Multiple capital raises, volatile penny stock (market cap $200-800M AUD)
- Revenue "ramp-up" from chip sales not expected until **late 2026 at earliest**

### Licensing Deals (Verified)

| Partner | Deal | Revenue | VIO Relevance |
|---------|------|---------|---------------|
| **Frontgrade Gaisler** | IP license for SoC | EUR 150K upfront, 10% royalty | Low (space/defense SoC, not VIO) |
| **ISL** | Radar/EW processing | Undisclosed | None (radar, not vision) |
| **Arquimea** | Drone swimmer detection | Undisclosed | **Uses Prophesee camera + Akida** |
| **Blue Ridge / Parsons** | Defense edge AI | Undisclosed | Low (general edge AI, not VIO) |
| **Andes Technology** | RISC-V integration | Partnership | None (platform integration) |
| **Chelpis Quantum** | AKD1000 purchase for security robots | Small | Low |

**The Arquimea deal is notable**: it pairs Akida with Prophesee cameras for drone-based detection. But this is **classification** (detect swimmers), not VIO (estimate drone pose). Different compute problem entirely.

### Akida 2.0 / TENNs Technology

TENNs (Temporal Event Neural Networks) add temporal convolution - relevant concept for VIO's sequential data. However:
- Architecturally suited to **time-series classification**, not geometric computation
- No published VIO demo or benchmark
- No native event camera (DVS) interface
- MetaTF toolchain: **3/10 usability** - "drop-in TensorFlow replacement" claim is significantly overstated

### Skeptical View (from analysts)

> "No breakdown of licenses signed, deployments made, or customers paying real money. No timeline for production volume or evidence that a major OEM has chosen Akida for a shipping product." ([Equity.Guru](https://equity.guru/2025/11/21/brainchip-asx-brn-big-promises-marketing-slop-and-an-ai-company-that-missed-the-ai-boom/))

### VIO Assessment: **LOW THREAT**

Akida lacks the computational architecture for geometric/matrix operations central to VIO. The TENNs addition is marketing-interesting but architecturally insufficient. BrainChip's own financial survival is uncertain. Even their defense partnerships are for classification/detection, not odometry.

---

## 3. Intel Loihi

### Latest Developments (2025-2026)

**Loihi 3 announced** (January 2026): Third-generation neuromorphic processor.
- Fabricated on **4nm process**
- **8M neurons, 64B synapses** per chip (8x over Loihi 2)
- **Caution**: The announcement source is a financial content site, not an official Intel press release. Treat with skepticism until confirmed by Intel directly.

**Loihi 2 benchmarks**: 75x lower latency and 1000x higher energy efficiency vs NVIDIA Jetson Orin Nano on state-space model workloads.

**Hala Point**: Large-scale system (1,152 Loihi 2 chips, 1.15B neurons) deployed at Sandia National Labs. Research only.

**Commercialization status**: **STILL RESEARCH ONLY**. Intel states they are "progressing from research prototypes to industry-leading commercial products over the coming years." The INRC has 200+ members but no commercial purchase path exists.

### VIO Assessment: **NOT A THREAT (but validates the space)**

Cannot buy the chip. Even Loihi 3 (if real) won't be commercially available. Intel's financial pressures make the neuromorphic division's future uncertain. The impressive benchmarks actually **validate your thesis** - neuromorphic processing for navigation IS dramatically more efficient, but nobody is selling it.

---

## 4. New Entrants

### Innatera (Delft, Netherlands)

| Attribute | Value |
|-----------|-------|
| Technology | Analog neuromorphic processor |
| Product | T1 processor |
| Status | Sampling/early access |
| Power | Sub-milliwatt |
| Funding | ~$15M+ |
| VIO Relevance | **VERY LOW** |

Focused on always-on sensor wake-up (audio, radar, simple vision). Analog approach limits the precision needed for geometric VIO computation.

### GrAI Matter Labs

**Acquired by BrainChip (~2024)**. GrAI One chip (NeuronFlow architecture) was actually one of the more VIO-relevant neuromorphic chips (real-time vision processing at edge). Standalone product likely discontinued. **Dead end** unless BrainChip integrates into Akida 3.0.

### Rain AI (San Francisco)

Analog in-memory computing. ~$40M+ funded (Sam Altman was early investor). **No shipping silicon.** Product timeline extremely delayed. Even if they ship, it's a general AI accelerator. **Vaporware.**

### Ceremorphic

Analog mixed-signal AI, targeting **data center**, not edge. Irrelevant to VIO.

### Chinese Neuromorphic

| Company | Status | Concern |
|---------|--------|---------|
| **Lynxi (灵汐科技)** | KA200 shipping in China | Export controls, general-purpose |
| **Tsinghua Tianjic** | Academic | No product |
| Various university spinoffs | Pre-product | None relevant to VIO |

Export control complications. Primarily domestic Chinese market. None have VIO capability.

### MIT Navion - The Benchmark

| Attribute | Value |
|-----------|-------|
| Power | **2 mW** |
| Resolution | 752x480 stereo |
| Architecture | 171K gate equivalent |
| Published | 2018 (JSSC) |
| Commercialized | **NO** |
| Spinoff | **None found** (verified Jan 2026) |

**This is the single most relevant piece of prior art.** Prof. Vivienne Sze's group proved a full VIO pipeline can run at 2mW. Five years later, nobody has commercialized it. No spinoff company, no licensing deals.

**This IS the opportunity**: take the Navion architectural concepts and bring them to market.

---

## 5. Non-Neuromorphic Competitors

### Hailo

| Product | Status | Power | TOPS | Price |
|---------|--------|-------|------|-------|
| **Hailo-8** | Volume shipping | 2.5W | 26 | $40-70 |
| **Hailo-8L** | Shipping | ~1.5W | 13 | $20-40 |
| **Hailo-10H** | Shipping | TBD | GenAI focus | TBD |
| **Hailo-15** | Shipping (smart cameras) | TBD | Vision processor | TBD |

**Drone deployment**: Demonstrated at CES 2025 - drone with Hailo-8 doing real-time face detection/people counting. But this is **inference** (CNN), not VIO. Hailo cannot do pose estimation, IMU integration, or geometric backend. Needs companion CPU for anything beyond detection.

**Hailo-15** is focused on smart cameras/security, not drones. No event camera support.

**Threat level: MEDIUM** - Could handle the neural network portion of learned VIO but not the geometric backend. Not a complete VIO solution.

### Qualcomm RB5/RB7

| Product | Status | Power | Price |
|---------|--------|-------|-------|
| **RB5 (QRB5165)** | Mature, shipping | 5-10W | ~$200 module |
| **RB7** | Announced | Similar | TBD |

**This is the current default for drone VIO.** Many drone companies use Qualcomm with its own VIO library (from Snapdragon Flight heritage). Integrated ISP, GPU, DSP (Hexagon), CPU - can run full VIO pipeline.

**The gap**: 5-10W is too much for micro-drones (<100g). $150-200+ module cost. No event camera support. Overkill (runs Android/Linux).

**SDK**: 6/10. Powerful but complex. Hexagon DSP programming is notoriously difficult. NDAs required.

**Threat level: HIGH for larger drones, LOW for micro-drones.** The power gap is your wedge.

### NVIDIA Jetson Orin Nano

| Product | Status | Power | TOPS | Price |
|---------|--------|-------|------|-------|
| **Orin Nano 4GB** | Shipping | 7-15W | 20 | $199 |
| **Orin Nano 8GB** | Shipping | 7-15W | 40 | $299 |
| **Orin NX** | Shipping | 10-25W | 70-100 | $399-599 |

**Best SDK in the space**: Isaac ROS includes cuVSLAM, CUDA ecosystem, massive developer community. Can run state-of-the-art learned VIO (DPVO, DROID-SLAM).

**The gap**: 7-15W minimum. Module + carrier is large and heavy. Needs heatsink/fan. **Power is disqualifying for micro/mini drones.** No event camera support.

**Threat level: HIGH for large drones/robots, NONE for micro-drones.**

### Lattice Semiconductor

| Product | LUTs | Power | MIPI | Price (chip) |
|---------|------|-------|------|-------------|
| **CrossLink-NX (LIFCL-40)** | 39.6K | 50-200 mW | **Best native** | $8-15 |
| **CertusPro-NX (LFCPNX-100)** | 97K | 0.5-2W | Hardened | $30-50 |
| **Avant (mid-range)** | Varies | 0.5-2W | Yes | $20-50 |

**SDK**: 7/10 - Lattice Radiant + sensAI/mVision are mature. Standard FPGA development.

**Assessment**: Lattice FPGAs are the **"do-it-yourself" option** - you build VIO from RTL. CrossLink-NX has the best MIPI implementation but is too small for full VIO. CertusPro-NX has enough LUTs but insufficient BRAM.

**Key insight**: Lattice is actually your **production platform**, not your competitor. A VIO IP running on Lattice FPGAs is a viable product. CrossLink-NX as MIPI front-end + CertusPro or Avant for compute is a realistic architecture.

**Threat level: MEDIUM** - anyone could build VIO on Lattice, but nobody has. The RTL development is the barrier.

---

## 6. Competitive Positioning Map (Updated)

```
                        FULL VIO PIPELINE
                              |
              Qualcomm RB5    |    NVIDIA Orin
              (5-10W, $200)   |    (7-15W, $199+)
                              |
                              |
                              |    YOUR OPPORTUNITY
                              |    (5-50mW, <$15)
                              |    Event camera native
                              |
              Hailo-8         |
              (2.5W, partial) |    MIT Navion (2mW, academic)
                              |
LOW POWER -------|------------|------------|-------- HIGH POWER
                              |
              Lattice FPGA    |
              (DIY, 0.5-2W)   |
                              |
              SynSense Speck  |    BrainChip Akida
              (1mW, 128x128)  |    (1W, no VIO)
                              |
                        CLASSIFICATION ONLY
```

---

## 7. Updated Risk Assessment

| Risk | Probability | Impact | Change from v1 |
|------|-------------|--------|----------------|
| Intel commercializes Loihi | LOW (Loihi 3 announced but no commercial plans) | HIGH | Unchanged |
| SynSense moves to HD | MEDIUM (iniVation acquisition helps) | MEDIUM-HIGH | **Increased** |
| Qualcomm low-power VIO DSP | MEDIUM | HIGH | Unchanged |
| BrainChip gains traction | LOW (financial struggles) | LOW | **Decreased** |
| Chinese subsidized VIO ASIC | LOW-MEDIUM | HIGH | Unchanged |
| Hailo adds VIO capability | LOW (focused on cameras/security) | MEDIUM | New |
| MIT Navion spinoff | LOW (no evidence found) | HIGH | New assessment |

---

## 8. Key Takeaways

1. **The neuromorphic competitors are NOT threats in 2026-2028.** They solve different problems at insufficient resolution/capability.

2. **SynSense + iniVation merger is the one to watch** - first company with both event sensors AND neuromorphic processing. But HD VIO is still years away for them.

3. **BrainChip is financially fragile** with minimal real revenue. Their partnerships are early-stage and defense deals are for classification, not VIO.

4. **The real competition is power-down from Qualcomm/NVIDIA** on general-purpose platforms. Your wedge is the 100x power gap for micro-drones.

5. **MIT Navion proved the concept at 2mW but nobody has commercialized it** in 5+ years. This validates both the opportunity and the difficulty.

6. **Lattice FPGAs are your platform, not your competitor.** VIO IP running on Lattice is a product.

---

## Sources

- [SynSense Products](https://www.synsense.ai/products/speck-2/)
- [SynSense/iniVation Merger - EE Times](https://www.eetimes.com/neuromorphic-developers-partner-to-integrate-sensor-processor/)
- [BrainChip AKD1500 Tape-Out](https://stocksdownunder.com/brainchip-2/)
- [BrainChip Financial Analysis - Equity.Guru](https://equity.guru/2025/11/21/brainchip-asx-brn-big-promises-marketing-slop-and-an-ai-company-that-missed-the-ai-boom/)
- [BrainChip H1 Revenue - Stockhead](https://stockhead.com.au/tech/brainchip-closes-h1-with-revenue-growth-us8-4m-loss-as-it-eyes-commercialisation-for-its-akida-ai-chip/)
- [Intel Loihi 3 Report](https://markets.financialcontent.com/wral/article/tokenring-2026-1-19-the-brain-like-revolution-intels-loihi-3-and-the-dawn-of-real-time-neuromorphic-edge-ai)
- [Intel Neuromorphic Computing](https://www.intel.com/content/www/us/en/research/neuromorphic-computing.html)
- [Hailo Drone Demo - CES 2025](https://hailo.ai/resources/industries/security/system-electronics-astrial-board-on-a-drone-platform/)
- [Hailo CES 2026](https://hailo.ai/company-overview/newsroom/events/ces-2026/)
- [MIT Navion Project](https://navion.mit.edu/)
- [Neuromorphic Market Report 2026](https://markets.financialcontent.com/bpas/article/tokenring-2026-1-9-the-silicon-brain-awakens-neuromorphic-computing-escapes-the-lab-to-power-the-edge-ai-revolution)
- [Prophesee AMD Kria Starter Kit](https://www.prophesee.ai/event-based-metavision-amd-kria-starter-kit/)
