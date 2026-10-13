# Competitive Deep Dive - Neuromorphic Processors

> Detailed comparison of SynSense, BrainChip, and Intel Loihi

**Generated**: 2026-01-26
**Purpose**: Understand competitive landscape and identify differentiation opportunities

---

## Executive Summary

| Platform | Commercial | VIO Capable | Power | Your Opportunity |
|----------|------------|-------------|-------|------------------|
| **Intel Loihi 2** | ❌ Research only | ✅ Proven | ~1W | Can't buy it |
| **BrainChip Akida** | ✅ Yes | ⚠️ Partial | <1W | Not optimized for VIO |
| **SynSense Speck** | ✅ Yes | ❌ No (128x128) | <5mW | Too low resolution |

**Gap**: No commercial neuromorphic processor is optimized for **high-resolution event-based VIO**.

---

## Intel Loihi 2

### Overview

| Attribute | Value |
|-----------|-------|
| **Company** | Intel Labs |
| **Status** | Research program only |
| **Process** | Intel 4 (7nm-class) |
| **Availability** | By application to Intel Neuromorphic Research Community |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      LOIHI 2 CHIP                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              128 Neuron Cores                        │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       ┌─────┐     │   │
│  │  │ NC  │ │ NC  │ │ NC  │ │ NC  │  ...  │ NC  │     │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘       └─────┘     │   │
│  │                                                     │   │
│  │  Each core: ~8K neurons, programmable              │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                   Network-on-Chip                          │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           6 Embedded x86 Cores (Lakemont)           │   │
│  │           For control, I/O, learning                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Specifications

| Spec | Loihi 1 | Loihi 2 |
|------|---------|---------|
| Neurons | 128K | 1M |
| Synapses | 128M | 120M |
| Process | 14nm | Intel 4 |
| Die Size | 60 mm² | 31 mm² |
| Cores | 128 | 128 |
| Spike Processing | Baseline | 10x faster |

### Demonstrated VIO Results

| Demo | Result |
|------|--------|
| **TU Delft Drone** | 64x faster than GPU, 3x less energy |
| **UZH Racing Drone** | 80 km/h, beat human champions |
| **SLAM on Loihi** | 100x more energy efficient than CPU |
| **Flight Control SNN** | 7-12 mW additional power |

### Strengths

- **Most capable** neuromorphic processor for research
- **Proven VIO demos** with event cameras
- **Flexible** neuron models (programmable)
- **Large ecosystem** (Lava framework, INRC community)
- **Cutting-edge process** (Intel 4)

### Limitations

| Limitation | Impact |
|------------|--------|
| **Not commercially available** | Can't build products with it |
| **Research access only** | Must apply to INRC |
| **No production roadmap** | Intel hasn't announced commercial plans |
| **Intel's commitment uncertain** | Neuromorphic is small part of Intel |

### Competitive Implication

**You cannot compete with Loihi on capability, but you can compete on availability.** If you build a commercial VIO accelerator, you address a market Loihi cannot serve.

---

## BrainChip Akida

### Overview

| Attribute | Value |
|-----------|-------|
| **Company** | BrainChip (ASX: BRN) |
| **Status** | Commercial (IP licensing + chips) |
| **Process** | TSMC 28nm (AKD1000) |
| **Price** | Dev kit ~$500, IP licensing negotiable |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AKIDA AKD1000                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              80 Neural Processing Units              │   │
│  │                                                      │   │
│  │  Each NPU:                                          │   │
│  │  ├── 8 Neural Processing Engines (NPEs)             │   │
│  │  ├── 40KB weight SRAM                               │   │
│  │  └── 60KB data spike SRAM                           │   │
│  │                                                      │   │
│  │  Total: 1.2M neurons, 10B synapses                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                    Scalable Fabric                         │
│                   (1-128 nodes)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Akida 2.0 (Latest)

| Feature | Akida 1.0 | Akida 2.0 |
|---------|-----------|-----------|
| Weights | 4-bit | 8-bit |
| Vision Transformers | No | Yes (Akida-P) |
| TENNs | No | Yes |
| Multi-chip | Limited | Enhanced |

