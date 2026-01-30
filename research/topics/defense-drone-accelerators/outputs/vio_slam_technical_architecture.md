# VIO/SLAM Technical Architecture for Hardware Acceleration

> Detailed breakdown of what to accelerate and how

**Generated**: 2026-01-25
**Audience**: Logic designers evaluating FPGA/ASIC implementation
**Confidence**: HIGH (based on published implementations)

---

## Table of Contents

1. [VIO Pipeline Overview](#vio-pipeline-overview)
2. [Computational Breakdown](#computational-breakdown)
3. [Block-by-Block Analysis](#block-by-block-analysis)
4. [Memory Architecture](#memory-architecture)
5. [FPGA Resource Estimates](#fpga-resource-estimates)
6. [Event-Based VIO Differences](#event-based-vio-differences)
7. [Recommended Acceleration Strategy](#recommended-acceleration-strategy)
8. [Reference Implementations](#reference-implementations)

---

## VIO Pipeline Overview

### Standard Frame-Based VIO

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VIO PIPELINE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FRONT-END (Image Processing)              BACK-END (State Estimation)  │
│  ┌─────────────────────────────┐           ┌─────────────────────────┐  │
│  │                             │           │                         │  │
│  │ ┌─────────┐   ┌──────────┐  │           │  ┌──────────────────┐   │  │
│  │ │ Image   │──→│ Feature  │  │           │  │ IMU              │   │  │
│  │ │ Input   │   │ Detection│  │           │  │ Preintegration   │   │  │
│  │ └─────────┘   │ (FAST/   │  │           │  │                  │   │  │
│  │               │  ORB)    │  │           │  └────────┬─────────┘   │  │
│  │               └────┬─────┘  │           │           │             │  │
│  │                    │        │           │           ▼             │  │
│  │               ┌────▼─────┐  │           │  ┌──────────────────┐   │  │
│  │               │ Feature  │  │           │  │ State            │   │  │
│  │               │ Tracking │──┼───────────┼─→│ Estimation       │   │  │
│  │               │ (Optical │  │           │  │ (EKF/            │   │  │
│  │               │  Flow/   │  │           │  │  Optimization)   │   │  │
│  │               │  KLT)    │  │           │  │                  │   │  │
│  │               └────┬─────┘  │           │  └────────┬─────────┘   │  │
│  │                    │        │           │           │             │  │
│  │               ┌────▼─────┐  │           │           ▼             │  │
│  │               │Descriptor│  │           │  ┌──────────────────┐   │  │
│  │               │Extraction│  │           │  │ Map Update       │   │  │
│  │               │ (BRIEF/  │  │           │  │ (Optional)       │   │  │
│  │               │  ORB)    │  │           │  │                  │   │  │
│  │               └──────────┘  │           │  └──────────────────┘   │  │
│  │                             │           │                         │  │
│  └─────────────────────────────┘           └─────────────────────────┘  │
│                                                                         │
│              ~90% of compute time                ~10% of compute time   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                           ┌───────────────┐
                           │ Pose Output   │
                           │ (position,    │
                           │  orientation, │
                           │  velocity)    │
                           └───────────────┘
```

### Key Insight: Front-End Dominates

**Feature extraction and tracking account for >90% of runtime** on general computing platforms. This is the primary target for hardware acceleration.

---

## Computational Breakdown

### Runtime Distribution (ORB-SLAM on CPU)

| Component | % Runtime | Operations | Parallelism |
|-----------|-----------|------------|-------------|
| **Feature Detection (FAST)** | 25-35% | Corner detection | Highly parallel |
| **Feature Tracking (Optical Flow)** | 30-40% | Lucas-Kanade / dense flow | Highly parallel |
| **Descriptor Extraction (BRIEF/ORB)** | 15-20% | Binary patterns | Highly parallel |
| **Descriptor Matching** | 10-15% | Hamming distance | Parallel |
| **IMU Preintegration** | 2-5% | Matrix multiply | Sequential |
| **State Estimation (EKF/BA)** | 5-10% | Matrix operations | Some parallel |

### What to Accelerate in Hardware

| Block | Hardware Fit | Rationale |
|-------|--------------|-----------|
| **FAST corners** | ★★★★★ | Regular memory access, pixel-parallel |
| **Optical flow (LK)** | ★★★★★ | Iterative, parallel over patches |
| **BRIEF descriptors** | ★★★★★ | Simple binary comparisons |
| **Hamming matching** | ★★★★☆ | Parallel XOR + popcount |
| **Gaussian pyramid** | ★★★★☆ | Separable convolution |
| **IMU preintegration** | ★★★☆☆ | Small, fixed math |
| **Bundle adjustment** | ★★☆☆☆ | Sparse, irregular, iterative |
| **Loop closure** | ★☆☆☆☆ | Complex, rare, CPU better |

---

## Block-by-Block Analysis

### 1. FAST Corner Detection

**Algorithm**: Compare center pixel to 16 surrounding pixels on Bresenham circle. Corner if N contiguous pixels all brighter or all darker than center ± threshold.

**Hardware Architecture**:
```
                    ┌─────────────┐
    Pixel Stream ──→│ Line Buffer │──→ 7x7 Window
                    │ (7 lines)   │
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ 16 Pixel    │
                    │ Comparators │ (parallel)
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Contiguous  │
                    │ Segment     │
                    │ Detector    │
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Non-Max     │
                    │ Suppression │
                    └─────────────┘
                           │
                           ▼
                      Corner (x,y)
```

**Resources (estimated)**:
| Resource | Count | Notes |
|----------|-------|-------|
| LUTs | ~2,000 | Comparators + logic |
| BRAM | 7 line buffers | ~10KB for 720p |
| Latency | ~7 lines | Pipeline depth |

**Throughput**: 1 pixel/cycle → 100 Mpix/s @ 100MHz → **140 fps @ 720p**

### 2. Optical Flow (Lucas-Kanade)

**Algorithm**: Iteratively solve for motion (dx, dy) that minimizes sum of squared differences in a patch between frames.

**Hardware Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│                  LK OPTICAL FLOW ENGINE                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐     ┌────────────┐     ┌────────────┐       │
│  │ Frame      │     │ Sobel      │     │ Gradient   │       │
│  │ Buffer     │────→│ Gradient   │────→│ Products   │       │
│  │ (current + │     │ Ix, Iy     │     │ Ix², Iy²,  │       │
│  │  previous) │     │            │     │ Ix*Iy, Ix*It│      │
│  └────────────┘     └────────────┘     └────────────┘       │
│                                               │              │
│                                               ▼              │
│                                        ┌────────────┐       │
│                                        │ Patch      │       │
│                                        │ Accumulator│       │
│                                        │ (ΣIx², etc)│       │
│                                        └────────────┘       │
│                                               │              │
│                                               ▼              │
│  ┌────────────┐                        ┌────────────┐       │
│  │ Iteration  │←───────────────────────│ 2x2 Matrix │       │
│  │ Controller │                        │ Solve      │       │
│  │            │                        │ (dx, dy)   │       │
│  └────────────┘                        └────────────┘       │
│        │                                     │              │
│        │ (typically 3-5 iterations)          │              │
│        ▼                                     ▼              │
│  ┌────────────┐                        ┌────────────┐       │
│  │ Convergence│                        │ Motion     │       │
│  │ Check      │                        │ Vector Out │       │
│  └────────────┘                        └────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Resources (estimated for 21x21 patch, 500 features)**:
| Resource | Count | Notes |
|----------|-------|-------|
| LUTs | ~15,000 | Gradient + accumulation |
| DSPs | 20-40 | Multiply-accumulate |
| BRAM | ~1MB | Two frame buffers |
| Latency | ~5ms/frame | For 500 features, 5 iterations |

### 3. ORB Descriptor Extraction

**Algorithm**: BRIEF descriptor with rotation normalization. 256-bit binary vector from 256 pixel pair comparisons.

**Hardware Architecture**:
```
                    ┌─────────────┐
    Patch (31x31) ─→│ Rotation    │──→ Oriented Patch
                    │ by θ        │
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ 256 Pixel   │
                    │ Pair        │──→ 256-bit Descriptor
                    │ Comparisons │
                    └─────────────┘
                    (parallel)
```

**Resources (estimated)**:
| Resource | Count | Notes |
|----------|-------|-------|
| LUTs | ~3,000 | Comparators |
| BRAM | Patch buffer | ~1KB per feature |
| DSPs | 4-8 | For rotation (optional) |
| Latency | ~1 cycle | Per descriptor (pipelined) |

### 4. Descriptor Matching (Hamming Distance)

**Algorithm**: XOR two 256-bit descriptors, count set bits.

**Hardware Architecture**:
```
    Descriptor A ──┐
                   ├──→ XOR (256-bit) ──→ Popcount ──→ Distance
    Descriptor B ──┘
```

**Resources**:
| Resource | Count | Notes |
|----------|-------|-------|
| LUTs | ~500 | XOR + popcount tree |
| Latency | 2-3 cycles | Pipelined |
| Throughput | 1 match/cycle | Easily parallelized |

### 5. IMU Preintegration

**Algorithm**: Integrate accelerometer and gyroscope over time between visual measurements. Rotation, velocity, position deltas.

**Hardware Architecture**:
```
    IMU Data (ax, ay, az, gx, gy, gz)
                    │
                    ▼
            ┌───────────────┐
            │ Bias          │
            │ Subtraction   │
            └───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ Rotation      │
            │ Integration   │ (quaternion multiply)
            │ Δq = Δq ⊗ q(ω·dt)
            └───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ Velocity &    │
            │ Position      │
            │ Integration   │
            └───────────────┘
                    │
                    ▼
            (ΔR, Δv, Δp, Jacobians)
```

**Resources**:
| Resource | Count | Notes |
|----------|-------|-------|
| LUTs | ~2,000 | Control logic |
| DSPs | 16-24 | Matrix operations |
| Latency | ~10 cycles | Per IMU sample |

### 6. State Estimation (EKF)

**Algorithm**: Extended Kalman Filter - predict/update cycle fusing IMU and visual measurements.

**Key Operations**:
- Matrix multiply: 15x15 state × 15x15 covariance
- Matrix inverse: 6x6 innovation covariance (Cholesky)
- Jacobian computation

**Hardware Fit**: MEDIUM - Benefits from DSP acceleration but complex control. Often left on CPU with hardware assist for matrix operations.

---

## Memory Architecture

### Bandwidth Requirements

| Data | Size | Access Pattern | Bandwidth (30 fps) |
|------|------|----------------|-------------------|
| Input frame (720p) | 1 MB | Sequential | 30 MB/s |
| Previous frame | 1 MB | Random (patches) | ~100 MB/s |
| Feature coordinates | 4 KB | Random | 0.1 MB/s |
| Descriptors | 16 KB | Sequential | 0.5 MB/s |
| Map points | Variable | Random | Depends on map |

### Memory Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                  ON-CHIP                                │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌────────────┐  │
│  │ Line Buffers  │  │ Patch Cache   │  │ Feature    │  │
│  │ (FAST, Sobel) │  │ (LK tracking) │  │ FIFO       │  │
│  │ ~50 KB        │  │ ~100 KB       │  │ ~16 KB     │  │
│  └───────────────┘  └───────────────┘  └────────────┘  │
│                                                         │
│  ┌───────────────┐  ┌───────────────┐                  │
│  │ Descriptor    │  │ IMU Buffer    │                  │
│  │ Buffer        │  │ ~1 KB         │                  │
│  │ ~64 KB        │  │               │                  │
│  └───────────────┘  └───────────────┘                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  OFF-CHIP (DDR)                         │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────┐  │
│  │ Frame Buffer (current + previous)                 │  │
│  │ ~4 MB (stereo, grayscale)                         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Sparse Map (if SLAM, not just VO)                 │  │
│  │ Variable (1-100 MB)                               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Bandwidth Optimization

MIT Navion techniques:
- **Reduced bit depth**: 8-bit → 5-bit per pixel, only 6% accuracy loss, 38% memory reduction
- **Skip right stereo frame**: Use disparity from previous, reduce bandwidth
- **In-place feature update**: Don't copy, update features in tracking memory

---

## FPGA Resource Estimates

### Full VIO Front-End Accelerator

Target: 720p @ 30 fps, 500 features, ORB descriptors

| Resource | Usage | % of ZU15EG |
|----------|-------|-------------|
| LUTs | ~80,000 | 36% |
| BRAM | ~3 MB | 52% |
| DSPs | ~200 | 19% |
| Power | ~2W | (FPGA fabric) |

### Comparison: Published Implementations

| Implementation | FPGA | Resolution | FPS | Power |
|----------------|------|------------|-----|-------|
| eSLAM (ORB-SLAM) | Zynq UltraScale+ | 640x480 | 31 | ~3W |
| Feature Tracker | Zynq UltraScale+ | 1920x1080 | 48 | ~4W |
| Navion ASIC | 65nm custom | 752x480 | 171 | 24mW |

---

## Event-Based VIO Differences

### What Changes

| Aspect | Frame-Based | Event-Based |
|--------|-------------|-------------|
| **Input** | Full frames @ 30-60 Hz | Event stream (async) |
| **Feature detection** | Corners in frame | Corners from event accumulation |
| **Tracking** | Frame-to-frame optical flow | Event-to-event or time surface |
| **Bandwidth** | High (full frames) | Low (sparse events) |
| **Latency** | Limited by frame rate | Microsecond potential |

### Event-Based Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EVENT-BASED VIO PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │ Event       │────→│ Time        │────→│ Event       │               │
│  │ Stream      │     │ Surface     │     │ Corner      │               │
│  │ (x,y,t,p)   │     │ Generation  │     │ Detection   │               │
│  └─────────────┘     └─────────────┘     └─────────────┘               │
│                                                 │                       │
│                                                 ▼                       │
│  ┌─────────────┐                         ┌─────────────┐               │
│  │ IMU         │────────────────────────→│ Event-IMU   │               │
│  │ Stream      │                         │ Fusion      │               │
│  └─────────────┘                         │ (EKF/Opt)   │               │
│                                          └─────────────┘               │
│                           ┌─────────────┐      │                       │
│                           │ Event       │      │                       │
│                           │ Tracking    │←─────┘                       │
│                           │ (ICP on     │                              │
│                           │  time surf) │                              │
│                           └─────────────┘                              │
│                                  │                                      │
│                                  ▼                                      │
│                           ┌─────────────┐                              │
│                           │ Pose Output │                              │
│                           └─────────────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Hardware Implications for Event-Based

| Block | Hardware Consideration |
|-------|----------------------|
| **Event interface** | High-speed async protocol (not standard MIPI) |
| **Time surface** | Rolling update, ~100KB BRAM for 640x480 |
| **Event filtering** | On-the-fly noise rejection |
| **Feature tracking** | Fundamentally different from LK |
| **SNN potential** | Natively event-driven, matches data format |

---

## Recommended Acceleration Strategy

### Phase 1: Frame-Based FPGA IP (Conservative)

**Target**: Accelerate front-end for standard cameras

```
┌─────────────────────────────────────────────────────────────┐
│                    ACCELERATOR SCOPE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FPGA Accelerated:                CPU (Host):               │
│  ┌─────────────────────┐          ┌─────────────────────┐  │
│  │ • FAST detection    │          │ • State estimation  │  │
│  │ • Gaussian pyramid  │──────────│   (EKF / BA)        │  │
│  │ • Optical flow (LK) │  Feature │ • Map management    │  │
│  │ • ORB descriptors   │  coords  │ • Loop closure      │  │
│  │ • Descriptor match  │  + descs │ • High-level logic  │  │
│  └─────────────────────┘          └─────────────────────┘  │
│                                                             │
│  Power: ~2W               Power: ~1W (Cortex-A53)          │
│  Latency: ~10ms           Latency: ~5ms                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Event-Based Extension (Differentiated)

**Add**: Event camera interface + event-specific processing

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTENDED SCOPE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Event Camera Interface (Prophesee MIPI / custom)    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Event Processing Engine                              │   │
│  │ • Time surface generation                            │   │
│  │ • Event filtering / denoising                        │   │
│  │ • Event corner detection                             │   │
│  │ • Event tracking (optional: SNN-based)               │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Existing Frame-Based Pipeline (dual mode)            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Full Neuromorphic (Disruptive)

**Ultimate goal**: SNN-based processing throughout

- Event camera → SNN feature extraction → SNN tracking → Hybrid state estimation
- Target: <100mW total
- Requires SNN IP development or partnership (SynSense, BrainChip)

---

## Reference Implementations

### Open Source Starting Points

| Project | What It Has | Link |
|---------|-------------|------|
| **eSLAM** | ORB extractor + matcher on FPGA | [arxiv.org/abs/1906.05096](https://arxiv.org/abs/1906.05096) |
| **ESVO2** | Event-based stereo VO (software) | [github.com/NAIL-HNU/ESVO2](https://github.com/NAIL-HNU/ESVO2) |
| **OpenVINS** | State estimation reference | [docs.openvins.com](https://docs.openvins.com/) |
| **VINS-Mono** | Full VIO pipeline (software) | [github.com/HKUST-Aerial-Robotics/VINS-Mono](https://github.com/HKUST-Aerial-Robotics/VINS-Mono) |

### Key Papers

| Paper | Contribution |
|-------|--------------|
| Navion (MIT) | First full VIO ASIC, 24mW |
| eSLAM | ORB-SLAM FPGA, 71x energy efficiency |
| Feature Tracker | 108 fps @ 720p on FPGA |

---

## Summary: What to Build

### Minimum Viable Accelerator

| Block | Priority | Effort | Impact |
|-------|----------|--------|--------|
| FAST corners | P1 | Low | High |
| Optical flow (LK) | P1 | Medium | High |
| BRIEF/ORB descriptors | P1 | Low | Medium |
| Gaussian pyramid | P2 | Low | Medium |
| Descriptor matching | P2 | Low | Medium |
| Event interface | P2 | Medium | High (differentiation) |

### Estimated Development

| Phase | Scope | Effort | Risk |
|-------|-------|--------|------|
| Frame-based front-end | FAST + LK + ORB | 6-9 months | Low |
| Event camera support | Interface + time surface | 3-6 months | Medium |
| Full event-based VIO | Event tracking + fusion | 6-12 months | Medium-High |
| SNN integration | Partnership or custom | 12-18 months | High |

---

## Sources

- [eSLAM: Energy-Efficient Accelerator for ORB-SLAM](https://arxiv.org/abs/1906.05096)
- [FPGA-Based Feature Extraction for Visual SLAM](https://pmc.ncbi.nlm.nih.gov/articles/PMC10574966/)
- [Navion: 2mW VIO ASIC](https://eems.mit.edu/wp-content/uploads/2018/12/2019_jssc_navion.pdf)
- [Mix-VIO: Hybrid Tracking Strategy](https://pmc.ncbi.nlm.nih.gov/articles/PMC11358903/)
- [How VIO Works](https://www.thinkautonomous.ai/blog/visual-inertial-odometry/)
- [ESVO2: Event-Based Stereo VIO](https://arxiv.org/html/2410.09374v1)
