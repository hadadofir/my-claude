# Defense Drone Accelerators

> Identifying disruptive accelerator chip opportunities in the defense drone market

**Status**: In Progress
**Started**: 2026-01-25
**Last Updated**: 2026-05-07
**Tags**: #technical #deep-dive #hardware #defense #drones

---

## Research Question

What compute-intensive bottlenecks in defense drones present opportunities for a disruptive accelerator chip design?

### Sub-questions
1. What are the primary compute workloads in modern defense drones?
2. Where are current solutions (GPUs, FPGAs, existing ASICs) falling short?
3. What emerging capabilities are compute-limited today?
4. What unique constraints exist (power, latency, size, thermal, radiation)?
5. Where is the market heading that hardware hasn't caught up with?

## Scope

### In Scope
- Autonomous navigation and SLAM
- Computer vision (detection, tracking, classification)
- Sensor fusion (radar, lidar, EO/IR, CF)
- Swarm coordination and communication
- Electronic warfare (jamming, anti-jamming, signal processing)
- Edge AI inference
- Cryptographic processing
- Real-time decision making

### Out of Scope
- Propulsion and mechanical systems
- Non-compute aspects of drone design
- Offensive weapon systems (focus on sensing/decision, not actuation)
- Large UAVs (focus on tactical/small drones where SWaP matters most)

## Key Takeaways

1. **Neuromorphic VIO is the disruptive opportunity** - Event cameras + SNN processing = 25-100x power reduction. Gap: nobody has productized integrated solution
2. **Commercial-first strategy recommended** - No defense contacts, so prove IP in commercial drones (ModalAI, Flyability) before defense entry
3. **FPGA IP path is optimal** - Lower NRE ($1-3M vs $30-50M ASIC), faster iteration, matches market reality
4. **Partner with Prophesee** - Event camera vendor, joint reference design creates mutual value
5. **Target customers**: ModalAI (platform, IP licensing), Flyability (GPS-denied validation), Prophesee (sensor partnership)

## Confidence Assessment

| Aspect | Confidence | Notes |
|--------|------------|-------|
| Market landscape | HIGH | Well-documented funding trends, public startup valuations |
| Technical bottlenecks | MEDIUM-HIGH | Validated against academic and industry sources |
| Opportunity identification | MEDIUM | Initial opportunities were over-rated; critic review added realism |
| Go-to-market path | MEDIUM-LOW | Defense market access requires customer validation |

## Target Output

Specific accelerator chip concept(s) with:
- Clear problem statement
- Technical approach
- Differentiation from existing solutions
- Market timing rationale

## Outputs

- [Summary](./outputs/summary.md) - Overall research findings (updated May 2026)
- [Neuromorphic VIO Deep Dive](./outputs/neuromorphic_vio_deep_dive.md) - Event cameras + SNN architecture
- [VIO/SLAM Technical Architecture](./outputs/vio_slam_technical_architecture.md) - RTL block breakdown
- [Customer Landscape](./outputs/customer_landscape.md) - ModalAI, Skydio, Flyability, Shield AI profiles
- [Competitive Deep Dive v3](./outputs/competitive_deep_dive_v3.md) - **Latest**: Q1-Q2 2026 (May 2026)
- [Competitive Deep Dive v2](./outputs/competitive_deep_dive_v2.md) - Jan 2026 analysis
- [Neuromorphic vs ANN VIO Deep Dive](./outputs/neuromorphic_vs_ann_vio_deep_dive.md) - SNN vs deep learning vs classical — computation models, MAC counts, hardware fit
- [SNN Mathematics and Demo](./outputs/snn_mathematics_and_demo.md) - **New**: LIF math, surrogate gradients, working demo code, KV260 deployment
- [FPGA Board Selection](./outputs/fpga_board_selection.md) - KV260 selection + prototype plan

## Sources

See [sources/](./sources/) folder:
- `landscape_research.md` - Initial market research
- `opportunity_analysis.md` - Opportunity scoring
- `commercial_first_strategy.md` - Go-to-market strategy

## Resume

If continuing later, read [CONTEXT_RESUME.md](./CONTEXT_RESUME.md) for full context.