**Product Lines**:
- **Akida-E**: Energy efficiency focus
- **Akida-S**: MCU/SoC integration
- **Akida-P**: High performance + ViT

### Specifications

| Spec | Value |
|------|-------|
| Neurons | 1.2 million |
| Synapses | 10 billion |
| Clock | 300 MHz |
| Power | Milliwatts typical |
| Benchmark | 100 FPS @ 9mW (ImageNet demo) |

### Supported Networks

- Convolutional Neural Networks (CNNs)
- Deep Neural Networks (DNNs)
- Recurrent Neural Networks (RNNs)
- Vision Transformers (ViT) - Akida 2.0
- Temporal Event-Based Neural Nets (TENNs)

### Software Ecosystem

| Tool | Purpose |
|------|---------|
| **MetaTF** | Model conversion from TensorFlow/ONNX/PyTorch |
| **Akida Model Zoo** | Pre-trained models |
| **Edge Impulse** | Third-party integration |

**Strengths**:
- **Commercially available** (buy today)
- **Mature software** (MetaTF, model zoo)
- **On-chip learning** (unique feature)
- **IP licensing** (integrate into custom SoC)
- **Public company** (stability, accountability)

### Limitations for VIO

| Limitation | Impact on VIO |
|------------|---------------|
| **Not event-native** | Converts frames to events internally, not optimized for DVS input |
| **No direct event camera interface** | Must preprocess events externally |
| **Optimized for classification** | Not for continuous state estimation |
| **Fixed architecture** | Less flexible than Loihi for custom VIO |
| **No VIO demos** | No published VIO implementations |

### Competitive Implication

**Akida is a general-purpose edge AI chip, not a VIO accelerator.** It could theoretically run parts of VIO but isn't optimized for it. Your opportunity: **purpose-built VIO accelerator** beats general-purpose on efficiency.

---

## SynSense Speck

### Overview

| Attribute | Value |
|-----------|-------|
| **Company** | SynSense AG (Zurich) |
| **Status** | Commercial (dev kits available) |
| **Process** | Not disclosed |
| **Price** | Dev kit ~$500 |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SPECK SoC                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────┐    │
│  │  Integrated DVS     │    │   DYNAP-CNN Processor   │    │
│  │  128 x 128 pixels   │───→│   328K spiking neurons  │    │
│  │                     │    │   9 CNN layers max      │    │
│  └─────────────────────┘    └─────────────────────────┘    │
│                                                             │
│  Fully asynchronous, event-driven throughout               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Specifications

| Spec | Value |
|------|-------|
| **Integrated Sensor** | 128 x 128 DVS |
| **Neurons** | 328,000 spiking |
| **CNN Layers** | Up to 9 |
| **Latency** | ~3 µs per spike |
| **Power (idle)** | 0.42 mW |
| **Power (active)** | <5 mW |
| **Power (face recognition)** | <1 mW |

### Software Ecosystem

| Tool | Purpose |
|------|---------|
| **SINABS** | SNN framework (Keras/PyTorch → SNN) |
| **Samna** | Hardware interface middleware |
| **Rockpool** | SNN training and deployment |

### Demonstrated Applications

| Application | Notes |
|-------------|-------|
| Gesture recognition | Commercial deployment in toys |
| Face detection | <1 mW |
| Drone detection | 20m range |
| Fall detection | Wearables |
| 27g drone | 25-minute flight time |

### Strengths

- **Integrated sensor + processor** (unique)
- **Extremely low power** (<5 mW total)
- **True event-driven** throughout
- **Commercial** (dev kits shipping)
- **Prophesee partnership** (co-development)

### Limitations for VIO

| Limitation | Impact on VIO |
|------------|---------------|
| **128 x 128 resolution** | **Far too low for VIO** (need 640x480+) |
| **No external camera interface** | Can't connect HD event camera |
| **Limited neurons** | 328K may not support full VIO pipeline |
| **Optimized for classification** | Not continuous estimation |
| **No IMU interface** | Would need external fusion |

### Competitive Implication

**Speck is amazing for ultra-low-power classification but wrong resolution for VIO.** Your opportunity: **HD-resolution event-based VIO** that Speck cannot address.

