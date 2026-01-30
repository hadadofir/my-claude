# Prototype Planning - Hardware Selection Guide

> Recommended hardware for neuromorphic VIO accelerator development

**Generated**: 2026-01-26
**Goal**: Get to working prototype with minimal cost and time

---

## Quick Recommendation

| Component | Choice | Price | Why |
|-----------|--------|-------|-----|
| **FPGA Board** | AMD Kria KV260 | $249 | Best price/performance, MIPI support, Prophesee compatible |
| **Event Camera** | Prophesee CCAM5 module | ~$500 | Direct MIPI to FPGA, HD resolution |
| **IMU** | Bosch BMI088 | ~$15 | 6-axis, drone-grade |
| **Total** | | ~$800 | Minimal viable prototype |

---

## Development Phases

```
Phase 1: Algorithm Development (Software)
├── PC + Prophesee EVK4 USB ($1,500)
├── Develop algorithms in Python/C++
├── Use ESVO2 open source as starting point
└── Duration: 2-3 months

Phase 2: FPGA Prototyping
├── Kria KV260 + CCAM5 module ($750)
├── Port front-end to RTL (FAST, optical flow)
├── Keep back-end on ARM cores
└── Duration: 4-6 months

Phase 3: Full Integration
├── Custom carrier board or higher-end FPGA
├── Full pipeline in hardware
├── Power/latency optimization
└── Duration: 3-6 months
```

---

## FPGA Board Options

### Tier 1: Entry-Level ($200-400)

#### AMD Kria KV260 Vision AI Starter Kit ⭐ RECOMMENDED

| Spec | Value |
|------|-------|
| **Price** | $249 |
| **FPGA** | Zynq UltraScale+ (K26 SOM) |
| **CPU** | Quad-core ARM Cortex-A53 |
| **RAM** | 4GB DDR4 |
| **MIPI** | Yes (RPi connector) |
| **Video Codec** | H.264/H.265 |

**Pros**:
- Best-selling AMD MPSoC platform
- Direct Prophesee support (official starter kit)
- Rich ecosystem, tutorials, Vitis AI
- Production path (K26 SOM is production-ready)

**Cons**:
- FPGA fabric is modest (~250K LUTs)
- May need upgrade for full VIO pipeline

