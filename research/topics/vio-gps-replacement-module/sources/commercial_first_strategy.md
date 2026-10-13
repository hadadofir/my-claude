# Commercial-First Strategy Analysis

**Date**: 2026-01-25
**Context**: No defense contacts, commercial-first preferred, flexible on product vs IP licensing

---

## Commercial Drone Market Overview

| Metric | Value |
|--------|-------|
| Global commercial drone market (2025) | $38.2B |
| Projected (2034) | $189.9B |
| Drone sensor shipments growth (2025-2036) | 4x |
| Key trend | Higher sensor density, more autonomy |

### High-Growth Segments
1. **Warehouse/logistics** - Inventory management, last-mile delivery
2. **Infrastructure inspection** - Power lines, pipelines, bridges
3. **Agriculture** - Crop monitoring, precision spraying
4. **BVLOS operations** - Beyond visual line of sight becoming legal/common

---

## Existing Compute Platforms

### ModalAI VOXL 2 (Qualcomm)
- **Weight**: 16g
- **AI**: 15 TOPS NPU
- **VIO**: Software-based on main processor
- **Position**: Blue UAS compliant, US-made
- **Investors**: Qualcomm, DoD

### NVIDIA Jetson (Orin Nano/NX)
- **AI**: 40-100 TOPS
- **Weight**: 314g (TX2 SOM alone, needs dev kit + flight controller)
- **Position**: Powerful but heavy/power-hungry
- **VIO**: GPU-accelerated (cuVSLAM)

### Raspberry Pi + Flight Controller
- **Cost**: $35+
- **AI**: Limited, needs external accelerator
- **Position**: Hobbyist/educational

---

## Case Study: Corvus Robotics

**What they built:**
- World's first fully autonomous warehouse drone
- 14 cameras + AI navigation
- GPS-denied, no WiFi beacons needed
- LiDAR + visual sensors + neural networks
- Deployed in 1-week at 1M sq ft facilities

**Key insight**: "First in the world to ship learning-based autonomy stack for indoor aerial robot using ML and neural network approaches"

**Recent**: Partnered with Honeywell for barcode decoding software

**What this tells us**:
- GPS-denied navigation is ALREADY a commercial product
- The value is in software/algorithms, not just hardware
- Integration with enterprise systems (Honeywell) matters

---

## Opportunity Refinement

### What the market needs (commercial)

| Need | Why | Current Solution |
|------|-----|------------------|
| Longer flight time | Battery is the constraint | More efficient compute |
| Robust navigation | Warehouses, urban canyons, indoors | VIO/SLAM in software |
| Multi-camera processing | 360° obstacle avoidance | CPU/GPU, power hungry |
| Real-time mapping | SLAM for unknown environments | CPU/GPU |
| Edge AI inference | Object detection, barcode reading | NPU/GPU |

### Where hardware acceleration helps

1. **VIO/SLAM** - Currently runs on main CPU, competes for cycles
   - Offload to dedicated accelerator = more headroom for AI
   - Lower latency = more responsive flight

2. **Optical flow** - Feature tracking across frames
   - ST VD56G3 sensor has on-chip optical flow
   - But limited to one sensor, not multi-camera

3. **Depth estimation** - Stereo matching, monocular depth
   - Compute-intensive, critical for obstacle avoidance

4. **Loop closure** - SLAM relocalization when returning to known area
   - Computationally expensive, often skipped on embedded

---

## Refined Opportunity: VIO/SLAM Acceleration IP

### Value Proposition
Offload VIO/SLAM from main processor to dedicated accelerator:
- **10x power efficiency** vs software on CPU
- **Lower latency** for more responsive flight
- **Frees main processor** for AI inference and application logic
- **More robust** algorithms that wouldn't fit in power budget otherwise

### Form Factors

| Option | Description | Target Customer |
|--------|-------------|-----------------|
| **FPGA IP core** | License RTL to integrate into customer's FPGA | Drone platform companies |
| **ASIC IP** | License to SoC vendors (Qualcomm, etc.) | Long-term, high volume |
| **Small module** | Plug-in accelerator for Jetson/VOXL | Drone developers |
| **Standalone chip** | Drop-in solution | Drone manufacturers |

### Technical Scope

