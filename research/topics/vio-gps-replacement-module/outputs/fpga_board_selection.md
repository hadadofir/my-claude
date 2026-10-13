# FPGA Board Selection for VIO Prototyping

> Detailed board comparison for neuromorphic VIO accelerator development

**Generated**: 2026-01-27
**Decision**: AMD Kria KV260 is the clear winner

---

## Design Requirements

| Parameter | Requirement | Notes |
|-----------|-------------|-------|
| LUTs | ~80,000 | Full VIO front-end |
| BRAM | ~3 MB (24 Mbit) | Frame buffers, feature storage |
| DSPs | ~200 | Optical flow, matrix ops |
| Power | ~2W fabric target | Micro-drone budget |
| Camera I/F | MIPI CSI-2 | Prophesee event cameras |
| IMU I/F | SPI / I2C | BMI088 or similar |
| Processing | ARM cores preferred | VIO back-end, ROS2 |
| Production | SOM-based path | Commercial deployment |

---

## The Winner: AMD Kria KV260

### Why It Wins

| Factor | KV260 | Runner-up |
|--------|-------|-----------|
| **Prophesee integration** | Official starter kit exists | No other board has this |
| **FPGA resources** | 117K LUTs, 7.1 MB BRAM, 1248 DSPs | All exceed requirements |
| **Price** | ~$199-250 (kit) | Most alternatives $500+ |
| **Toolchain** | Free (Vivado Standard) | Intel Agilex needs $3K+ license |
| **Production path** | K26 SOM is production-grade | Best SOM ecosystem |
| **MIPI CSI-2** | Hardened + dedicated connector | Most boards lack connector |
| **ARM cores** | Quad A53 + Dual R5F | Best for VIO back-end |

---

## Detailed Board Comparison

### 1. AMD Kria KV260 (RECOMMENDED)

| Spec | Value |
|------|-------|
| **FPGA** | Zynq UltraScale+ XCK26 (K26 SOM) |
| **LUTs** | 117,120 (46% headroom over requirement) |
| **BRAM** | 144 Block RAMs = 5.1 MB + 64 UltraRAM = 2 MB = **7.1 MB total** |
| **DSPs** | 1,248 (6x headroom) |
| **CPU** | Quad-core ARM Cortex-A53 + Dual Cortex-R5F |
| **RAM** | 4 GB DDR4 |
| **Storage** | 16 GB eMMC + QSPI flash |
| **MIPI** | Hardened D-PHY (PS side, 4 lanes @ 1.5 Gbps) + Soft IP available |
| **Camera** | IAS connector + RPi connector (both MIPI CSI-2) |
| **Price** | Kit: ~$199-250 / K26 SOM standalone: ~$406 (commercial) / ~$562 (industrial) |
| **Vivado** | Standard Edition (free, no license required) |
| **Production** | K26 SOM in commercial (-1C) and industrial (-1I) temp grades |