**Buy**: [AMD.com](https://www.amd.com/en/products/system-on-modules/kria/k26/kv260-vision-starter-kit.html)

---

#### ZUBoard 1CG

| Spec | Value |
|------|-------|
| **Price** | $159 |
| **FPGA** | Zynq UltraScale+ ZU1CG |
| **CPU** | Dual-core ARM Cortex-A53 |
| **RAM** | 1GB DDR4 |

**Pros**: Cheapest entry point

**Cons**: Very limited FPGA resources, no MIPI

**Verdict**: Too limited for VIO development

---

### Tier 2: Mid-Range ($500-1,500)

#### ALINX AXU4EV-P

| Spec | Value |
|------|-------|
| **Price** | ~$800 |
| **FPGA** | Zynq UltraScale+ XCZU4EV |
| **Video** | 4K H.264/H.265 codec |
| **Focus** | Video processing, ADAS |

**Pros**: More FPGA resources, video codec

**Cons**: Chinese vendor, limited support

---

#### Topic UAV & Robotics Platform

| Spec | Value |
|------|-------|
| **Price** | ~$1,200 |
| **FPGA** | Zynq UltraScale+ |
| **Extras** | GPS, WiFi/BT, Bosch IMU, motor I/O |
| **Software** | ROS, PX4 support |

**Pros**: Complete UAV development platform, sensors included

**Cons**: May be overkill for initial prototyping

---

### Tier 3: High-End ($1,500+)

#### Genesys-ZU (Digilent)

| Spec | Value |
|------|-------|
| **Price** | $1,995 |
| **FPGA** | Zynq UltraScale+ ZU5EV |
| **Resources** | 500K+ LUTs |

**Pros**: Full VIO pipeline fits easily

**Cons**: Expensive for prototyping

---

### Comparison Table

| Board | Price | LUTs | BRAM | MIPI | Best For |
|-------|-------|------|------|------|----------|
| **Kria KV260** | $249 | ~250K | 144 Mb | Yes | Initial prototype |
| ZUBoard 1CG | $159 | ~25K | 36 Mb | No | Learning only |
| ALINX AXU4EV | ~$800 | ~350K | 200 Mb | Yes | Mid-stage |
| Topic UAV | ~$1,200 | ~250K | 144 Mb | Yes | Full UAV integration |
| Genesys-ZU | $1,995 | ~500K | 288 Mb | Yes | Full pipeline |

**Recommendation**: Start with **Kria KV260**. Upgrade to AXU4EV or custom board only after front-end works.

---

## Event Camera Options

### Option 1: Prophesee EVK4 HD (USB) - For Algorithm Development

| Spec | Value |
|------|-------|
| **Price** | ~$1,500 |
| **Sensor** | Sony IMX636 |
| **Resolution** | 1280 x 720 |
| **Interface** | USB 3.0 |
| **Dynamic Range** | >120 dB |
| **Size** | 30 x 30 x 36 mm |
| **Weight** | 40g |

**Use Case**: Algorithm development on PC before FPGA port

**Pros**: Plug-and-play, full SDK support

**Cons**: USB interface not ideal for FPGA

---

### Option 2: Prophesee CCAM5 Module (MIPI) - For FPGA Integration ⭐ RECOMMENDED

| Spec | Value |
|------|-------|
| **Price** | ~$500 (estimate) |
| **Sensor** | IMX636 or GenX320 |
| **Interface** | MIPI CSI-2 |
| **Size** | 30 x 30 mm PCB |

**Use Case**: Direct FPGA integration via Kria KV260

**Pros**: Native MIPI, no USB overhead, Prophesee provides RTL examples

**Cons**: Requires FPGA development

---

### Option 3: Prophesee GenX320 Starter Kit (RPi5)

| Spec | Value |
|------|-------|
| **Price** | ~$200 (estimate) |
| **Sensor** | GenX320 |
| **Resolution** | 320 x 320 |
| **Interface** | MIPI CSI-2 |
| **Target** | Raspberry Pi 5 |

**Use Case**: Very low cost experimentation

**Pros**: Cheapest entry

**Cons**: Low resolution, may not support VIO well

---

### Option 4: iniVation DAVIS 346

| Spec | Value |
|------|-------|
| **Price** | ~$3,000 |
| **Resolution** | 346 x 260 |
| **Special** | Hybrid: events + standard frames |

**Use Case**: Research, hybrid event+frame algorithms

**Pros**: Can fallback to frames when events sparse

**Cons**: Expensive, lower resolution than Prophesee

---

### Comparison

| Camera | Price | Resolution | Interface | VIO Suitability |
|--------|-------|------------|-----------|-----------------|
| EVK4 HD | ~$1,500 | 1280x720 | USB | Algorithm dev |
| **CCAM5** | ~$500 | 1280x720 | MIPI | **FPGA integration** |
| GenX320 Kit | ~$200 | 320x320 | MIPI | Experimentation |
| DAVIS 346 | ~$3,000 | 346x260 | USB | Research |

---

## IMU Selection

### Bosch BMI088 ⭐ RECOMMENDED

| Spec | Value |
|------|-------|
| **Price** | ~$15 |
| **Axes** | 6 (3-axis accel + 3-axis gyro) |
| **Gyro Range** | ±2000°/s |
| **Accel Range** | ±24g |
| **Interface** | SPI / I2C |
| **Used By** | PX4, many drones |

**Why**: Industry standard for drones, well-documented, PX4 drivers available.

---

### Alternatives

| IMU | Price | Notes |
|-----|-------|-------|
| InvenSense ICM-42688 | ~$10 | Good, newer |
| STMicro ISM330 | ~$12 | Automotive grade |
| Analog Devices ADIS16470 | ~$200 | Tactical grade, overkill for prototype |

---

## Development Software Stack

### Phase 1: Algorithm Development

```
┌─────────────────────────────────────────────────────────┐
│                    PC Development                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Prophesee Metavision SDK (Python/C++)                  │
│  ├── Event stream handling                              │
│  ├── Visualization tools                                │
│  └── Sample algorithms                                  │
│                                                         │
│  ESVO2 (Open Source)                                    │
│  ├── Event-based stereo VIO reference                   │
│  ├── ROS integration                                    │
│  └── Modify for mono + IMU                              │
│                                                         │
│  OpenCV + Eigen                                         │
│  ├── Matrix operations                                  │
│  └── Visualization                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: FPGA Development

```
┌─────────────────────────────────────────────────────────┐
│                    FPGA Development                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  AMD Vivado                                             │
│  ├── RTL design and simulation                          │
│  ├── IP integrator for SoC                              │
│  └── Free WebPACK edition sufficient for KV260          │
│                                                         │
│  AMD Vitis                                              │
│  ├── ARM software development                           │
│  ├── Acceleration library                               │
│  └── AI tools (optional)                                │
│                                                         │
│  Prophesee FPGA Resources                               │
│  ├── MIPI receiver RTL                                  │
│  ├── Event stream parsing                               │
│  └── Reference applications                             │
│                                                         │
│  PetaLinux                                              │
│  └── Linux BSP for Zynq UltraScale+                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Recommended Purchase Order

### Immediate (Algorithm Development)

| Item | Price | Source |
|------|-------|--------|
| Prophesee EVK4 HD | ~$1,500 | Prophesee.ai |
| High-performance PC (if needed) | ~$2,000 | - |
| **Subtotal** | **~$3,500** | |

**Goal**: Develop and validate event-based VIO algorithms in software.

---

### Month 2-3 (FPGA Prototyping)

| Item | Price | Source |
|------|-------|--------|
| AMD Kria KV260 | $249 | AMD.com, DigiKey |
| Prophesee CCAM5 (MIPI) | ~$500 | Prophesee.ai |
| BMI088 breakout board | ~$30 | SparkFun, Adafruit |
| Cables, adapters | ~$50 | - |
| **Subtotal** | **~$830** | |

**Goal**: Port front-end (FAST, optical flow) to FPGA.

---

### Month 6+ (Full Integration)

| Item | Price | Source |
|------|-------|--------|
| Higher-end FPGA (if needed) | $800-2,000 | - |
| Custom carrier board (optional) | $5,000-10,000 | PCB fab |
| Drone frame for testing | ~$500 | - |
| **Subtotal** | **~$6,000-12,500** | |

**Goal**: Complete pipeline, power optimization, real-world testing.

---

## Total Budget Estimate

| Phase | Duration | Budget |
|-------|----------|--------|
| Algorithm Development | 2-3 months | ~$3,500 |
| FPGA Prototyping | 4-6 months | ~$1,000 |
| Full Integration | 3-6 months | ~$10,000 |
| **Total** | **9-15 months** | **~$15,000** |

This is for hardware only. Engineering time is separate.

---

## Quick Start Path

```
Week 1-2:
├── Order Prophesee EVK4 HD
├── Install Metavision SDK
└── Run sample applications, understand event data

Week 3-8:
├── Clone ESVO2 repository
├── Modify for mono camera + IMU
├── Profile computational bottlenecks
└── Identify exactly what to accelerate

Week 9-10:
├── Order Kria KV260 + CCAM5
├── Set up Vivado environment
└── Run Prophesee FPGA examples

Week 11-20:
├── Implement FAST corner detection in RTL
├── Implement optical flow in RTL
├── Validate against software reference
└── Measure power, latency

Week 21+:
├── Integrate with VIO back-end (ARM or RTL)
├── Real-world testing
└── Iterate
```

---

## Sources

- [AMD Kria KV260](https://www.amd.com/en/products/system-on-modules/kria/k26/kv260-vision-starter-kit.html)
- [Prophesee EVK4](https://www.prophesee.ai/event-camera-evk4/)
- [Prophesee FPGA Starter Kit](https://docs.prophesee.ai/stable/hw/evk/evk4.html)
- [ESVO2 GitHub](https://github.com/NAIL-HNU/ESVO2)
- [Topic UAV Platform](https://linuxgizmos.com/drone-controller-board-runs-linux-on-zynq-ultrascale/)