Core VIO pipeline:
```
Camera frames → Feature extraction → Feature tracking →
IMU preintegration → State estimation → Map update
```

Acceleration targets:
1. **Feature extraction** (ORB, FAST corners) - highly parallel
2. **Feature matching** (BRIEF descriptors) - parallel compare
3. **Optical flow** - dense motion estimation
4. **Bundle adjustment** - sparse matrix operations
5. **IMU integration** - fixed-point math

### Competitive Differentiation

| Competitor | Approach | Gap |
|------------|----------|-----|
| MIT Navion | Full VIO ASIC, 2mW | Academic, not productized |
| NVIDIA cuVSLAM | GPU-accelerated | High power (10W+) |
| ModalAI VOXL | Software VIO on Qualcomm | Competes for CPU cycles |
| Qualcomm NPU | General AI accelerator | Not optimized for VIO |
| ST VD56G3 | On-sensor optical flow | Single sensor, limited |

**Our position**: Production-ready VIO acceleration IP that:
- Runs full SLAM pipeline at <1W
- Integrates with existing platforms (VOXL, Jetson)
- Supports multi-camera configurations
- Has defense-grade path for later

---

## Go-to-Market Strategy

### Phase 1: FPGA IP (Year 1-2)
- Develop optimized VIO IP for Xilinx Zynq / Intel Cyclone
- Target drone platform companies (ModalAI competitors)
- License fee + royalty model
- Build reference designs, benchmark data

### Phase 2: Module Product (Year 2-3)
- Small FPGA-based module that plugs into Jetson/VOXL
- Sell direct to drone developers
- $100-300 price point
- Prove market demand and volume

### Phase 3: ASIC (Year 3-5, if volume justifies)
- Convert proven IP to ASIC
- Target 100K+ units/year market
- Approach defense market with proven commercial solution

---

## Target Customers (Commercial)

### Platform Companies
- **ModalAI** - Could integrate into future VOXL
- **Auterion** - Enterprise drone software
- **Skydio** - US-based, autonomous drones

### Application Companies
- **Corvus Robotics** - Warehouse drones (may build own platform)
- **Zipline** - Delivery drones
- **Flyability** - Inspection drones (GPS-denied specialist)

### Defense (Later)
- **Shield AI** - Autonomous drones, GPS-denied focus
- **AeroVironment** - Small tactical drones
- **GA-ASI** - Larger platforms

---

## Business Model Options

### Option A: Pure IP Licensing
- License RTL to platform companies
- $50K-200K upfront + $1-5 royalty per unit
- Low capital, high margin, slower growth
- Risk: Customer may build internal alternative

### Option B: Module Product
- Sell hardware module to drone developers
- $100-300 per unit, 50%+ gross margin
- Requires manufacturing, support
- More capital intensive but builds brand

### Option C: Hybrid
- IP licensing to big players (Qualcomm, NVIDIA)
- Module sales to smaller developers
- Reference designs free/low cost to drive adoption

---

## Key Risks

| Risk | Mitigation |
|------|------------|
| Qualcomm/NVIDIA builds this internally | Move fast, establish relationships, offer better PPA |
| Market stays on software solutions | Focus on use cases where power/latency matter most |
| FPGA too expensive vs software | Target premium segment where efficiency = longer flight |
| Algorithms evolve, IP becomes stale | Continuous R&D, version updates, FPGA reconfigurability |

---

## What Would Make This Succeed

1. **10x better PPA** than software on same workload
2. **Easy integration** with existing platforms
3. **Reference designs** that just work
4. **Benchmark data** proving the value
5. **Strategic partnership** with one platform vendor

---

## Sources

- [ModalAI VOXL 2](https://www.modalai.com/products/voxl-2)
- [Top 5 Companion Computers for UAVs](https://www.modalai.com/blogs/blog/top-5-companion-computers-for-uavs)
- [Corvus Robotics MIT News](https://news.mit.edu/2024/corvus-autonomous-drones-precisely-track-warehouse-inventories-1220)
- [SLAM for GPS-Denied Navigation](https://xray.greyb.com/drones/slam-gps-denied-navigation)
- [Commercial Drone Market Forecast](https://www.heliguy.com/blogs/posts/global-drone-market-forecast-147-billion-2036/)
- [BVLOS Future 2026](https://uavcoach.com/inside-bvlos/)
