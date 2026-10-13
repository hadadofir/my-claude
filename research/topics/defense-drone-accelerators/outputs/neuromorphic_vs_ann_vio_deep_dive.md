# Neuromorphic Neural Networks vs Conventional NNs for VIO
## A Logic Designer's Technical Deep Dive

**Written**: 2026-05-07
**Validity check performed**: 2026-07-01 (see addendum below — core thesis holds, one new competitor found, one hardware claim corrected)
**Audience**: Logic designer evaluating hardware acceleration for visual-inertial odometry
**Purpose**: Understand the computation gap between today's deployed VIO algorithms, the current deep learning frontier, and spiking/neuromorphic approaches — with hardware implications for each

---

## Validity Check Addendum (2026-07-01)

Re-verified this document ~2 months after writing. Overall: **the core thesis is intact and, if anything, better evidenced.** Details below.

### Still valid, no changes needed
- NeuroVIO remains framework-only with no DPVO/ORB-SLAM3 benchmark (§4.4, §10) — confirmed still true as of July 2026.
- SS-VIO (§3.5, §9.3) is a real, verifiable publication: "SS-VIO: A Novel Cross Modal State Space Visual Inertial Odometry," IEEE/RAL 2026 (IEEE Xplore doc 11297822; matches the ADS citation already in §11). Confidence in this citation raised from "plausible" to "confirmed."
- Section 4.8 maturity ladder, the "gap" in §5, and the Section 8 pipeline-decomposition argument all still match the current literature — no published SNN has closed the geometric-backend gap.

### New data point strengthening the NeuroVIO entry (§4.4)
NeuroVIO has a quantitative result this doc didn't capture: on the AQUALOC dataset, it cuts energy 80.4% vs. its non-spiking counterpart **while preserving pose-estimation accuracy**. That's a real (if narrow, underwater-only) accuracy-preserving benchmark — slightly more mature than "framework paper only" implied. Still no comparison against DPVO/ORB-SLAM3/EuRoC-class benchmarks.

### New paper filling part of "the gap" (§5, the sub-500mW/500mW-2W white space)
**TinyDEVO** (CVPR 2026 Workshops, arXiv 2604.08060) is a new, directly relevant data point: event-based deep VO running on a 9-core RISC-V ultra-low-power MCU at **86 mW, 1.2 fps, 27cm average trajectory error**, via an 11.5x memory reduction and 29.7x compute reduction vs. its parent model (DEVO). This is the first published demonstration that a *learned* event-VO pipeline can run at classical-VIO-class power. It's slow (1.2fps) and not yet competitive on accuracy, but it's evidence the sub-500mW learned-VIO gap is starting to close from the academic side — worth tracking as a possible IP-licensing or fast-follow target rather than a threat.

### Correction: Intel Loihi 3 timing is less certain than stated
§9.3 states "Intel Loihi 3 commercial availability Q3 2026 (confirmed)." On re-checking: **Intel has not published an official Loihi 3 product sheet, launch date, price, neuron count, or power spec.** The Q3 2026 date circulating online traces back to low-quality syndicated content (same article re-posted across several finance/news-aggregator sites), not an Intel press release or spec sheet. Treat Loihi 3 timing as **unconfirmed/rumored**, not a fixed planning input — don't set the SNN roadmap's "18-30 months" estimate in §9.1 against a hard Q3 2026 date.

### New competitive development (relevant to the product thesis generally, not VIO-specifically)
**HYFIX** raised a $15M seed round (Craft Ventures, announced April 2026) and shipped an "H1 Autonomous Systems Chip" / H1P module targeting exactly the "GPS-denied navigation chip for small drones" market this thesis targets. Important nuance: HYFIX's approach is **RTK/GNSS-correction based** (uses the GEODNET ground-station + LEO-satellite network for anti-spoofing, centimeter-accurate positioning) — it addresses GPS-*degraded*/spoofed environments, not true GPS-*denied* (no signal at all, e.g., indoors, tunnels, heavy jamming) environments that VIO targets. It's not a direct VIO competitor, but it is: (a) validation that investors will fund exactly this category of chip, and (b) a company that could plausibly add a VIO/vision fallback mode later. Worth tracking; doesn't change the recommendation but should be added to the competitive landscape doc.

### Market validation reconfirmed
The Army's Red Dragon contract (AeroVironment, $17.58M, awarded 2026-03-12, 400km range) is real and confirmed via multiple independent sources, and its GPS-denied navigation is explicitly built on "onboard autonomy and digital scene matching" — i.e., vision-based perception — which is a direct, concrete validation of the VIO-for-defense-drones thesis, not just an adjacent data point.

---

## Table of Contents