---

## Side-by-Side Comparison

### Hardware Specs

| Spec | Intel Loihi 2 | BrainChip Akida | SynSense Speck |
|------|---------------|-----------------|----------------|
| **Neurons** | 1M | 1.2M | 328K |
| **Synapses** | 120M | 10B | N/A |
| **Process** | Intel 4 | 28nm | N/A |
| **Power** | ~1W | <1W | <5mW |
| **Event Camera** | External | External | Integrated 128x128 |
| **Commercial** | ❌ No | ✅ Yes | ✅ Yes |

### VIO Suitability

| Factor | Intel Loihi 2 | BrainChip Akida | SynSense Speck |
|--------|---------------|-----------------|----------------|
| **HD Resolution Support** | ✅ Yes | ⚠️ Limited | ❌ No |
| **Event Camera Interface** | ✅ Yes | ❌ External preprocess | ❌ Fixed 128x128 |
| **Continuous State Est.** | ✅ Proven | ⚠️ Not optimized | ❌ Not designed for |
| **IMU Fusion** | ✅ Demonstrated | ⚠️ Possible | ❌ No interface |
| **Published VIO Demos** | ✅ Multiple | ❌ None | ❌ None |
| **Commercial Availability** | ❌ No | ✅ Yes | ✅ Yes |

### Software Maturity

| Factor | Intel Loihi 2 | BrainChip Akida | SynSense Speck |
|--------|---------------|-----------------|----------------|
| **Framework** | Lava | MetaTF | SINABS/Rockpool |
| **PyTorch/TF Support** | ⚠️ Via conversion | ✅ Good | ⚠️ Via conversion |
| **Model Zoo** | ⚠️ Research | ✅ Yes | ⚠️ Limited |
| **Documentation** | ✅ Good | ✅ Good | ⚠️ Moderate |
| **Community** | ✅ INRC | ⚠️ Small | ⚠️ Small |

---

## Competitive Positioning

### Where Each Wins

```
                        CONTINUOUS STATE ESTIMATION
                                    ▲
                                    │
                Intel Loihi 2       │
                (if it were        │
                 commercial)       │
        ┌───────────────────┐      │
        │                   │      │
        │   YOUR            │      │
        │   OPPORTUNITY     │      │
        │                   │      │
        └───────────────────┘      │
                                    │
LOW POWER ◄─────────────────────────┼───────────────────────► HIGH POWER
                                    │
                SynSense Speck      │        BrainChip Akida
                (classification     │        (general edge AI)
                 only)             │
                                    │
                                    ▼
                            CLASSIFICATION
```

### Your Differentiation

| vs. Intel Loihi | vs. BrainChip Akida | vs. SynSense Speck |
|-----------------|---------------------|--------------------|
| **You're commercial** | **You're VIO-optimized** | **You support HD resolution** |
| Can actually buy | Purpose-built beats general | External HD event camera |
| Production roadmap | Native event interface | Full VIO pipeline |
| | IMU fusion built-in | |

---

## Opportunities They Leave Open

### 1. Integrated HD Event-Based VIO

**Nobody offers**: Single-chip solution for HD event camera → pose output

**Why**:
- Loihi: Research only
- Akida: General-purpose, not VIO-optimized
- Speck: Wrong resolution

### 2. Direct Event Camera Interface

**Nobody offers**: Native MIPI interface optimized for Prophesee/iniVation

**Why**:
- All require external preprocessing
- Adds latency, power, complexity

### 3. Hybrid SNN + Fixed-Point Architecture

**Nobody offers**: Optimal split between SNN (feature extraction) and fixed-point (state estimation)

**Why**:
- Loihi: All SNN
- Akida: Pseudo-SNN with ANN conversion
- Speck: All SNN

### 4. IMU Fusion in Hardware

**Nobody offers**: Tight hardware integration of IMU with visual processing

**Why**:
- All treat IMU as external sensor
- Fusion done in software

### 5. Defense-Grade Hardening

**Nobody offers**: Neuromorphic VIO with defense qualifications

**Why**:
- All consumer/commercial focus
- Your opportunity if you choose defense path later