**Prophesee Integration (Verified)**:
- Prophesee sells an official [Metavision AMD Kria Starter Kit](https://www.prophesee.ai/event-based-metavision-amd-kria-starter-kit/)
- Two sensor options: IMX636 (1280x720 HD) and GenX320 (320x320)
- Connects via MIPI CSI-2 through KV260 RPi interface
- Open-source resources: [LogicTronix GitHub repo](https://github.com/LogicTronixInc/Kria-Prophesee-Event-VitisAI) with Vitis AI ML applications
- AMD has an [official product page](https://www.amd.com/en/products/system-on-modules/kria/k26/kv260-vision-starter-kit/event-based-vision-starter-kit.html) for the event-based vision combo
- Prophesee provides [quickstart guide](https://www.prophesee.ai/quickstart-prophesee-metavision-starter-amd-kria-kv260/) specifically for KV260

**2025 Refresh**: AMD released a refreshed KV260 with auto-focus upgrade for enhanced vision applications. No change to FPGA resources.

**Power Estimate for VIO Design**:
- At 68% LUT utilization (80K/117K), expect ~2.5-3.5W PL power
- Slightly above 2W target, mitigate with:
  - Clock gating idle pipeline stages
  - Use UltraRAM (lower power per bit than BRAM)
  - Run PL at 150-200 MHz instead of max clock
  - In production, consider partial reconfiguration for unused blocks

**Production Carrier Board**: AMD provides full carrier card design files (schematics + layout) for both KV260 and KR260. Design custom carrier with only the interfaces you need.

---

### 2. AMD Kria KR260 Robotics Kit

| Spec | Value |
|------|-------|
| **FPGA** | Same K26 SOM (identical resources) |
| **Differentiators** | 4x GbE (TSN), ROS 2 focus, motor control I/O |
| **MIPI** | Hardened (on SOM), but **no MIPI camera connector on carrier** |
| **Price** | ~$350 |

**Verdict: Choose KV260 over KR260.** The lack of dedicated MIPI camera connectors is a deal-breaker for vision work. Same SOM, worse carrier for your use case.

---

### 3. AMD Kria K24 SOM (KD240 Kit)

| Spec | Value |
|------|-------|
| **FPGA** | Zynq UltraScale+ ZU3EG-equivalent |
| **LUTs** | 70,560 |
| **BRAM** | 0.9 MB (no UltraRAM) |
| **DSPs** | 360 |
| **CPU** | Dual A53 + Dual R5F |
| **RAM** | 2 GB DDR4 |
| **MIPI** | Hardened D-PHY on PS |
| **Price** | K24 SOM: ~$150-200, KD240 kit: ~$250 |
| **Kit Focus** | Motor/drives, not vision |

**Verdict: DOES NOT MEET REQUIREMENTS.**
- LUTs: 70K vs 80K needed = 12% short
- BRAM: 0.9 MB vs 3 MB needed = **severely insufficient**
- Connector-compatible with K26, so could theoretically migrate UP to K26 on same carrier
- The KD240 carrier has no MIPI camera connector

**Only useful if**: You need a cheap learning platform before committing to KV260.

---

### 4. Lattice CrossLink-NX / CertusPro-NX

#### CrossLink-NX (LIFCL-40)

| Spec | Value |
|------|-------|
| **LUTs** | 39,600 |
| **BRAM** | EBR: 0.34 MB + LRAM: 0.31 MB = **0.65 MB** |
| **DSPs** | 56 |
| **MIPI** | **Best-in-class hardened D-PHY + CSI-2** (4 lanes, 2.5 Gbps/lane) |
| **ARM** | None |
| **Price** | Dev board ~$100-150, chip $8-15 in volume |
| **Toolchain** | Lattice Radiant (free) |

#### CertusPro-NX (LFCPNX-100)

| Spec | Value |
|------|-------|
| **LUTs** | 97,000 |
| **BRAM** | EBR: 0.56 MB + LRAM: 1.25 MB = **1.81 MB** |
| **DSPs** | 156 |
| **MIPI** | Hardened D-PHY |
| **ARM** | None |
| **Price** | Dev board ~$200-300, chip $30-50 in volume |
| **Toolchain** | Lattice Radiant (free) |

**Verdict: Not standalone VIO platforms** (insufficient BRAM, no ARM cores). But CrossLink-NX is the **best MIPI bridge chip** available. Consider for production architecture:

```
Prophesee Camera (MIPI) -> CrossLink-NX (deserialize, filter) -> Main SoC FPGA (VIO compute)
```

This splits the MIPI interface cleanly at ~0.3W additional power.

---

### 5. Intel/Altera Agilex 5

| Spec | Value |
|------|-------|
| **FPGA** | Agilex 5 E-Series SoC variants |
| **LUTs** | 50K to 400K+ |
| **CPU** | Quad A55 + A76 (faster than Zynq A53) |
| **MIPI** | Some variants have hardened MIPI |
| **Price** | Dev kit $500-1000+ |
| **Toolchain** | **Quartus Prime Pro: ~$3,000+/year** |
| **Production** | Thin SOM ecosystem |

**Verdict: Technically capable but POOR ecosystem fit.**
- Expensive toolchain is a significant barrier
- Immature ecosystem for vision
- No Prophesee integration
- Limited dev board availability (still ramping)
- Only consider if you already have deep Intel FPGA expertise

---

### 6. Microchip PolarFire SoC (Icicle Kit)

| Spec | Value |
|------|-------|
| **FPGA** | MPFS250T |
| **LUTs** | 254,000 (massive headroom) |
| **BRAM** | ~1.5-2 MB (different memory architecture) |
| **Math Blocks** | 784 (~392 DSP48-equivalent) |
| **CPU** | **4x SiFive U54 RISC-V + 1x E51 monitor** |
| **RAM** | 2 GB LPDDR4 |
| **MIPI** | **None hardened** (requires external bridge) |
| **Price** | Icicle Kit ~$499 |
| **Toolchain** | Libero SoC (free, no restrictions) |
| **Special** | Flash-based FPGA (instant-on, inherently secure) |

**Advantages**:
- Non-volatile fabric: no bitstream loading, better security (defense appeal)
- Low power design: potentially closer to 2W target
- RISC-V: no ARM licensing (long-term cost advantage)
- Built-in hardware security module

**Disadvantages**:
- BRAM: 1.5-2 MB vs 3 MB needed = **insufficient** (borderline)
- No MIPI: must add CrossLink-NX or TI DS90UB954 bridge
- RISC-V ecosystem less mature for Prophesee SDK, ROS2
- No known Prophesee integration examples

**Verdict: Interesting for production (defense appeal, flash-based, low power) but higher risk for prototyping.** Consider as production platform AFTER proving design on KV260.

---

### 7. Enclustra Mercury+ XU5 SOM

| Spec | Value |
|------|-------|
| **FPGA** | ZU5EV (same die as K26) |
| **Resources** | Identical to K26: 117K LUTs, 7.1 MB BRAM, 1248 DSPs |
| **CPU** | Quad A53 + Dual R5F |
| **RAM** | Up to 4 GB DDR4 |
| **Price** | SOM: ~$500-700, Base board: ~$400-600 |
| **MIPI** | Routed to SOM pins, carrier must implement connector |
| **Production** | European supplier, 10+ year availability guarantee |

**Verdict: Viable alternative to Kria if you need European supply chain or custom form factor.** Same silicon, 2-3x the cost, less vision-specific ecosystem. The PE1 base board does NOT have MIPI camera connectors.

---

### 8. ALINX AXU4EV-P / AXU5EV-P

| Board | FPGA | LUTs | Price |
|-------|------|------|-------|
| **AXU4EV-P** | ZU4EV | ~87,360 | ~$500-800 |
| **AXU5EV-P** | ZU5EV | 117,120 | ~$600-900 |

**Pros**: More FPGA resources per dollar than Enclustra
**Cons**: Chinese vendor, documentation in Chinese (variable English quality), no production SOM, limited support, ships from China (1-3 weeks)

**Verdict: Budget prototyping option only.** No production path. Choose if you're already comfortable with Chinese FPGA boards and want more resources on the cheap. For anything serious, use KV260.

---

### 9. Other Options (Not Recommended)

| Board | Why Not |
|-------|---------|
| **Efinix Ti180** | 180K LUTs but only 1.25 MB BRAM, no ARM cores, immature tools |
| **Gowin GW5A-138** | 0.8 MB BRAM, no ARM, immature ecosystem, China supply chain |
| **AMD Versal VEK280** | $3,000+, massive overkill |
| **Intel Cyclone V** | Legacy, insufficient BRAM/DSPs, no MIPI, EOL trajectory |

---

## Summary Comparison

| Board | LUTs | BRAM (MB) | DSPs | ARM | MIPI Connector | Price | Free Tools | Prophesee | Production | **Score** |
|-------|------|-----------|------|-----|---------------|-------|------------|-----------|------------|-----------|
| **Kria KV260** | **117K** | **7.1** | **1248** | **4xA53** | **Yes** | **$199-250** | **Yes** | **Official kit** | **Excellent** | **10/10** |
| PolarFire SoC | 254K | ~1.5-2 | 784 | 4xU54 RV | No | $499 | Yes | No | Good (defense) | 5/10 |
| Enclustra XU5 | 117K | 7.1 | 1248 | 4xA53 | No | $900-1100 | Yes | Possible | Excellent (EU) | 5/10 |
| Agilex 5 SoC | Varies | Varies | 100s | A55+A76 | Some | $500-1000 | No ($3K+) | No | Weak | 3/10 |
| ALINX AXU5EV | 117K | 7.1 | 1248 | 4xA53 | Maybe | $600-900 | Yes | No | None | 4/10 |
| KR260 | 117K | 7.1 | 1248 | 4xA53 | No | $350 | Yes | Possible | Excellent | 6/10 |
| K24 / KD240 | 70K | 0.9 | 360 | 2xA53 | No carrier | $200-250 | Yes | No | Good | 2/10 |
| CertusPro-NX | 97K | 1.81 | 156 | None | Yes | $200-300 | Yes | No | Bridge only | 3/10 |

---

## Recommended Purchase Plan

### Immediate: Algorithm + FPGA Prototype

| Item | Price | Source | Notes |
|------|-------|--------|-------|
| **AMD Kria KV260** | ~$250 | [DigiKey](https://www.digikey.com/en/products/detail/amd/SK-KV260-G/13985269), Mouser, AMD.com | In stock |
| **Prophesee Metavision Kria Kit (IMX636)** | ~$500-1000 | [Prophesee](https://www.prophesee.ai/event-based-metavision-amd-kria-starter-kit/) | HD event camera + MIPI adapter |
| **BMI088 breakout** | ~$30 | SparkFun/Adafruit | SPI IMU |
| **Cables/adapters** | ~$50 | - | MIPI, PMOD, USB |
| **Total** | **~$830-1,330** | | |

### Alternative: Separate Algorithm Dev + FPGA

| Item | Price | Notes |
|------|-------|-------|
| Prophesee EVK4 HD (USB) | ~$1,500 | Algorithm dev on PC first |
| AMD Kria KV260 | ~$250 | FPGA port later |
| Prophesee CCAM5 (MIPI) | ~$500 | FPGA integration |
| **Total** | **~$2,250** | Higher cost but more flexible |

### Production Path

```
Prototype:  KV260 + Prophesee Kria Kit
    |
    v
Custom Carrier: K26 SOM + custom PCB (design files from AMD)
    |
    v
Production: K26 SOM (commercial/industrial grade)
    OR
    PolarFire SoC (if defense/security features needed)
    OR
    Custom ASIC (if volume > 10K units/year)
```

---

## Immediate Next Steps

1. **Purchase KV260** from DigiKey/Mouser (~$250, in stock)
2. **Contact Prophesee** about Metavision Kria Starter Kit (IMX636 variant)
   - Check if academic pricing applies (20% off for research orgs)
   - Request access to FPGA reference designs and RTL examples
3. **Install Vivado Standard** + Vitis + PetaLinux (all free)
4. **Clone LogicTronix repo** for Prophesee + KV260 integration examples
5. **Run Vivado Power Estimator (XPE)** with your VIO RTL utilization estimates to get precise power numbers for ZU5EV
6. **Begin VIO front-end RTL** targeting K26 fabric (FAST corners, optical flow)

---

## Sources

- [AMD Kria KV260 Product Page](https://www.amd.com/en/products/system-on-modules/kria/k26/kv260-vision-starter-kit.html)
- [AMD Kria KV260 Refresh Blog (2025)](https://www.amd.com/en/blogs/2025/kria-kv260-vision-ai-starter-kit-refresh.html)
- [AMD Kria SOMs Portfolio](https://www.amd.com/en/products/system-on-modules/kria.html)
- [AMD Kria K24 SOM](https://www.amd.com/en/products/system-on-modules/kria/k24.html)
- [Prophesee Metavision AMD Kria Starter Kit](https://www.prophesee.ai/event-based-metavision-amd-kria-starter-kit/)
- [Prophesee KV260 Quickstart Guide](https://www.prophesee.ai/quickstart-prophesee-metavision-starter-amd-kria-kv260/)
- [AMD Event-Based Vision Starter Kit Page](https://www.amd.com/en/products/system-on-modules/kria/k26/kv260-vision-starter-kit/event-based-vision-starter-kit.html)
- [LogicTronix Kria-Prophesee GitHub](https://github.com/LogicTronixInc/Kria-Prophesee-Event-VitisAI)
- [Prophesee Academic Offer 2025](https://www.prophesee.ai/research-library-offer-2025/)
- [DigiKey KV260 Listing](https://www.digikey.com/en/products/detail/amd/SK-KV260-G/13985269)
