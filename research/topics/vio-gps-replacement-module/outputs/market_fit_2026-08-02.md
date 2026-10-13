# Market Fit Assessment — VIO/FPGA GPS-Protocol-Compatible Nav Module

> Assessing MARKET FIT (not market size) for: FPGA-accelerated classical VIO/SLAM outputting a standard GPS-protocol signal (NMEA/UBX/MAVLink GPS_INPUT), <1W, "zero flight-stack integration" drop-in — Phase 1; event-camera+SNN — Phase 3.

**Generated**: 2026-08-02
**Builds on**: `outputs/summary.md` (esp. "2026-08-02 Validation Update"), `outputs/customer_landscape.md`, `sources/commercial_first_strategy.md`
**Confidence**: MEDIUM — public-source research only, no primary customer/procurement-officer interviews
**Method**: Web search, dated 2026-08-02, cross-checked against existing local research base

---

## Key Takeaways

1. **The procurement door is not closed, but it's more crowded than the prior research pass knew.** Theseus is not the only funded, DoD-integrated, vision-based GPS-denial vendor. A second, comparably-positioned competitor — **Vermeer** (US/Ukraine, formerly Aerocine, founded 2018, $17M+ raised including a $10M Series A led by Draper Associates, Oct 2025) — is combat-proven in Ukraine, holds Army/Air Force SBIR-AFWERX relationships, and is **"in use by" Lockheed Martin and Northrop Grumman**. This is a new finding not captured in the 2026-08-02 same-day validation update in `summary.md` and should be treated as at least as material as the Theseus finding.
2. **Direct-to-DoD via SBIR/AFWERX/APFIT is real and multi-vendor, not winner-take-all** — Theseus, Vermeer, ANELLO ($20M APFIT, Jan 2026), and OKSI/Cyberlux all received distinct DoD funding in the same ~18-month window. Early-stage prototype/SBIR funding is pluralistic; it is only at the **program-of-record production** stage (e.g., TRX Systems' $402M dismounted-PNT IDIQ, BAE's $318M sole-source M-code GPS card contract) that DoD consolidates around one or two vendors.
3. **No public unit pricing exists anywhere in this category** — not for Theseus, Vermeer, ANELLO, or OKSI. The closest proxies (ModalAI VOXL 2 companion computer, $1,299.99; Starling 2 dev drone, $2,949.99) describe general-purpose compute, not GPS-denial-specific hardware. Willingness-to-pay for this specific capability is unvalidated in public data.
4. **The SWaP math argues the FPGA <1W niche is real but narrower than the pitch implies.** True nano-drones (Crazyflie-class, 27-33g) need a sub-100-300mW *total* avionics budget — below even a <1W FPGA module's target, meaning that tier needs ASIC/SNN (Phase 3 territory), not FPGA (Phase 1). Group 1-2 tactical platforms where the pitch is aimed already fit Jetson-Orin-Nano-class (7-15W) or Qualcomm QRB5165-class (~5W) compute within their power budgets — so <1W FPGA is an efficiency/endurance improvement there, not a hard enabler. No SBIR/RFP was found explicitly naming an unserved "<1W but not sub-10mW" band — this remains supply-push reasoning, not demand-pull evidence.
5. **Market timing is genuinely favorable and accelerating** — AFRL's $49.68M alt-PNT contract (July 2026) states GPS degradation is now "an expected operating condition," not an exception; Congress's FY27 NDAA markup calls for a dedicated PNT overseer; GPS jamming/spoofing incident rates are rising sharply (spoofing reports "more than doubled" Jan–Jun 2025). But there is no hard equipage *mandate* yet (unlike the FY2006 NDAA GPS-equipage requirement) — momentum is programmatic, not statutory.
6. **"Commercial-first" does not serve as an on-ramp to this specific pitch.** The original commercial-first thesis (indoor warehouse/inspection GPS-denial, e.g. Corvus Robotics, Flyability) solves a different problem (no signal at all) already served adequately by existing software VIO. No evidence was found of commercial buyers paying for jam/spoof resilience specifically — even Vermeer's own "dual-use" marketing language has no named commercial pilot behind it. This proposal, as scoped, is inherently defense-first.

---

## 1. Buyer Segments & Procurement Channel

**Confidence: MEDIUM-HIGH** (multiple corroborating contract announcements, but no primary-source interviews with program offices)