1. [The Three Paradigms](#1-the-three-paradigms)
2. [Computation Model: How Each Actually Computes](#2-computation-model-how-each-actually-computes)
3. [Current ANN VIO Algorithms — What They Do](#3-current-ann-vio-algorithms--what-they-do)
4. [SNN VIO — What Exists Today](#4-snn-vio--what-exists-today)
5. [Accuracy vs Power Tradeoff Map](#5-accuracy-vs-power-tradeoff-map)
6. [Training: ANN vs SNN](#6-training-ann-vs-snn)
7. [Hardware Mapping: Who Runs What](#7-hardware-mapping-who-runs-what)
8. [The VIO-Specific Insight: Where Each Paradigm Belongs](#8-the-vio-specific-insight-where-each-paradigm-belongs)
9. [Implications for the Accelerator Product](#9-implications-for-the-accelerator-product)
10. [Key Uncertainties](#10-key-uncertainties)
11. [Sources](#11-sources)

---

## 1. The Three Paradigms

VIO approaches split into three distinct computational paradigms. These are not stages of evolution — all three are actively used or researched today, for different reasons.

### Paradigm 1: Classical / Geometric VIO

**Examples**: ORB-SLAM3, VINS-Mono, OpenVINS, MSCKF, ESVO2 (event-based)

The pipeline is entirely hand-engineered:
1. Detect corners (FAST algorithm)
2. Track features across frames (Lucas-Kanade optical flow)
3. Compute binary descriptors (ORB/BRIEF)
4. Match descriptors (Hamming distance)
5. Fuse with IMU (Extended Kalman Filter or factor graph)
6. Estimate pose from geometric constraints (PnP, triangulation)

**No learned parameters.** All math is deterministic and well-understood. This is what almost every deployed drone uses today, including ModalAI VOXL, DJI platforms, and military drones.

**Why it's still dominant**: predictable, debuggable, runs on low-power CPUs, no GPU, no training data, no distribution shift risk.

### Paradigm 2: Deep ANN (Conventional Neural Network) VIO

**Examples**: DPVO, DROID-SLAM, TartanVO, MAC-VO (ICRA 2025 Best Paper), SuperPoint+LightGlue+EKF

Some or all of the pipeline is replaced by learned networks:
- Feature detection → Learned (SuperPoint)
- Optical flow → Learned (RAFT, NeuFlow)
- Pose estimation → End-to-end learned (DPVO, TartanVO)
- Uncertainty estimation → Learned (MAC-VO)
- Bundle adjustment → Differentiable, embedded in the network (DROID-SLAM)

**Key architectural types**: CNN, Transformer (attention), RNN/GRU, and very recently Mamba-based state space models (SS-VIO, RWKV-VIO, 2025-2026).

**Why it's better in theory**: handles illumination changes, textureless regions, motion blur, scale ambiguity — things that break hand-crafted detectors.

**Why it's not deployed on drones yet**: needs 4-24GB GPU VRAM, 5-15W GPU power, doesn't fit in a $5 embedded processor.

### Paradigm 3: Neuromorphic / Spiking Neural Network (SNN) VIO

**Examples**: TU Delft ego-motion on Loihi (2023), NeuroVIO hybrid (2025), UZH neuromorphic racing drone (2023)

Computation is fundamentally different:
- Neurons operate asynchronously
- Information is encoded in spike timing, not floating-point values
- Computation only occurs when a spike arrives (sparse, event-driven)
- Naturally paired with event cameras (same asynchronous, sparse paradigm)

**State of maturity**: Research only. No SNN has published competitive VIO accuracy numbers against DPVO or ORB-SLAM3 on standard benchmarks. The TU Delft Loihi demo was ego-motion estimation (velocity), not full 6-DOF VIO.

**Why it matters**: 1-10M operations per frame vs 500M-4B for learned ANNs. If accuracy can be matched, power consumption drops by 100-1000x.

---

## 2. Computation Model: How Each Actually Computes

This section is the core for a hardware designer: **what silicon operations does each paradigm require?**

### 2.1 Classical VIO: What Silicon Does

Every operation is deterministic and data-parallel.

```
FAST Corner Detection (per frame):
  - Load 7 pixel line buffers (streaming)
  - For every pixel: compare to 16 Bresenham circle neighbors
  - Check for 9+ contiguous bright/dark pixels → corner flag
  - Non-maximum suppression
  → Operations: 16 comparisons × (W × H) pixels
  → 720p: ~15M comparisons/frame
  → Hardware: line buffer + parallel comparators → 1 corner/cycle at 1 pixel/cycle

Lucas-Kanade Optical Flow (per 500 features):
  - For each feature: extract 21×21 patch from two frames
  - Compute image gradients (Sobel Ix, Iy)
  - Accumulate spatial gradient matrix (ΣIx², ΣIy², ΣIxIy)
  - Compute image difference (It = current - prev)
  - Solve 2×2 linear system: [dx, dy] = -(H^-1) × b
  - Iterate 3-5 times
  → Operations: ~20M MACs per frame for 500 features
  → Hardware: streaming multiply-accumulate, 2×2 matrix inverse (trivial)

ORB Descriptor (per 500 features):
  - Rotate 31×31 patch by computed orientation
  - Compare 256 predefined pixel pairs → 256-bit vector
  → Operations: 256 comparisons × 500 features = 128K ops/frame
  → Hardware: parallel comparators, trivially pipelined

IMU Preintegration (100 Hz IMU, 30 Hz camera):
  - ~3 samples between frames
  - Quaternion multiply: 16 MACs
  - Total: negligible
  → Hardware: tiny DSP block is sufficient

EKF Update:
  - 15×15 state covariance matrix operations
  - Cholesky factorization of 6×6 innovation matrix
  → Total: ~5,000 MAC-equivalent operations
  → Hardware: small DSP or CPU

TOTAL CLASSICAL VIO FRONT-END: ~150-300M MACs/frame at 720p, 30fps
```

**Silicon characteristics**: streaming, data-parallel, fixed precision (8-16 bit integer), low memory bandwidth (line buffers, patch caches). **This is exactly what FPGAs are built for.**

### 2.2 Deep ANN VIO: What Silicon Does

The fundamental operation is floating-point tensor multiply-accumulate, at massive scale.

```
Convolutional Feature Extraction (e.g., ResNet encoder in DPVO):
  Layer example: 3×3 conv, 128 in channels, 256 out channels, 90×160 spatial
  MACs = 3×3 × 128 × 256 × 90 × 160 = 13.4B MACs
  (one layer, one pass!)

Self-Attention in Transformer VIO (e.g., SS-VIO, 2026):
  Sequence length N = num patches = (720/16)×(1280/16) = 3600 patches
  Multi-head attention: Q,K,V projections: 3 × N × D² (D=512)
  Attention matrix: N × N = 3600 × 3600 = 13M entries
  Attention matmul: N² × D = ~6.7B MACs
  Feed-forward MLP: N × D × 4D = 3.7B MACs
  → One transformer layer: ~15-20B MACs
  → 12 layers: ~180-240B MACs per frame pair

RAFT Optical Flow (4D correlation volume approach):
  Feature extraction: ~50M MACs
  Correlation volume: all-pairs features → 4D tensor
  Optimized local lookup → ~200M MACs per iteration
  12 iterations → ~2.4B MACs per frame pair
  NeuFlow (10x faster variant): ~240M MACs per frame pair

DPVO (patch-based recurrent VO):
  Patch encoder: ~100M MACs per frame
  RNN update operator: ~200-500M MACs per frame
  Bundle adjustment layer: ~100M MACs per iteration × ~5 iterations
  → Total: ~1B MACs per frame pair
  → Memory: 4GB GPU VRAM minimum (for correlation volumes + state tensors)

DROID-SLAM:
  Dense optical flow (all pixels) → 2-4x DPVO compute
  Global bundle adjustment (multi-frame) → iterative, memory-intensive
  → Total: 2-4B MACs per frame, 11-24GB VRAM required
```

**Silicon characteristics**: irregular sparse tensor operations, high-bandwidth DRAM (dozens of GB/s), FP32/FP16/INT8 arithmetic, requires thousands of parallel execution units.

**FPGA limitation**: FPGA BRAMs hold 3-7MB; these models need 2-24GB. The tensor bandwidth is fundamentally off-chip. An FPGA can accelerate some convolutional layers but cannot run end-to-end transformer VIO — that requires GPU-class memory.

**The key number**: ANN VIO at 720p needs **1-4B MACs per frame** vs classical's **150-300M MACs per frame** — roughly 10-20x more computation, and on a completely different memory hierarchy.

### 2.3 SNN VIO: What Silicon Does

SNN computation is fundamentally different. The operation per neuron per timestep is:

```
Leaky Integrate-and-Fire (LIF) Neuron:
  v[t] = β × v[t-1] + Σ(w_i × spike_i[t])   // membrane potential update
  out[t] = 1 if v[t] > threshold, else 0      // spike or don't spike
  v[t] = v[t] × (1 - out[t])                  // reset if spiked

Key properties:
  - β (decay): typically 0.5-0.9 (one multiply)
  - w_i × spike_i: if spike is 0, this is a no-op (no MAC needed!)
  - Typical sparsity: 5-30% of neurons spike per timestep
  → Effective MAC cost per neuron per timestep: 0.05-0.30 (not 1.0)
```

For a typical SNN vision network:
- 10,000-100,000 neurons (much smaller than ANN feature maps)
- 8-32 timesteps per inference
- 5-30% sparsity

```
SNN feature extraction (comparable to 5-layer CNN):
  100,000 neurons × 16 timesteps × 0.15 sparsity × 100 synapses/neuron
  = 24M synapse operations
  vs ANN equivalent: 500M MACs
  → ~20x fewer operations
  → Energy savings: 20x fewer ops × 100x better energy/op on neuromorphic = 2000x

SNN optical flow (Spike-FlowNet):
  Published energy: ~927 μJ per inference
  vs ANN RAFT equivalent: ~15,000 μJ per inference
  → ~16x energy savings (measured, not theoretical)
```

**Silicon characteristics**: sparse, event-driven, irregular (no regular matrix ops), no floating point (weights are integers, operations are additions or zeros), low memory bandwidth (most zero-values skipped). **This requires custom neuromorphic silicon or FPGA with sparse-compute hardware.**

**FPGA challenge**: Standard FPGA DSPs are built for dense MAC operations. SNN's sparse, irregular access pattern doesn't map well to conventional DSP primitives. You need custom LUT-based sparse accumulation logic.

### 2.4 Side-by-Side Computation Summary

| Dimension | Classical VIO | ANN VIO | SNN VIO |
|-----------|:---:|:---:|:---:|
| **MACs per frame (720p)** | 150-300M | 1,000-4,000M | 1-25M |
| **Primary operation** | Integer add/compare | FP16/INT8 MAC | Spike accumulation |
| **Memory footprint** | 10-100MB | 2-24GB | 1-50MB |
| **Off-chip bandwidth** | 30-100 MB/s | 10-100 GB/s | 1-10 MB/s |
| **Temporal dynamics** | None | RNN/Mamba: yes | Native (spiking dynamics) |
| **Data parallelism** | High, regular | Very high, irregular | Low-medium, sparse |
| **FPGA fit** | Excellent | Poor (memory-bound) | Good (custom logic) |
| **ASIC fit** | Excellent | Excellent | Excellent (specialized) |
| **GPU fit** | Poor | Excellent | Poor |

---

## 3. Current ANN VIO Algorithms — What They Do

### 3.1 DPVO (Deep Patch Visual Odometry) — 2023, NeurIPS

**Core innovation**: Replace dense optical flow with sparse patch tracking.

Instead of computing flow for every pixel, DPVO:
1. Samples ~96 patches from input frames
2. Maintains patch *trajectories* across a 7-frame history
3. Uses an RNN to iteratively refine patch positions (similar to RAFT's recurrent refinement)
4. Embeds differentiable bundle adjustment inside the recurrent loop

**What makes it faster than DROID-SLAM**: patches (sparse) vs all pixels (dense). Reduces VRAM from 24GB to 4GB, runtime from "needs 2 RTX-3090s" to "runs in real-time on 1".

**Hardware target**: RTX 3090 or better. Too heavy for embedded.

**2025 optimization (DPVO-QAT++)**: Heterogeneous quantization + CUDA kernel fusion → 52% faster, 38% less VRAM. Brings it closer to Jetson-class hardware, but still 4-8W GPU power.

### 3.2 DROID-SLAM — 2021, ICCV

The quality ceiling. Builds a differentiable SLAM system where the optimization loop (bundle adjustment) is *inside* the neural network.

**What this means in hardware terms**: The network's forward pass *is* an iterative nonlinear optimization. Every inference step involves:
- Dense feature extraction across all frames in the graph
- All-pairs correlation lookup
- Differentiable Cholesky solve for camera poses

This is why it needs 24GB and 2 GPUs for long sequences. It's academically impressive but architecturally irreducible — you can't remove the memory without losing the capability.

**DPV-SLAM (2024)**: 2.5x faster derivative. Still GPU-only.

### 3.3 TartanVO — Generalization Champion

**Problem it solves**: Every classical VIO system needs calibration and tuning per environment. Most learned VIO overfits its training dataset.

**Solution**: Train on TartanAir (massive diverse synthetic dataset covering indoor, outdoor, night, rain, fog, underwater, space) with an up-to-scale loss that handles monocular ambiguity.

**Result**: A single model transfers to KITTI (outdoor), EuRoC (indoor), and ETH without retraining. This is the critical property for defense — a drone that works in a new theater without dataset collection.

**Hardware cost**: Lower than DROID-SLAM, but still CNN-based with GPU requirements.

### 3.4 MAC-VO — ICRA 2025 Best Paper on Robot Perception

The current best practical learned VIO for deployment considerations.

**Core insight**: Previous learned VIO treated all features equally. MAC-VO learns which features to *trust* — it estimates per-keypoint uncertainty based on global scene context, then weights pose graph optimization accordingly.

**Why this matters for hardware**: MAC-VO Fast Mode runs at **12.5 fps on 480x640** (on what hardware? — approximately Jetson-class). It uses learned uncertainty to *reduce* the number of features processed, not increase them. This is the direction toward embedded deployment.

### 3.5 The 2026 Frontier: State Space Models

**SS-VIO (2026, RAL)**: Replaces transformer attention with Mamba (State Space Model). Attention is O(N²) in sequence length; Mamba is O(N). For long sequences with many patches, this is a 10-50x compute reduction.

**Why relevant for hardware**: SSMs map well to fixed, streaming recurrent computations — closer to classical FPGA design patterns than transformers. An FPGA with dedicated state-machine logic could run SSM-VIO more efficiently than transformer-VIO.

### 3.6 Hybrid: Learned Front-End + Classical Back-End

The pragmatic path to deployment:

**SuperPoint** (detector) + **LightGlue** (matcher) + **OpenVINS** (factor graph backend):
- SuperPoint replaces FAST+ORB: ~70M MACs per frame (vs 5M for FAST)
- LightGlue replaces Hamming matching: 200-500M MACs (vs 1M for Hamming)
- OpenVINS backend: unchanged, EKF on CPU

**Mix-VIO (2024)**: Uses SuperPoint for detection but Lucas-Kanade for tracking (keeping LK in hardware) and LightGlue only for keyframe matching. Smart: expensive learned matching only when needed.

**Hardware implication**: A SuperPoint inference accelerator (a small CNN, ~5MB weights) is feasible on FPGA with 10-20MB BRAM. LightGlue is transformer-based — needs larger accelerator or GPU.

---

## 4. SNN VIO — What Exists Today

### 4.1 The Honest Landscape

There is **no published SNN that achieves competitive VIO accuracy on standard benchmarks**. This is the most important fact in this section. The TU Delft and UZH results are real, but they solve different sub-problems.

Here is what actually exists, with precise scope:

### 4.2 TU Delft Autonomous Neuromorphic Drone (2021-2023)

**What was implemented**: Ego-motion estimation — estimating the drone's *velocity* (vx, vy, vz, ωz) from event camera input. This is a critical distinction:

| Task | What it estimates | DOF | Useful for |
|------|------------------|-----|-----------|
| **Ego-motion** | Velocity at this instant | 4 | Stabilization, hovering |
| **Odometry (VO)** | Position relative to start | 6 | Navigation, mapping |
| **VIO** | Position + velocity + IMU fusion | 6+3 | Full autonomous navigation |

The TU Delft drone uses the SNN as a *reflex arc* (fast velocity estimate) not as a pose estimator. The drone can hover and avoid obstacles but cannot navigate a 100m indoor corridor and return to a known position.

**SNN architecture**: 5 layers, 28,800 neurons, Leaky Integrate-and-Fire neurons. Trained offline with supervised learning on labeled event-camera data, then deployed on Loihi.

**Power**: 7-12 mW *additional* compute for the neural processing. Total drone system power is much higher (motors, sensors, baseline compute).

**Accuracy**: Not reported in terms of m/s error. The behavior result is "can hover and avoid objects" — qualitative, not quantitative.

### 4.3 UZH Neuromorphic Racing Drone (2023)

**What was implemented**: High-speed obstacle avoidance using event camera + Loihi 2.

**Not VIO**: This system doesn't estimate the drone's pose. It detects obstacles and computes control commands directly. It's an end-to-end reactive control policy, trained with reinforcement learning, not a VIO module.

**Result**: 80 km/h flight, 30% faster than frame-based drone racing, beat human champions.

**Why it's impressive**: Latency. Event cameras + SNN produce control outputs in <1ms. At 80 km/h, 1ms = 2.2cm of travel. Frame cameras at 60fps + CPU have 16ms latency = 36cm. At those speeds, the frame-based drone crashes before it can react.

**Hardware implication**: SNN is doing reflex-level control (μs latency), not state estimation (ms latency). These are architecturally separate problems.

### 4.4 NeuroVIO: Hybrid ANN+SNN (October 2025)

**First paper** to explicitly frame the problem as hybrid ANN+SNN for visual-inertial pose estimation. Applied to underwater robotics.

**Architecture**: Conventional feature extraction → spiking layers for temporal fusion → pose output. The SNN portion handles temporal integration (accumulating evidence over time), which maps naturally to LIF neuron dynamics.

**Status**: No benchmark comparison against DPVO or ORB-SLAM3 has been published as of May 2026. The paper establishes the framework, not the accuracy ceiling.

### 4.5 SNN Optical Flow (Spike-FlowNet, SENECA)

This is the most mature SNN application in the VIO pipeline.

| System | Energy | Latency | Accuracy vs RAFT |
|--------|--------|---------|-----------------|
| **SENECA (2024-2025)** | 927 μJ | 44.9 ms | Comparable |
| **Spike-FlowNet** | ~62-75% of ANN | Comparable | Within 10% |

**Critical observation**: The energy savings are real but modest at the sub-component level. 927μJ vs ~15,000μJ for RAFT is a 16x improvement, but RAFT is overkill — classical LK optical flow for 500 features costs ~50μJ equivalent. The SNN is significantly more efficient than *learned* flow, but learned flow was always the wrong comparison. The right comparison is SNN flow vs classical LK, where the gap is much smaller.

### 4.6 ESVO2 — Clarification

**ESVO2 is NOT SNN-based.** It is a classical geometric algorithm that uses event cameras as input. The confusion arises because event cameras and SNNs are often mentioned together.

ESVO2 builds a **time surface** (a 2D map of when each pixel last triggered) and uses classical direct methods (photometric minimization, similar to DSO or LSD-SLAM) on this surface. There are no learned parameters.

**Why this matters**: ESVO2 is the most deployable event-based VIO right now. It's open-source (GPLv3), runs on CPU, and works at VGA resolution in real time. If you're building a prototype, ESVO2 is the algorithm to target, not any SNN approach.

### 4.7 Neuromorphic Resonator Networks (Nature Machine Intelligence, 2024)

**What it is**: A Vector Symbolic Architecture (VSA) abstraction for neuromorphic VO — a mathematical framework where the SNN computes symbolic geometric representations.

**Result**: Matches state-of-the-art on 2D visual odometry tasks. Not 3D, not full VIO.

**Significance**: Proof that SNNs can perform geometric computation at competitive accuracy — but in simplified settings. The architectural principles (spatial encoding via sparse distributed representations) are relevant for full VIO design.

### 4.8 The Summary: SNN VIO Maturity vs ANN VIO

```
Maturity Scale (1=idea, 10=production)

Classical VIO:          ████████████  10  Production-deployed
ANN Front-end (SP+LG):  ████████      8   Research → early commercial (Mix-VIO)
DPVO/MAC-VO:            ██████        6   Research with demo systems
DROID-SLAM:             █████         5   Research benchmark, GPU required
SNN Optical Flow:       ████          4   Proof of concept, measured energy gains
SNN Ego-motion:         ████          4   Drone demos (TU Delft, UZH)
SNN Full VIO:           ██            2   Framework papers only (NeuroVIO)
```

---

## 5. Accuracy vs Power Tradeoff Map

```
              │
     HIGH     │    ★ DROID-SLAM
   ACCURACY   │      DPVO ★
   (cm/m      │                        ★ MAC-VO
    drift)    │
              │         ★ TartanVO
              │
     MEDIUM   │  ★ VINS-Mono          ★ SuperPoint+OpenVINS
              │  ★ ORB-SLAM3
              │        ★ OpenVINS (classical)
              │
              │
     LOWER    │    SNN Ego-motion ★
              │    (not full VIO,         ★ NeuroVIO
              │     so unfair to compare)  (TBD accuracy)
              ├────────────────────────────────────────────────
              │  mW        0.1W      1W        5W        15W+
                         POWER (inference)

Classification of what runs where:
  Sub-500mW: Classical on ARM (MSCKF, OpenVINS)
              FPGA-accelerated classical (eSLAM, MIT Navion)
  0.5-2W:    Classical on Cortex-A72
              FPGA with learned front-end (SuperPoint)
  2-5W:      Hailo-8 (CNN inference only, not full VIO)
              Qualcomm RB5 (full VIO, 5-10W)
  7-15W:     NVIDIA Jetson Orin (full learned VIO)
  50W+:      DPVO, DROID-SLAM (desktop GPU)
```

**The gap**: Nothing exists between OpenVINS on ARM (~300-500mW, good accuracy) and Qualcomm RB5 (5-10W, better accuracy). This is the product opportunity.

---

## 6. Training: ANN vs SNN

### 6.1 How ANN VIO Is Trained

**End-to-end supervised** (DPVO, DROID-SLAM):
- Dataset: EuRoC MAV, TartanAir (500K+ frames), KITTI, ScanNet
- Supervision: Ground truth camera poses from motion capture or LIDAR
- Loss: L2 pose error + photometric loss + epipolar consistency
- Training time: 3-7 days on 4× A100 GPUs
- Optimization: Adam, batch size 4-8 (small batches because sequences are correlated)

**Self-supervised** (SelfVIO, PackNet-SfM):
- No ground truth poses needed
- Supervises via photometric loss: "does reprojecting frame N-1 into frame N look like frame N?"
- 30-50% weaker accuracy than supervised on standard benchmarks
- Used when pose ground truth is unavailable (e.g., your custom environment)

**The critical training challenge for deployment**: Learned VIO that trains on EuRoC may fail on a desert canyon. TartanVO addresses this with synthetic diversity. MAC-VO addresses this with learned uncertainty (ignore bad features). Neither fully solves it — this is an active research problem.

### 6.2 How SNNs Are Trained

Three methods exist, with very different properties:

**Method 1: Surrogate Gradient (dominant, 2024-2026)**

The spike function is non-differentiable (it's a step function). Surrogate gradient replaces the step with a smooth approximation (sigmoid, piecewise linear) *only during the backward pass*:

```
Forward:  out[t] = 1 if v[t] > threshold, else 0
Backward: ∂out/∂v ≈ sigmoid'(v - threshold)  [the "surrogate"]
```

This allows standard backpropagation through the SNN. Results:
- Competitive accuracy (83-85% on ImageNet vs 87-90% for ANNs)
- Training time: 2-5x longer than ANN equivalent (more timesteps, more memory)
- The accuracy gap is closing rapidly — 2022: 8% gap, 2025: 2-5% gap

**Method 2: ANN-to-SNN Conversion**

Train a standard ANN, then convert ReLU activations to firing rates:
- ReLU(x) maps to a neuron that fires x/max_rate times per second
- Achieves 80-84% ImageNet accuracy with 128-256 timesteps
- Lower accuracy than surrogate training
- Quick to implement (no SNN training expertise needed)
- **Hardware implication**: Requires many timesteps → higher latency than true SNN

**Method 3: Spike Timing-Dependent Plasticity (STDP)**

Biologically inspired, fully unsupervised learning rule: strengthen synapses when pre-neuron fires just before post-neuron, weaken when after.

- No labeled data required
- Extremely low power during training (no backprop)
- Current accuracy: 60-70% on ImageNet (vs 87-90% ANN) — unacceptable gap for VIO
- Used for online adaptation in deployment, not initial training

### 6.3 Accuracy Gap in Numbers

For image classification (the most benchmarked task):

| Method | ImageNet-1k | CIFAR-10 | Notes |
|--------|------------|----------|-------|
| **ANN (ResNet-50)** | 87-90% | 99%+ | Baseline |
| **SNN surrogate (2025 SOTA)** | 83-85% | 95-96% | 2-5% gap |
| **SNN converted (256 steps)** | 80-84% | 94-96% | 3-7% gap |
| **SNN STDP (unsupervised)** | 60-70% | 88-92% | 15-20% gap |

**For VIO specifically**: No direct comparison exists. The 2-5% gap on classification doesn't directly translate — VIO accuracy depends on geometric consistency, not just pixel-level recognition. SNNs may perform better on VIO's temporal tasks (where their native temporal dynamics help) and worse on recognition tasks (where they lag).

---

## 7. Hardware Mapping: Who Runs What

### 7.1 Classical VIO on FPGA

The match is near-perfect. The operations (streaming convolutions, line buffers, parallel comparators, DSP-based multiply-accumulate) are the canonical FPGA acceleration targets.

```
FAST detector:    Line buffer (7 lines) + 16-element comparator tree
LK optical flow:  Sobel gradient + patch-accumulate + 2×2 solve (4 DSPs)
ORB descriptor:   Bilinear interpolation + 256-parallel comparators
Hamming match:    XOR256 + popcount (2-3 cycles pipeline)
IMU preintegrate: Small DSP block (<20 DSPs)
EKF update:       Cholesky decompose (iterative, ~50 DSPs)
```

Published results on Zynq UltraScale+:
- eSLAM (ORB-SLAM FPGA): 31 fps @ 640×480, ~3W, 71x energy improvement over CPU
- Feature tracker: 48 fps @ 1920×1080, ~4W
- MIT Navion ASIC: 171 fps @ 752×480, 24mW (the theoretical target)

**The Navion gap**: Navion is a 65nm custom ASIC. The same design on a 22nm or 16nm ASIC would be ~3-5mW. Nobody has done it commercially.

### 7.2 ANN VIO on FPGA

Partially possible, poorly efficient.

**What FPGA can do well**: The convolutional layers of SuperPoint (small CNN, INT8) fit on a mid-range FPGA. This is what NVIDIA's Hailo-8 and similar CNN accelerators do. FPGA/ASIC with bespoke CNN systolic array.

**What FPGA cannot do**: Transformer attention at VIO scale. The attention matrix for a 1280×720 image divided into 16×16 patches is 3600×3600 — requires 52MB just for the attention scores. No FPGA has that on-chip. Off-chip access makes it memory-bandwidth-bound in a way that's architecturally ugly.

**What FPGA can partially do**: Mamba/SSM-based VIO (SS-VIO). State space models are *streaming* — they update a fixed-size state per timestep, not a growing attention matrix. This maps to FPGA recurrence well. An SSM-VIO accelerator is architecturally feasible on a high-end FPGA; a transformer-VIO accelerator is not.

### 7.3 SNN on FPGA

**Better than ANN, but not natural.** The operations are:
1. For each neuron per timestep: multiply membrane potential by decay (1 multiply), add weighted input if spike received (1 multiply + 1 add, but only ~20% of the time)
2. Compare against threshold (1 compare)
3. Send spike or not (1-bit output)

The sparsity is the key. A 100K-neuron SNN with 20% firing rate and 32 timesteps processes 640K spike events per inference. Each event costs ~4-8 LUTs. Total: ~5M LUTs equivalent — fits on a mid-range FPGA.

**The problem**: Standard FPGA architectures (DSP blocks) are optimized for dense MACs. Sparse spike routing requires custom interconnect. Intel Loihi's mesh routing is specifically designed for this; FPGA requires custom fabric, which wastes resources.

**FPGA SNN efficiency**: ~10-50x worse than custom neuromorphic silicon for the same SNN workload. Good enough for a prototype; not good enough for a product power target.

### 7.4 Hardware Mapping Summary

| Algorithm | GPU | FPGA | Neuromorphic ASIC | Best fit |
|-----------|:---:|:----:|:-----------------:|----------|
| Classical FAST+LK+ORB | Poor | ★★★★★ | Poor | FPGA/ASIC |
| SuperPoint (CNN only) | ★★★ | ★★★★ | ★★ | FPGA or Hailo |
| RAFT optical flow | ★★★★ | ★★ | ★ | GPU |
| SSM-VIO (Mamba) | ★★★ | ★★★ | ★★ | FPGA (feasible) |
| Transformer VIO | ★★★★ | ★ | ★ | GPU only |
| DPVO (RNN patches) | ★★★ | ★★ | ★★ | GPU (today) |
| SNN ego-motion | Poor | ★★★ | ★★★★★ | Neuromorphic |
| SNN optical flow | Poor | ★★★ | ★★★★★ | Neuromorphic |
| Event+ESVO2 (geometric) | ★★ | ★★★★ | ★★ | FPGA |

---

## 8. The VIO-Specific Insight: Where Each Paradigm Belongs

The key insight that the competitive analysis in other documents misses: **VIO is a heterogeneous pipeline**. No single paradigm is best for all components. The right architecture is a *hybrid*.

### 8.1 VIO Components and Their Natural Homes

```
┌─────────────────────────────────────────────────────────────────┐
│                VIO PIPELINE — PARADIGM FIT                      │
├───────────────────────┬────────────┬──────────────────────────┐│
│ Component             │ Best Para- │ Why                      ││
│                       │ digm       │                          ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ Event camera          │ SNN        │ Same data format: sparse,││
│ denoising/filtering   │            │ asynchronous, temporal   ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ Feature detection     │ Classical  │ Deterministic, data-     ││
│ (FAST / Harris)       │ or learned │ parallel; SuperPoint     ││
│                       │ CNN        │ better in hard scenes    ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ Optical flow /        │ Classical  │ LK is FPGA-perfect;      ││
│ feature tracking      │ (LK)       │ SNN for event cameras    ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ Descriptor extraction │ Classical  │ ORB trivially parallel,  ││
│                       │            │ SuperPoint only if HDR   ││
│                       │            │ scenes needed            ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ Temporal integration  │ SNN /      │ Natural LIF dynamics for ││
│ (event accumulation,  │ SSM        │ time-surface generation; ││
│ time surface)         │            │ SSM for sequential flow  ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ IMU preintegration    │ Classical  │ Fixed math, <20 DSPs,    ││
│                       │            │ negligible power         ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ State estimation      │ Classical  │ EKF/factor graph:        ││
│ (EKF / GTSAM)         │ with       │ geometric, reliable,     ││
│                       │ learned    │ interpretable. Learned   ││
│                       │ uncertainty│ covariance (MAC-VO) adds ││
│                       │            │ robustness               ││
├───────────────────────┼────────────┼──────────────────────────┤│
│ Failure detection /   │ SNN /      │ Low-power continuous     ││
│ quality monitoring    │ learned    │ monitoring (1mW budget)  ││
└───────────────────────┴────────────┴──────────────────────────┘│
```

### 8.2 Why Full SNN VIO Is Harder Than It Looks

The TU Delft and UZH demonstrations are impressive but deceptive. They show SNN doing *reactive control*, not *state estimation*.

The core of VIO is solving a **nonlinear optimization problem** (bundle adjustment, EKF matrix inversion) that has no obvious SNN formulation. The ANN approaches (DPVO, DROID-SLAM) embed differentiable optimization *inside* the network, which is why they work — but this requires floating-point precision and regular memory access, exactly what SNNs don't provide.

**The geometric computation gap**: A Cholesky decomposition of a 15×15 covariance matrix requires full floating-point precision. A spiking neuron emitting 0 or 1 cannot represent this. The hybrid approaches (NeuroVIO) address this by using classical or ANN components for the backend and SNN for the frontend. This is architecturally sound but means the SNN isn't replacing all the compute.

### 8.3 Where SNNs Have a Natural Advantage

Two VIO sub-problems are genuinely SNN-friendly:

**1. Event camera processing (the real opportunity)**

The event camera's native output is `(x, y, timestamp, polarity)` — a sparse stream of binary events. This is *directly* the SNN's input format. No conversion. No frame reconstruction. No batching.

A classical pipeline must reconstruct event frames (time surfaces, voxel grids) to feed convolutions — losing the temporal advantage. An SNN processes each event as it arrives, maintaining the microsecond timing that is the event camera's core advantage.

**2. Temporal integration and adaptive thresholds**

LIF neurons naturally integrate over time, decaying old evidence and accumulating new. For tracking features across a variable-rate event stream, this is exactly the right operation. The neuron's membrane potential is a continuous-time tracker — no need to explicitly define "frame" boundaries.

---

## 9. Implications for the Accelerator Product

### 9.1 What This Means for Architecture Choice

Given the analysis above, three architectures are technically coherent:

**Option A: Classical Accelerator (Near-term, proven)**

Accelerate FAST + LK + ORB + IMU preintegration on FPGA. This is the MIT Navion approach. Proven hardware fit, proven algorithms, 10-50x power improvement over CPU. The gap: no ANN robustness for hard lighting/texture conditions.

- FPGA resources: ~80K LUTs, 3MB BRAM, 200 DSPs (ZU15EG: 36%, 52%, 19%)
- Power: ~2W (FPGA fabric)
- Accuracy: matches ORB-SLAM3 in normal conditions, degrades in hard conditions
- **Time to prototype: 6-9 months**

**Option B: Hybrid Classical + Learned Front-End (Medium-term, differentiated)**

Add SuperPoint inference accelerator as a drop-in replacement for FAST when quality demands it. Keep LK for tracking (hardware-friendly), use SuperPoint only for keyframe detection.

- Additional resources: ~50K LUTs for CNN accelerator, 10-20MB weights (Lattice BRAM or external flash)
- Power impact: +200mW for CNN accelerator
- Accuracy: significant improvement in challenging lighting/texture
- **Time to prototype: 9-15 months**

**Option C: Event Camera + Geometric Pipeline (Maximum differentiation)**

Add event camera interface (Prophesee MIPI) and ESVO2-compatible time surface generator. This enables the power advantage of event cameras without requiring SNN maturity.

- Additional resources: MIPI PHY (use Lattice CrossLink-NX), time surface BRAM (~100KB), event corner detector
- Power: event camera (10mW) + processing (~500mW FPGA) = 510mW total
- Accuracy: comparable to frame-based in most conditions, superior at high speed / HDR
- **Time to prototype: 12-18 months**

**Option D: SNN Front-End (Long-term, disruptive, unproven)**

Replace feature tracking with SNN on neuromorphic silicon (Loihi 3 when commercial, or custom SNN FPGA IP). Keep classical/ANN back-end.

- Requires SNN training infrastructure (Python + Lava or Norse)
- Accuracy not yet proven for VIO sub-tasks
- Power: potentially sub-100mW for front-end
- **Time to prototype: 18-30 months, dependent on Loihi 3 commercial availability**

### 9.2 What Not to Build

**Full SNN VIO**: Nobody has published results. The backend geometric computation doesn't map to SNN. Attempting this today is a research project, not a product.

**Transformer VIO on FPGA**: The attention memory requirements are architecturally incompatible. DPVO/DROID-SLAM require GPU-class hardware. Don't try to put these on an FPGA without a major architectural redesign (Mamba/SSM is the right research direction).

**Pure SNN without event camera**: SNN's advantage over ANN is sparse, event-driven processing. Feeding frame-based images into an SNN requires conversion that loses both the efficiency and accuracy advantages. SNN without event camera is neither efficient nor accurate.

### 9.3 The Two-Year Technology Horizon

By 2027-2028, expect:

- **SSM-VIO on FPGA will be feasible**: Mamba-based VIO is computationally tractable for FPGA. This is the path to learned robustness + embedded power.
- **Intel Loihi 3 commercial availability**: Enables SNN prototype integration without custom silicon. The Q3 2026 commercialization (healthcare/AV target) may include an SDK accessible for drone research.
- **SNN VIO accuracy proof points**: NeuroVIO and follow-on papers will establish baseline SNN VIO accuracy. If they publish within 10% of ORB-SLAM3, the path to productization opens.
- **Prophesee HD sensor successor**: IMX636 is 1280×720. A next-generation part may push resolution and reduce cost.

**The window**: The classical accelerator gap is open today. The hybrid + event camera opportunity opens in 2026-2027. Full SNN is a 2028+ story. Starting with Option A (classical) or Option B (hybrid) now preserves optionality to layer in Options C and D.

---

## 10. Key Uncertainties

These are the questions that most affect the product thesis and lack published answers:

| Question | Why It Matters | When We'll Know |
|----------|---------------|-----------------|
| Can surrogate-trained SNNs match ANN accuracy on VIO? | Determines whether SNN is ever a drop-in replacement | NeuroVIO follow-on (2026-2027) |
| What is SSM-VIO power on FPGA at 720p? | Determines if learned robustness + embedded power is achievable | SS-VIO implementation study needed |
| Does Loihi 3 have a public SDK and event camera interface? | Determines SNN prototyping path | Intel Q3 2026 commercialization details |
| What is the SNN ego-motion accuracy in m/s (not just qualitative)? | Determines if it's competitive with classical IMU fusion | TU Delft follow-on publications |
| Can MAC-VO run on sub-2W hardware? | 12.5fps @ 480p is encouraging — what hardware? | MAC-VO embedded port (open research) |

---

## 11. Sources

### Deep Learning VIO
- [DPVO: Deep Patch Visual Odometry — NeurIPS 2023](https://arxiv.org/abs/2208.04726)
- [DPVO-QAT++: Heterogeneous Quantization 2025](https://arxiv.org/html/2511.12653)
- [DROID-SLAM — ICCV 2021](https://arxiv.org/abs/2108.10869)
- [TartanVO: Generalizable Learning-based VO](https://arxiv.org/abs/2011.00359)
- [MAC-VO: ICRA 2025 Best Paper](https://arxiv.org/abs/2409.09479)
- [MAC-VO GitHub](https://github.com/MAC-VO/MAC-VO)
- [Mix-VIO: Hybrid Tracking — PMC 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11358903/)
- [NeuFlow: 10x faster optical flow](https://arxiv.org/html/2403.10425v1)
- [SS-VIO: Mamba-based VIO — RAL 2026](https://ui.adsabs.harvard.edu/abs/2026IRAL...11.2010Q/abstract)
- [Learning-based VIO Survey](https://github.com/KwanWaiPang/Awesome-Learning-based-VO-VIO)

### SNN VIO and Neuromorphic Navigation
- [NeuroVIO: Hybrid ANN+SNN for VIO — OpenReview 2025](https://openreview.net/forum?id=hI7i4ncgXe)
- [Neuromorphic Resonator Networks — Nature Machine Intelligence 2024](https://www.nature.com/articles/s42256-024-00846-2)
- [TU Delft Autonomous Neuromorphic Drone](https://mavlab.tudelft.nl/fully_neuromorphic_drone/)
- [ESVO2: Event-Based Stereo VO](https://arxiv.org/html/2410.09374v1)
- [Data-driven Feature Tracking for Events — UZH 2024](https://rpg.ifi.uzh.ch/docs/Arxiv24_Messikommer.pdf)
- [Application of Event Cameras and Neuromorphic Computing to VSLAM — PMC 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11274992/)

### SNN Architecture and Training
- [Surrogate Gradient Learning — Zenke Lab 2024](https://zenkelab.org/2024/04/elucidating-the-theoretical-underpinnings-of-surrogate-gradient-learning-in-spiking-neural-networks/)
- [STDP-based Learning Review 2025](https://www.researchgate.net/publication/386735895_Modulated_Spike-Time_Dependent_Plasticity_STDP-based_Learning_for_Spiking_Neural_Network_SNN_A_review)
- [SNN Survey — ioe 2025](https://www.oejournal.org/ioe/article/doi/10.29026/ioe.2025.250007)
- [Adaptive and Lightweight Surrogate Gradients 2026](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2026.1795946/full)
- [Hybrid Spiking Vision Transformer — ICML 2025](https://arxiv.org/html/2505.07715v1)

### Hardware Energy
- [AI integrated circuits: GPU vs FPGA vs ASIC comparison 2024](https://www.researchgate.net/publication/372209945_Artificial-Intelligence_integrated_circuits_Comparison_of_GPU_FPGA_and_ASIC)
- [MIT Navion: 24mW VIO ASIC](https://eems.mit.edu/wp-content/uploads/2018/12/2019_jssc_navion.pdf)
- [eSLAM: Energy-Efficient ORB-SLAM FPGA](https://arxiv.org/abs/1906.05096)
- [FPGA-Based Feature Extraction for SLAM — PMC 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10574966/)
