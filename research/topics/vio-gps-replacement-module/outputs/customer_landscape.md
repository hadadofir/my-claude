# Customer Landscape - Drone Navigation Market

> Profiles of potential customers for VIO/SLAM acceleration IP

**Generated**: 2026-01-25
**Focus**: Commercial-first, defense later
**Confidence**: HIGH (public information)

---

## Table of Contents

1. [Market Segments](#market-segments)
2. [Commercial Drone Platforms](#commercial-drone-platforms)
3. [Industrial/Inspection Specialists](#industrialinspection-specialists)
4. [Defense Players](#defense-players)
5. [Component/IP Buyers](#componentip-buyers)
6. [Customer Prioritization](#customer-prioritization)

---

## Market Segments

```
                        VOLUME
                          ▲
                          │
    Consumer/Prosumer ────┼──────────────────── HIGH (millions)
                          │     (DJI dominates, hard to enter)
                          │
    Commercial/Enterprise─┼──────────────────── MEDIUM (100Ks)
                          │     ★ SWEET SPOT ★
                          │     (Skydio, Auterion, Flyability)
                          │
    Defense ──────────────┼──────────────────── LOW (10Ks)
                          │     (High margins, long cycles)
                          │     (Shield AI, AeroVironment)
                          │
                          └────────────────────────────────► MARGIN
                               LOW              HIGH
```

---

## Commercial Drone Platforms

### Skydio

| Attribute | Details |
|-----------|---------|
| **HQ** | San Mateo, CA |
| **Valuation** | ~$2.2B (2023) |
| **Focus** | Autonomous drones for enterprise & defense |
| **Key Products** | X10, X10D (defense), X2 series |

**Navigation Technology**:
- Proprietary Visual Inertial Odometry (VIO)
- AI-based obstacle avoidance with 6 fisheye cameras
- GPS-denied navigation via "Anchor Points" (visual reference)
- NightSense for autonomous flight in darkness

**Compute Platform**:
- NVIDIA Jetson Orin for AI compute
- Previously: Jetson TX2

**GPS-Denied Capabilities**:
- VIO at high altitudes (several km)
- Indoor operation without GPS
- Automatic transition between GPS and VIO modes

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | MEDIUM - Already strong, but power-hungry |
| Openness to external IP | LOW - Vertically integrated |
| Volume | HIGH - Enterprise + defense |
| Strategic value | HIGH - Validation partner |

**Approach**: Difficult to sell IP to; they build internally. Better as benchmark/validation. Could be acquirer if successful.

---

### ModalAI

| Attribute | Details |
|-----------|---------|
| **HQ** | San Diego, CA |
| **Background** | Spun out of Qualcomm (2018) |
| **Focus** | Drone/robot compute platforms |
| **Key Products** | VOXL 2, Starling drone, Sentinel |

**Navigation Technology**:
- Software VIO on Qualcomm QRB5165
- 15 TOPS NPU for AI
- Blue UAS Framework compliant (NDAA)

**Compute Platform**:
- Qualcomm Snapdragon (exclusive focus)
- 16g VOXL 2 SOM

**GPS-Denied Capabilities**:
- VIO development drones available
- Software-based, runs on main processor

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | HIGH - VIO competes for CPU cycles |
| Openness to external IP | HIGH - Platform company, integrates components |
| Volume | MEDIUM - Sells to other drone makers |
| Strategic value | VERY HIGH - Multiplier effect |

**Approach**:
- **Primary target for IP licensing**
- Their customers need better VIO
- FPGA add-on module or IP for future VOXL
- Could co-develop, they provide Qualcomm integration

---

### Auterion

| Attribute | Details |
|-----------|---------|
| **HQ** | Zurich, Switzerland / USA |
| **Focus** | Enterprise drone software (PX4-based) |
| **Key Products** | AuterionOS, Skynode, Mission Control |

**Navigation Technology**:
- PX4 autopilot (open source core)
- Software-based state estimation
- Integrates with various hardware

**Compute Platform**:
- Skynode: Integrated flight computer + mission computer
- ARM-based processors

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | MEDIUM - Software focus |
| Openness to external IP | HIGH - Integration-focused |
| Volume | MEDIUM - Enterprise customers |
| Strategic value | HIGH - PX4 ecosystem influence |

**Approach**: Software partnership first, hardware later. They influence PX4 ecosystem widely.

---

## Industrial/Inspection Specialists

### Flyability

| Attribute | Details |
|-----------|---------|
| **HQ** | Lausanne, Switzerland |
| **Focus** | Confined space inspection drones |
| **Key Products** | Elios 3 (LiDAR + collision-tolerant) |

**Navigation Technology**:
- **FlyAware™**: Proprietary SLAM engine
- LiDAR + 3 optical cameras
- Real-time 3D mapping during flight
- SLAM-based stabilization

**Compute Platform**:
- NVIDIA GPU for processing
- Embedded LiDAR processing

**GPS-Denied Capabilities**:
- **100% GPS-denied operation** (core use case)
- Indoor, confined spaces
- Centimeter-accurate positioning

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | HIGH - GPS-denied is their entire market |
| Openness to external IP | MEDIUM - Have internal tech but not compute experts |
| Volume | MEDIUM - Industrial niche |
| Strategic value | HIGH - Perfect use case validation |

**Approach**:
- Strong fit for event-based vision (HDR environments in industrial settings)
- Power efficiency = longer inspection time
- Could provide real-world test environments

---

### Corvus Robotics

| Attribute | Details |
|-----------|---------|
| **HQ** | Boston, MA |
| **Background** | MIT spinout, YC-backed |
| **Focus** | Warehouse inventory drones |
| **Key Products** | Corvus One autonomous drone |

**Navigation Technology**:
- **First learning-based autonomy stack** for indoor aerial robots
- 14 cameras + neural networks
- No GPS, no WiFi beacons, no human operators
- Computer vision for navigation + inventory scanning

**Compute Platform**:
- Custom embedded system
- Edge + cloud processing options

**GPS-Denied Capabilities**:
- **Fully GPS-denied by design**
- Operates in "lights-out" warehouses
- 1-week deployment in 1M sq ft facilities

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | HIGH - Navigation is core differentiator |
| Openness to external IP | MEDIUM - Have strong internal team |
| Volume | HIGH - Warehouse market is huge |
| Strategic value | HIGH - Cutting-edge use case |

**Approach**:
- Event cameras could help in varying warehouse lighting
- Power efficiency = longer autonomous operation
- May prefer to build internally (MIT DNA)

---

## Defense Players

### Shield AI

| Attribute | Details |
|-----------|---------|
| **HQ** | San Diego, CA |
| **Valuation** | $5.6B (2025) |
| **Focus** | AI pilots for military aircraft |
| **Key Products** | Hivemind AI, V-BAT, Nova 2, X-BAT |

**Navigation Technology**:
- **Hivemind**: AI pilot software
- Visual odometry for GPS-denied operation
- First AI-piloted drone in combat (2018, Nova)

**Compute Platform**:
- Custom embedded systems
- Hivemind Edge for edge AI

**GPS-Denied Capabilities**:
- **Combat-proven GPS-denied operation**
- V-BAT swarms without GPS/comms
- Visual odometry navigation

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | HIGH - GPS-denied is critical |
| Openness to external IP | LOW-MEDIUM - Build internally, but scale demands help |
| Volume | MEDIUM - Defense scale |
| Strategic value | VERY HIGH - Defense validation |

**Approach**:
- Long sales cycle (2-3 years minimum)
- Need proven commercial track record first
- Clearances required for deep engagement
- Could be acquirer

---

### AeroVironment

| Attribute | Details |
|-----------|---------|
| **HQ** | Arlington, VA |
| **Revenue** | ~$540M (FY2023) |
| **Focus** | Small UAS for defense |
| **Key Products** | Puma, Switchblade, JUMP 20 |

**Navigation Technology**:
- **Puma VNS**: Visual Navigation System (2022)
- VIO + Laser Altimeter Terrain Matching
- Automatic GPS/VIO mode switching
- **ARK**: Autonomy Retrofit Kit with edge compute

**Compute Platform**:
- Embedded compute modules
- SPOTR-Edge computer vision software

**GPS-Denied Capabilities**:
- Puma VNS for GPS-contested environments
- Down-looking sensors + embedded compute
- Extended to Puma LE (Long Endurance)

**Potential Fit**:
| Factor | Assessment |
|--------|------------|
| Need for better VIO | HIGH - Active development (VNS) |
| Openness to external IP | MEDIUM - Traditional defense, but ARK shows openness |
| Volume | HIGH - Large defense contracts |
| Strategic value | HIGH - Established defense prime |

**Approach**:
- More traditional defense procurement
- ARK/AVACORE shows interest in modular autonomy
- Could license VIO IP for next-gen products
- Requires defense market positioning

---

## Component/IP Buyers

### Qualcomm

| Attribute | Details |
|-----------|---------|
| **Relevance** | Provides chips to ModalAI, others |
| **Products** | QRB5165, Snapdragon Flight |

**Potential Fit**:
- Could integrate VIO IP into future Snapdragon for drones
- Long sales cycle, large NRE
- Would need proven IP with traction

**Approach**: Later-stage opportunity. Get design wins with ModalAI first, then approach Qualcomm for integration.

---

### NVIDIA

| Attribute | Details |
|-----------|---------|
| **Relevance** | Jetson platform dominates robotics |
| **Products** | Jetson Orin, cuVSLAM |

**Potential Fit**:
- Already have cuVSLAM (GPU-based)
- Unlikely to license external VIO
- Potential acquirer if event-based proves superior

**Approach**: Compete, don't partner. Target customers who need lower power than Jetson.

---

### Event Camera Vendors

#### Prophesee

| Attribute | Details |
|-----------|---------|
| **HQ** | Paris, France |
| **Focus** | Event-based vision sensors |
| **Products** | Metavision EVK4, GenX320 |

**Potential Fit**:
- **Natural partner for neuromorphic VIO**
- They sell sensors, need processing solutions
- Already partner with Sony, BrainChip, SynSense
- DoD contracts (defense pathway)

**Approach**:
- **High-priority partnership**
- Joint reference design: Prophesee sensor + your VIO IP
- They bring sensor expertise, you bring processing
- Access to their defense relationships

---

## Customer Prioritization

### Tier 1: Immediate Targets (Year 1)

| Company | Why | Approach |
|---------|-----|----------|
| **ModalAI** | Platform company, multiplier effect | IP licensing for VOXL ecosystem |
| **Prophesee** | Sensor partner, joint value | Co-development, reference design |
| **Flyability** | Perfect GPS-denied use case | Pilot project, validation |

### Tier 2: Medium-Term (Year 2-3)

| Company | Why | Approach |
|---------|-----|----------|
| **Auterion** | PX4 ecosystem influence | Software integration first |
| **Corvus Robotics** | Cutting-edge warehouse use | Technical collaboration |
| **AeroVironment** | Defense bridge | ARK integration opportunity |

### Tier 3: Long-Term (Year 3+)

| Company | Why | Approach |
|---------|-----|----------|
| **Shield AI** | Defense validation | Requires clearances, track record |
| **Skydio** | Market leader validation | Difficult, but valuable if achieved |
| **Qualcomm** | SoC integration | Requires proven traction |

---

## Key Relationships to Build

### Technical Validation Partners
1. **University of Zurich RPG** - Leading event-based VIO research
2. **MIT EEMS Lab** - Navion creators
3. **HKUST Aerial Robotics** - VINS-Mono, ESVO creators

### Ecosystem Partners
1. **Prophesee** - Event camera supply + joint development
2. **AMD/Xilinx** - FPGA reference designs
3. **PX4/Dronecode** - Open source integration

### Industry Validation
1. **Flyability** or similar - Real-world GPS-denied testing
2. **Warehouse operator** - High-volume commercial validation

---

## Summary: Go-to-Market Sequence

```
Year 1:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Prophesee   │────→│ Reference   │────→│ ModalAI     │
│ Partnership │     │ Design      │     │ Integration │
└─────────────┘     └─────────────┘     └─────────────┘

Year 2:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Flyability  │────→│ Commercial  │────→│ Auterion    │
│ Pilot       │     │ Validation  │     │ PX4 Ecosys  │
└─────────────┘     └─────────────┘     └─────────────┘

Year 3+:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Defense     │────→│ AeroVironment│───→│ Shield AI   │
│ Positioning │     │ ARK Integ   │     │ Hivemind    │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Sources

- [Skydio Autonomy](https://www.skydio.com/skydio-autonomy)
- [Skydio X10D](https://www.skydio.com/x10d)
- [ModalAI VOXL 2](https://www.modalai.com/products/voxl-2)
- [Auterion Enterprise PX4](https://auterion.com/bringing-px4-to-enterprise-users/)
- [Flyability Elios 3](https://www.flyability.com/elios-3)
- [Corvus Robotics - MIT News](https://news.mit.edu/2024/corvus-autonomous-drones-precisely-track-warehouse-inventories-1220)
- [Shield AI Hivemind](https://shield.ai/hivemind-for-operational-read-and-react-swarming/)
- [AeroVironment Puma VNS](https://www.avinc.com/resources/press-releases/view/aerovironment-introduces-puma-vns-a-visual-based-navigation-system-that-enables-gps-denied-navigation-across-gps-contested-environments)
- [Prophesee Event-Based Vision](https://www.prophesee.ai/)
