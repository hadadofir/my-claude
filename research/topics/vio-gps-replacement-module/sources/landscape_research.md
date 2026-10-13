# Defense Drone Accelerators - Landscape Research

**Date**: 2026-01-25
**Phase**: Discovery

---

## Market Context

- Defense tech startups raised $17.9B in 2025 (up from $7.3B in 2024)
- Manufacturing-focused defense investment: $4.7B across 39 deals in 2025
- Key players: Anduril ($2.5B raise), Shield AI ($5.6B valuation), Helsing (€12B valuation)
- DARPA OPTIMA program: $78M for compute-in-memory accelerators

## Current Compute Solutions in Drones

### NVIDIA Jetson Ecosystem
- Jetson AGX Xavier: 22 TOPS, 512 CUDA cores, tensor cores
- Ruggedized versions: Curtiss-Wright DuraCOR
- Limitations: 30-45W power, heat dissipation challenges

### Alternatives
- **Qualcomm VOXL 2**: 15 TOPS NPU, 16g SOM, Blue UAS compliant
- **Google Coral TPU**: 4 TOPS @ 2W, TensorFlow Lite only
- **Intel Movidius Myriad X**: Good power efficiency, limited flexibility
- **AMD Xilinx Kria/Versal**: FPGA + AI cores, flexible but complex

### Key Constraint
- Military systems often limited to 100-200W per computer
- SWaP (Size, Weight, Power) drives all decisions
- Ruggedization adds cost and thermal challenges

## Compute-Intensive Workloads

### 1. Computer Vision / AI Inference
- Object detection, tracking, classification
- Current: 30ms-100ms latency typical
- Bottleneck: Power consumption vs. accuracy tradeoff

### 2. Visual-Inertial Odometry (VIO) / SLAM
- Real-time localization without GPS
- MIT Navion ASIC: 2mW for full VIO pipeline
- FPGA implementations: eSLAM reduces compute by 90%+
- Opportunity: GPS-denied navigation is critical for contested environments

### 3. Sensor Fusion
- Radar + EO/IR + RF + acoustic
- Current: GPU-based, high power, 50µs+ latency
- Challenge: Multi-vendor sensor alignment, timing

### 4. Electronic Warfare
- Cognitive radar: adaptive waveform generation
- Jamming detection and countermeasures
- FPGA preferred for <1µs latency requirements
- GPU better for ML-based threat classification

### 5. Swarm Coordination
- Consensus algorithms (adapted Raft, etc.)
- 120ms+ latency in complex environments
- Positioning errors: 2-5cm/minute without GPS
- Need: Low-latency mesh networking + distributed compute

### 6. Cryptography
- Post-quantum crypto needed for quantum-threat resilience
- Kyber (encryption) + Dilithium (signatures) are NIST standards
- Current implementations: ~0.08s authentication on RPi5
- Hardware acceleration shows promise for lattice-based operations

## Emerging Technologies

### Neuromorphic Computing
- Event cameras: 1000x less data than frame-based
- Spiking Neural Networks: fire only on change
- Intel Loihi 2: 50x faster, 100x less energy than GPUs
- BrainChip Akida: 1.2M neurons, edge SoC
- TU Delft drone: 64x faster than GPU, 3x less energy
- **Key insight**: Orders of magnitude efficiency gains for motion-based sensing

### Compute-in-Memory
- DARPA OPTIMA program targeting this
- EnCharge AI partnership with Princeton
- Reduces memory bandwidth bottleneck

## Latency Requirements by Application

| Application | Required Latency | Current Solution |
|-------------|------------------|------------------|
| Counter-UAS engagement | <100ms | GPU/FPGA hybrid |
| Cognitive radar adaptation | <1µs | FPGA only |
| Swarm consensus | <50ms | CPU/software |
| VIO update | <10ms | CPU/FPGA |
| PQC authentication | <100ms | CPU (slow) |
| Sensor fusion | <50ms | GPU |

## Key Pain Points (Opportunities)

1. **Power consumption**: GPUs consume 30-45W, batteries are limited
2. **GPS-denied operation**: VIO/SLAM is compute-intensive
3. **Swarm latency**: Software consensus is too slow for tight coordination
4. **Multi-sensor fusion**: No dedicated accelerator, relies on GPU
5. **PQC readiness**: Most drones have no quantum-resistant crypto
6. **Cognitive EW**: FPGA development is slow, ASICs could help
7. **Event-based sensing**: Neuromorphic hardware is nascent

## Sources

- [Real-Time Drone Data Processing with Edge Computing](https://anvil.so/post/real-time-drone-data-processing-with-edge-computing)
- [AI in deployed systems - Military Embedded Systems](https://militaryembedded.com/ai/machine-learning/ai-in-deployed-systems)
- [NVIDIA Jetson for Military - Curtiss-Wright](https://defense-solutions.curtisswright.com/media-center/blog/nvidia-jetson-military-aerospace)
- [Fitting AI under the SWaP umbrella](https://militaryembedded.com/ai/deep-learning/fitting-ai-under-the-swap-umbrella)
- [Drone Swarms as Networked Control Systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC8068910/)
- [FPGAs fuel military EW](https://militaryembedded.com/radar-ew/signal-processing/fpgas-fuel-military-electronic-warfare-cognitive-radio-and-radar-signal-processing-innovation)
- [Neuromorphic computing for robotic vision](https://www.nature.com/articles/s44172-025-00492-5)
- [Navion VIO ASIC](https://eems.mit.edu/wp-content/uploads/2018/12/2019_jssc_navion.pdf)
- [Counter-UAS detection survey](https://arxiv.org/html/2402.05909v2)
- [Post-quantum authentication for drone swarms](https://www.mdpi.com/2079-9292/14/17/3364)
- [Sensor fusion at tactical edge](https://militaryembedded.com/radar-ew/sigint/guest-blog-sensor-fusion-at-the-tactical-edge-why-gpus-are-essential-for-modern-c5isr-systems)