---

## What To Build (Competitive Whitespace)

```
┌─────────────────────────────────────────────────────────────┐
│              NEUROMORPHIC VIO ACCELERATOR                   │
│                  (Your Product)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  What Intel Loihi has (proven):                            │
│  ├── SNN processing for events                             │
│  ├── Event camera interface                                │
│  └── VIO algorithm support                                 │
│                                                             │
│  What BrainChip Akida has:                                 │
│  ├── Commercial availability                               │
│  ├── IP licensing model                                    │
│  └── Mature software                                       │
│                                                             │
│  What SynSense Speck has:                                  │
│  ├── Ultra-low power (<5mW)                                │
│  ├── Integrated sensor+processor                           │
│  └── Fully event-driven                                    │
│                                                             │
│  What NONE of them have:                                   │
│  ├── HD resolution VIO                          ← YOU      │
│  ├── Direct Prophesee/MIPI interface            ← YOU      │
│  ├── Purpose-built VIO pipeline                 ← YOU      │
│  ├── IMU fusion in hardware                     ← YOU      │
│  └── Commercial + VIO + HD resolution           ← YOU      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Partnership Opportunities

### Prophesee

**Why partner**:
- They sell sensors, need processing solutions
- Already partner with SynSense (low-res only)
- Gap in HD processing partner
- Access to defense customers

**What to offer**:
- Joint reference design: Prophesee EVK4 + your VIO IP
- Co-marketing
- Shared customer leads

### SynSense

**Why partner**:
- They have SNN expertise but wrong form factor for VIO
- Could license their SNN IP for your chip
- Complementary (they do classification, you do VIO)

**Risk**: They may compete if they move to HD

### BrainChip

**Why partner**:
- They have commercial infrastructure
- Could add VIO-specific accelerator to Akida
- IP licensing model fits

**Risk**: They may see you as competitor

---

## Risk Assessment

### If Intel Commercializes Loihi

**Probability**: LOW-MEDIUM (no announced plans, neuromorphic is side project)

**Impact**: HIGH (would dominate on capability)

**Mitigation**: Move fast, establish customer relationships, focus on integration/ease-of-use that big Intel won't provide

### If SynSense Moves to HD

**Probability**: MEDIUM (logical next step for them)

**Impact**: MEDIUM-HIGH (direct competition)

**Mitigation**: Differentiate on VIO-specific optimization, IMU integration, defense path

### If Qualcomm/NVIDIA Adds Event Support

**Probability**: MEDIUM (event cameras gaining traction)

**Impact**: MEDIUM (they'd do general-purpose, not VIO-specific)

**Mitigation**: Stay focused on VIO, be the specialist

---

## Summary

### Your Competitive Position

```
"The first commercial, HD-resolution, event-based VIO accelerator"

├── vs. Loihi: You're commercial
├── vs. Akida: You're VIO-optimized
├── vs. Speck: You support HD
└── vs. All: You integrate IMU fusion
```

### Key Differentiators to Build

1. **HD event camera interface** (MIPI, Prophesee-compatible)
2. **Purpose-built VIO pipeline** (not general-purpose SNN)
3. **IMU fusion in hardware** (not software afterthought)
4. **<200mW total power** (between Speck and Akida)
5. **Commercial from day 1** (Loihi can't compete)

---

## Sources

- [Intel Loihi 2 Overview](https://open-neuromorphic.org/neuromorphic-computing/hardware/loihi-2-intel/)
- [BrainChip Akida Technology](https://brainchip.com/technology/)
- [BrainChip Akida 2.0 Announcement](https://brainchip.com/brainchip-makes-second-generation-akida-platform-available-to-advance-state-of-edge-ai-solutions/)
- [SynSense Speck](https://open-neuromorphic.org/neuromorphic-computing/hardware/speck-synsense/)
- [SynSense Speck Product Page](https://www.synsense.ai/products/speck-2/)
- [Neuromorphic Hardware Comparison](https://open-neuromorphic.org/neuromorphic-computing/hardware/)
- [Top Neuromorphic Chips 2025](https://www.elprocus.com/top-neuromorphic-chips-in-2025/)