| Channel | Evidence | Assessment |
|---|---|---|
| **Direct-to-startup via SBIR/AFWERX/APFIT** | Theseus sold to SOCOM ~6 months after a hackathon, units delivered for testing since Aug 2024 ([Defense Tech Signals](https://defensetechsignals.beehiiv.com/p/theseus)). Vermeer: $7M+ in SBIR/AFWERX awards prior to its Series A ([DroneLife](https://dronelife.com/2025/10/23/vermeer-secures-10-million-series-a-to-advance-gps-free-drone-navigation-for-defense-and-dual-use-applications/)). ANELLO: Navy Phase I + Army Phase II SBIR, then a **$20M APFIT award** (Jan 2026) explicitly to "fast-track procurement, production and scaling" ([UST](https://www.unmannedsystemstechnology.com/2026/01/anello-photonics-secures-20m-apfit-award-for-scaling-gps-denied-navigation/), [PR Newswire](https://www.prnewswire.com/news-releases/anello-photonics-awarded-20m-in-department-of-war-apfit-funding-to-accelerate-gps-denied-navigation-302667842.html)). | **This is the primary realistic entry channel for a new, unconnected startup** — confirmed pattern of DoD funding early-stage GPS-denial vendors directly, without a prime as intermediary. |
| **Integration through primes (component model)** | Vermeer's VPS is explicitly described as **"in use by U.S. defense organizations and major contractors including Lockheed Martin and Northrop Grumman"** ([DroneLife](https://dronelife.com/2025/10/23/vermeer-secures-10-million-series-a-to-advance-gps-free-drone-navigation-for-defense-and-dual-use-applications/), [TechUkraine](https://techukraine.org/2025/10/24/vermeer-the-us-ukrainian-startup-making-drones-immune-to-russian-ew-lands-10m-from-draper-associates/)). Shield AI's Hivemind (visual odometry-based autonomy) flies aboard Anduril's YFQ-44A under the USAF CCA program — a prime-to-prime component relationship ([Benzinga](https://www.benzinga.com/markets/private-markets/26/06/53235906/anduril-and-shield-ai-a-massive-bet-on-autonomous-warfare-or-the-next-ai-bubble)). | Confirms a second viable channel: **become a sub-component supplier to a prime's platform**, not just a direct DoD vendor. Consistent with prior `customer_landscape.md` Tier-3 assessment of AeroVironment/Shield AI as longer-cycle targets. |
| **Drone platform companies (ModalAI, Auterion, Skydio) as buyers of this specific capability** | No new evidence found of these companies buying a GPS-protocol-compatible anti-jam module specifically (as opposed to building VIO internally, per `customer_landscape.md`'s existing "vertically integrated" assessment of Skydio and "build internally" note for Shield AI). | **No update** to prior finding — still assessed as a difficult direct-IP-licensing sell; more useful as validation/benchmark partners. |
| **Single-source risk / "did Theseus close the door?"** | Theseus, Vermeer, ANELLO, and OKSI/Cyberlux all hold **separate, concurrent** DoD funding relationships as of Aug 2026 — this is not a single-vendor market. However, once a specific **program of record** forms, DoD does consolidate: TRX Systems holds a $402M/7-year sole production IDIQ for dismounted PNT (DAPS Gen II) ([PRWeb](https://www.prweb.com/releases/U_S_Army_Awards_TRX_Systems_402_Million_Production_Contract_for_DAPS_GEN_II/prweb19318883.htm)); BAE holds a $318M sole-source contract for M-code GPS cards ([DefenseScoop](https://defensescoop.com/2023/09/29/bae-scores-318m-army-gps-contract/)). | **Answer: the door is not closed, but the field is more crowded than believed.** Theseus's SOCOM relationship appears to still be at prototype/testing stage (no disclosed production IDIQ found), so no program of record has yet consolidated around a single vendor in the *vision-based* GPS-denial sub-category specifically — but Vermeer's Lockheed/Northrop integration and ANELLO's APFIT scaling award suggest that window is narrowing faster than the same-day validation pass (which only flagged Theseus) assumed. |

---

## 2. Willingness to Pay / Pricing Signals

**Confidence: LOW** — no confirmed unit pricing found for any direct competitor

| Data point | Value | Source | Notes |
|---|---|---|---|
| Theseus unit/system cost | No public figure. Qualitative claim only: "~10x more affordable than existing solutions" | [Fly Eye](https://www.flyeye.io/theseus-raises-4-3-million-for-gps-free-drone-navigation/) | Comparison baseline ("existing solutions") not specified — could mean full INS/optical-gyro systems, not FPGA modules. |
| Vermeer unit/system cost | Not disclosed | [DroneLife](https://dronelife.com/2025/10/23/vermeer-secures-10-million-series-a-to-advance-gps-free-drone-navigation-for-defense-and-dual-use-applications/) | — |
| ANELLO X3 IMU price | Not disclosed | [Defense Advancement](https://www.defenseadvancement.com/company/anello-photonics/anello-x3-imu/) | $20M APFIT is a production-scaling award, not a per-unit price signal. |
| OKSI OMNInav price | Not disclosed | [OKSI](https://oksi.ai/omninav-gps-denied-navigation/) | Spec known: 70×50×50mm, 300g, <5W. |
| ModalAI VOXL 2 (proxy: general-purpose companion compute, not GPS-denial-specific) | $1,299.99 (board only); $1,249.99 (Mini) | [ModalAI](https://www.modalai.com/products/voxl-2) | Best available public proxy for a "navigation/companion-compute" BOM line item at low-volume/dev-kit pricing. |
| ModalAI Starling 2 dev drone (companion compute + full airframe) | $2,949.99–$2,999.99 | [ModalAI](https://www.modalai.com/products/voxl-2) | Upper bound of what a small-drone developer currently pays for a compute+navigation platform at prototype volumes. |
| DAPS Gen II (comparable *program*, not comparable *product* — dismounted PNT, not vision-based) | $402M / 7-year IDIQ, full-rate production since Sep 2024 | [PRWeb](https://www.prweb.com/releases/U_S_Army_Awards_TRX_Systems_402_Million_Production_Contract_for_DAPS_GEN_II/prweb19318883.htm) | Shows DoD will commit large multi-year sums to a fielded PNT-alternative program — but doesn't reveal a per-unit price, and the product (wearable INS+M-code fusion) is not camera/VIO-based. |

**Assessment**: The category has real dollars flowing (APFIT, SBIR, AFWERX, Series A/B rounds), but **no evidence exists of a stable, disclosed per-unit price point** a buyer has committed to for this specific capability. This is consistent with an early, pre-commoditization market where money currently flows as R&D/scaling grants rather than repeat unit purchases — a mixed signal: real budget exists, but the proposal's own economics (can it profitably sell an FPGA module at a price a drone BOM will absorb) remain unvalidated by any public data point.

---

## 3. Is the FPGA Power/SWaP Niche Real and Sizable — or a Niche-Within-a-Niche?

**Confidence: MEDIUM** (strong technical/SWaP-math evidence; weak demand-pull evidence)

| Platform class | Power/SWaP reality | Does <1W FPGA uniquely fit? |
|---|---|---|
| **Nano-drones** (e.g. Crazyflie-class, 27-33g) | Total power budget 7-10W; avionics/compute allocation is typically **5-15% of total** — i.e. sub-100mW to 200-300mW for *all* sensing+compute+comms combined ([arXiv 2601.13252](https://arxiv.org/html/2601.13252v1), [UZH Palossi 64mW DNN engine](https://rpg.ifi.uzh.ch/docs/IoT19_Palossi.pdf)) | **No** — even <1W is too much. This tier needs ASIC (MIT Navion, 2mW) or SNN (Phase 3), not FPGA (Phase 1). Confirms the existing research's Phase 3 rationale but undercuts Phase 1's fit at the truly smallest platform tier. |
| **Loitering munitions / Group 1-2 tactical UAS** | Literature confirms "SWaP constraints exclude many sensor options" and terminal-accuracy/cruise-drift tradeoffs are real ([defenseadvancement.com](https://www.defenseadvancement.com/suppliers/gnss-gps-denied-navigation-positioning/)) | **Plausible but unconfirmed by a named solicitation.** No DARPA/SBIR RFP was found explicitly citing a sub-1W power ceiling as a requirement for this platform class. General-purpose compute (Jetson Orin Nano 7-15W, Qualcomm QRB5165 ~5W) already fits within most Group 1-2 power budgets — so FPGA acceleration here reads as an **endurance/margin improvement**, not a hard enabler. |
| **Small UGVs (tunnel/subterranean)** | Current published approaches use "low-power edge hardware" (general-purpose, not FPGA-specific) for LiDAR-inertial odometry ([arXiv 2603.04470](https://arxiv.org/html/2603.04470v1)) | **No direct evidence of an FPGA-specific unmet need**; existing solutions target edge GPU/CPU, not dedicated silicon. |
| **Wearables (dismounted soldier PNT)** | TRX DAPS Gen II is a real, funded ($402M), power-constrained, handheld/wearable program — but it fuses **M-code GPS + inertial + other PNT sources**, not camera/VIO ([Military Aerospace](https://www.militaryaerospace.com/sensors/article/14292424/positioning-navigation-and-timing-pnt-gps-denied-infantry)) | **Weak fit** — no camera-pointing use case for a handheld soldier device; this segment's SWaP constraint is real but the form factor doesn't match a VIO-based module. |
| **General SBIR solicitations found** | MDA SBIR (up to $314K, deadline Aug 19 2026) for "GPS-denied event-based navigation" for missile defense/space systems ([BW&CO](https://www.bwcoconsulting.com/fod/mda26bz04-nv008)) | Notably **event-based**, i.e. closer to the Phase 3 (event camera + SNN) framing than Phase 1 FPGA/classical-SLAM — a signal that DoD's stated interest in this direction is already skewing toward the neuromorphic end, not the classical-VIO-on-FPGA end. |

**Assessment**: The technical logic for a distinct FPGA <1W band is defensible (there is a real gap between "2mW ASIC-only" and "5-15W general-purpose compute is fine") but **no solicitation, RFP, or program requirement was found that names this specific band as underserved**. This is currently a supply-side thesis, not a demand-pull-validated one. It is best characterized as a **plausible niche-within-a-niche**, not yet an evidenced one.

---

## 4. Market Timing

**Confidence: MEDIUM-HIGH**

| Signal | Detail | Date | Source |
|---|---|---|---|
| AFRL alt-PNT maturation contract | $49,684,402 to Canyon Consulting LLC to mature multiple alt-PNT technologies (quantum inertial sensors, PULSAR LEO nav constellation, SATCOM-based PNT-as-a-Service); explicit framing that GPS degradation is now "an expected operating condition in future conflicts," not exceptional | Jul 6, 2026 | [corsstations.com](https://corsstations.com/news/air-force-expands-alternative-pnt-strategy-with-49-7-million-canyon-consulting-contract/) |
| FY27 NDAA markup — PNT overseer | House Armed Services Committee chairman's mark calls for a single designated Pentagon PNT official, citing "a concerning lack of clear direction" across the alt-PNT portfolio | May 26, 2026 | [Inside GNSS](https://insidegnss.com/house-armed-services-committee-calls-for-single-pnt-overseer-in-fy27-ndaa-markup/) |
| ANELLO APFIT award | $20M to fast-track procurement/production/scaling of GPS-denied nav tech | Jan 2026 | [UST](https://www.unmannedsystemstechnology.com/2026/01/anello-photonics-secures-20m-apfit-award-for-scaling-gps-denied-navigation/) |
| DAPS Gen II full-rate production | Confirms dismounted alt-PNT is already a program of record, not just interest | Since Sep 2024 | [PRWeb](https://www.prweb.com/releases/trx-systems-daps-gen-ii-system-now-shipping-to-the-us-army/) |
| GPS jamming/spoofing incident growth | ~700 jamming/spoofing events/day (2024 baseline, Secure World Foundation 2026 report); spoofing reports "more than doubled" Jan–Jun 2025 in business aviation | 2026 report | [RCR Wireless](https://www.rcrwireless.com/20260420/defense-communications/gps-jamming-attacks-threaten-critical-sectors) |
| Ukraine EW pressure | ~50% of Ukrainian FPV losses attributed to Russian jamming (2023 baseline); Pole-21 systems degrade GPS accuracy sector-wide (8m → 50m+ uncertainty) | Ongoing, 2026 reporting | [Drone Warfare](https://drone-warfare.com/2026/06/04/dwim-monthly-may-2026/) |
| Historical precedent for hard mandates | FY2006 NDAA Section 260 required GPS equipage on aircraft/ships/vehicles/indirect-fire systems bought after Sep 2007 | Historical | [GPS.gov](https://www.gps.gov/gps-legislation) |

**Assessment**: Momentum is real and accelerating on multiple independent axes (budget lines, contract awards, incident-rate data, Congressional attention) — favorable timing for a 2-3 year-old startup. However, **no equivalent hard equipage mandate for GPS-denial backup capability was found for FY26/27** (unlike the FY2006 GPS-equipage precedent). The push today is programmatic/budgetary (AFRL, APFIT, program-of-record growth) rather than statutory — a meaningfully strong tailwind, but not yet a forced-buy.

---

## 5. Does "Commercial-First" Still Make Sense for This Specific Proposal?

**Confidence: MEDIUM-HIGH**

- The original commercial-first strategy (`sources/commercial_first_strategy.md`) was built around **indoor/no-signal GPS-denial** (warehouse, inspection) — a fundamentally different problem from **anti-jam/anti-spoof resilience under adversarial RF conditions**. Corvus Robotics and Flyability's GPS-denial need is "there is no GPS signal at all here," solved adequately today by existing software VIO at acceptable power (no adversary, no urgency around power/SWaP beyond normal battery-life concerns).
- Commercial GPS interference is a growing but *distinct* phenomenon: "GPS disruptions affecting agriculture and construction operations have been detected," and business-aviation spoofing reports "more than doubled" Jan–Jun 2025 ([RCR Wireless](https://www.rcrwireless.com/20260420/defense-communications/gps-jamming-attacks-threaten-critical-sectors), [Undark](https://undark.org/2025/12/24/gps-attack-new-tech/)). This shows a real and growing commercial pain point exists in principle — but:
- **No evidence was found of a commercial buyer paying for, piloting, or requesting jam/spoof-resilient navigation specifically.** Even Vermeer — the most dual-use-postured competitor, with marketing language citing "urban air mobility to logistics and inspection operations" — has **no named commercial pilot or customer** behind that claim per available sources; it reads as aspirational positioning, not validated demand.
- Agricultural drones (~26% of the commercial drone market) depend on RTK/GPS precision, but the failure mode operators actually experience and budget for is *accuracy/reliability*, not adversarial jamming — a different sales conversation than "drop-in replacement for a jammed/spoofed GPS input."

**Assessment**: The "GPS-protocol-compatible drop-in, built for anti-jam/spoofing resilience" framing does **not** resonate with the commercial buyers profiled in the existing research (ModalAI, Auterion, Corvus, Flyability) — their GPS-denial problem and this proposal's anti-jam value proposition solve different problems for different reasons. **The proposal, as scoped in Phase 1, is inherently defense-first**, not a commercial-first play with a defense option later. This doesn't invalidate the original commercial-first customer_landscape.md work — it simply means that work describes a *different, still-viable* product (VIO/SLAM acceleration IP for indoor GPS-denial) rather than a stepping-stone to the anti-jam GPS-protocol module Yuda is now assessing.

---

## Market Fit Verdict

### **MODERATE**

**Reasoning:**

- **What argues for it**: The category is real, funded, and timing-favorable. Direct-to-DoD SBIR/AFWERX/APFIT channels are demonstrably open to multiple simultaneous vendors at the prototype/scaling stage (Theseus, Vermeer, ANELLO, OKSI all funded in the same window) — this is the channel a DoD-connected founder like Yuda is best positioned to use, and it is not winner-take-all in the near term. GPS-denial procurement momentum (AFRL $49.7M, ANELLO APFIT $20M, NDAA PNT-overseer push, rising jamming-incident data) is accelerating on a timescale relevant to a 2-3 year startup runway.
- **What argues against strong fit**: This research pass surfaced a competitor (Vermeer) at least as advanced and DoD/prime-integrated as Theseus, which the same-day 2026-08-02 validation update in `summary.md` had not yet found — the vision-based GPS-protocol-replacement category is more crowded than the existing research base currently reflects. The specific FPGA/<1W SWaP differentiation lacks demand-pull evidence (no RFP/solicitation found naming that band as underserved), and the SWaP math itself shows the truly power-starved tier (nano-drones) needs sub-300mW — below even the <1W target — while the tactical tier the pitch targets (Group 1-2, loitering munitions) mostly already accommodates Jetson/Qualcomm-class compute, making the FPGA advantage an efficiency margin rather than a hard unlock. No public pricing data validates the unit economics. And the commercial-first on-ramp does not work for this specific framing — it's a defense-first bet from day one, raising execution risk (this favors Yuda's DoD relationships, but narrows the path if those relationships don't convert quickly).
- **Net**: a real, moving, accessible-to-newcomers market — but the differentiation claim needs to be sharpened and re-tested against **two** funded direct competitors (not one), and the core "FPGA is uniquely necessary at this SWaP tier" claim needs a named buyer/solicitation before it should be treated as validated rather than plausible.

---

## What Would Change This Assessment

| Trigger | Action |
|---|---|
| A DARPA/SBIR/service solicitation is found explicitly citing a sub-1W (not sub-10mW, not "any low power") requirement for VIO/SLAM on a named platform class | Upgrades Q3 from "plausible" to "evidenced" — strengthens the FPGA-specific wedge materially |
| Theseus or Vermeer discloses a production-scale program of record (IDIQ, sole-source award) in the vision-based GPS-denial category | Signals the near-term window for a third/fourth vendor may be closing — reassess urgency and differentiation |
| Any competitor (Theseus, Vermeer, ANELLO, OKSI) discloses public unit pricing | Immediately re-run Q2 with real WTP data; may validate or kill the module's target price point |
| A named commercial buyer (agriculture, construction, survey, warehouse) is found piloting or paying for jam/spoof-resilient navigation specifically | Reopens the commercial-first path as a genuine on-ramp, not just a parallel product line |
| FY27 NDAA final text includes a hard GPS-denial-backup equipage mandate (vs. the current PNT-overseer coordination language) | Upgrades Q4 from "favorable momentum" to "forced-buy tailwind" — materially de-risks the market-timing bet |
| A third or fourth well-funded vision-based GPS-denial startup is found beyond Theseus/Vermeer/ANELLO/OKSI | Confirms this is now a genuine, crowding category — differentiation must be revisited as the central risk, not the market's existence |

---

## Sources

- [Theseus tests GPS-denied navigation system over 550 km flight](https://defence-blog.com/theseus-tests-gps-denied-navigation-system-over-550-km-flight/)
- [Theseus — Fighting When GPS Goes Dark | Defense Tech Signals](https://defensetechsignals.beehiiv.com/p/theseus)
- [Theseus Raises $4.3M to Develop GPS-Free Drone Navigation](https://technews180.com/funding-news/theseus-secures-4-3m-in-seed-funding/)
- [Theseus Raises $4.3 Million for GPS-Free Drone Navigation - Fly Eye](https://www.flyeye.io/theseus-raises-4-3-million-for-gps-free-drone-navigation/)
- [THESEUS — Micro VPS Technology](https://www.theseus.us/technology)
- [Vermeer Secures $10 Million Series A to Advance GPS-Free Drone Navigation for Defense and Dual-Use Applications - DroneLife](https://dronelife.com/2025/10/23/vermeer-secures-10-million-series-a-to-advance-gps-free-drone-navigation-for-defense-and-dual-use-applications/)
- [Vermeer, the US-Ukrainian Startup Making Drones Immune to Russian EW, Lands $10M from Draper Associates · TechUkraine](https://techukraine.org/2025/10/24/vermeer-the-us-ukrainian-startup-making-drones-immune-to-russian-ew-lands-10m-from-draper-associates/)
- [American-Ukrainian Defense Tech Startup Vermeer Reaches $10M in Total Series A Funding - PR Newswire](https://www.prnewswire.com/news-releases/american-ukrainian-defense-tech-startup-vermeer-reaches-10m-in-total-series-a-funding-following-draper-associates-led-extension-302592137.html)
- [ANELLO Photonics Secures $20M APFIT Award for Scaling GPS-Denied Navigation | UST](https://www.unmannedsystemstechnology.com/2026/01/anello-photonics-secures-20m-apfit-award-for-scaling-gps-denied-navigation/)
- [ANELLO Photonics Awarded $20M in Department of War APFIT Funding - PR Newswire](https://www.prnewswire.com/news-releases/anello-photonics-awarded-20m-in-department-of-war-apfit-funding-to-accelerate-gps-denied-navigation-302667842.html)
- [ANELLO X3 IMU | Defense Advancement](https://www.defenseadvancement.com/company/anello-photonics/anello-x3-imu/)
- [OMNInav by OKSI: A Breakthrough in GPS-Denied Navigation for UAS | Soldier Systems Daily](https://soldiersystems.net/2025/02/06/omninav-a-breakthrough-in-gps-denied-navigation-for-unmanned-aerial-systems-2/)
- [OMNInav: A Breakthrough in GPS-Denied Navigation for UAS - OKSI](https://oksi.ai/omninav-gps-denied-navigation/)
- [Cyberlux and OKSI Advance UAS Capabilities for GPS- and RF-Denied Environments - BusinessWire](https://www.businesswire.com/news/home/20250507811627/en/Cyberlux-and-OKSI-Advance-UAS-Capabilities-for-GPS--and-RF-Denied-Environments)
- [Cyberlux Corporation Reports Fiscal Year 2025 Annual Results](https://cyberlux.com/2025-annual-report/)
- [U.S. Army Awards TRX Systems $402 Million Production Contract for DAPS GEN II](https://www.prweb.com/releases/U_S_Army_Awards_TRX_Systems_402_Million_Production_Contract_for_DAPS_GEN_II/prweb19318883.htm)
- [TRX Systems DAPS GEN II System Now Shipping to the U.S. Army](https://www.prweb.com/releases/trx-systems-daps-gen-ii-system-now-shipping-to-the-us-army-301950361.html)
- [Hand-held navigation tool for US Army deemed effective against jamming - C4ISRNET](https://www.c4isrnet.com/electronic-warfare/2024/02/07/hand-held-navigation-tool-for-us-army-deemed-effective-against-jamming/)
- [BAE scores $318M Army GPS contract | DefenseScoop](https://defensescoop.com/2023/09/29/bae-scores-318m-army-gps-contract/)
- [Intermap Expands Role in GPS-Denied Navigation with Third DOD Research Contract - GlobeNewswire](https://www.globenewswire.com/news-release/2026/06/25/3317435/0/en/intermap-expands-role-in-gps-denied-navigation-with-third-dod-research-contract.html)
- [Battlefield GPS Failures Mount: Air Force Commits $49.7M to Navigation Alternatives - Tech Times](https://www.techtimes.com/articles/319822/20260707/battlefield-gps-failures-mount-air-force-commits-497m-navigation-alternatives.htm)
- [Air Force Expands Alternative PNT Strategy With $49.7 Million Canyon Consulting Contract](https://corsstations.com/news/air-force-expands-alternative-pnt-strategy-with-49-7-million-canyon-consulting-contract/)
- [House Armed Services Committee Calls for Single PNT Overseer in FY27 NDAA Markup - Inside GNSS](https://insidegnss.com/house-armed-services-committee-calls-for-single-pnt-overseer-in-fy27-ndaa-markup/)
- [GPS Legislation | GPS.gov](https://www.gps.gov/gps-legislation)
- [GPS jamming attacks threaten critical sectors - RCR Wireless](https://www.rcrwireless.com/20260420/defense-communications/gps-jamming-attacks-threaten-critical-sectors)
- [GPS Is Vulnerable. New Technology May Be Required. - Undark](https://undark.org/2025/12/24/gps-attack-new-tech/)
- [DWIM Monthly: May 2026 | Drone Warfare](https://drone-warfare.com/2026/06/04/dwim-monthly-may-2026/)
- [Anduril and Shield AI: A Massive Bet on Autonomous Warfare - Benzinga](https://www.benzinga.com/markets/private-markets/26/06/53235906/anduril-and-shield-ai-a-massive-bet-on-autonomous-warfare-or-the-next-ai-bubble)
- [Autonomous Navigation at the Nano-Scale: Algorithms, Architectures, and Constraints - arXiv](https://arxiv.org/html/2601.13252v1)
- [A 64mW DNN-based Visual Navigation Engine - UZH](https://rpg.ifi.uzh.ch/docs/IoT19_Palossi.pdf)
- [Efficient Autonomous Navigation of a Quadruped Robot in Underground Mines on Edge Hardware - arXiv](https://arxiv.org/html/2603.04470v1)
- [MDA SBIR: GPS-Denied Event-Based Navigation Funding — BW&CO](https://www.bwcoconsulting.com/fod/mda26bz04-nv008)
- [Blue UAS Framework: Comprehensive Overview - Mobilicom](https://mobilicom.com/insight/blue_uas_framework/)
- [ModalAI VOXL 2](https://www.modalai.com/products/voxl-2)
