# Spiking Neural Networks: Mathematics and Demo Deployment

**Written**: 2026-05-07
**Audience**: Logic designer — mathematically fluent, new to ML/SNNs
**Goal**: Understand the math from first principles, then run a working demo on a laptop, then connect to event camera data

---

## Table of Contents

1. [From ANN to SNN: The Core Difference](#1-from-ann-to-snn-the-core-difference)
2. [The LIF Neuron: Full Mathematics](#2-the-lif-neuron-full-mathematics)
3. [Information Encoding](#3-information-encoding)
4. [Network Architecture](#4-network-architecture)
5. [Training: Surrogate Gradient and BPTT](#5-training-surrogate-gradient-and-bptt)
6. [The Dead Neuron Problem](#6-the-dead-neuron-problem)
7. [Setup: Frameworks and Installation](#7-setup-frameworks-and-installation)
8. [Demo 1: N-MNIST in 60 Lines](#8-demo-1-n-mnist-in-60-lines)
9. [Demo 2: DVS Gesture Recognition (ConvSNN)](#9-demo-2-dvs-gesture-recognition-convsnn)
10. [Demo 3: Live Prophesee Camera Feed](#10-demo-3-live-prophesee-camera-feed)
11. [Hardware Path: From Demo to KV260](#11-hardware-path-from-demo-to-kv260)
12. [Appendix: Mathematical Reference](#12-appendix-mathematical-reference)

---

## 1. From ANN to SNN: The Core Difference

A conventional ANN neuron computes a single, instantaneous, real-valued output:

```
ANN neuron:
  y = f(Σ_i w_i × x_i + b)        f = ReLU, sigmoid, etc.
  
  time dimension: NONE
  output:         real number (e.g., 0.73)
  when it fires:  always, every forward pass
```

An SNN neuron has an **internal state** (membrane potential) that evolves over time, and produces a **binary spike** only when that state crosses a threshold:

```
SNN neuron (LIF):
  V[t] = β × V[t-1] + Σ_i w_i × s_i[t]    (state update)
  S[t] = 1  if V[t] ≥ V_th,  else 0         (fire or not)
  V[t] ← V[t] - V_th × S[t]                 (reset)

  time dimension: EXPLICIT — you run T timesteps per inference
  output:         binary spike stream S[0], S[1], ..., S[T-1]
  when it fires:  only when membrane potential V[t] exceeds threshold
```

**The key consequences for hardware:**

1. If the input is zero (or all upstream neurons are silent), no computation happens.
   Multiplying by zero = skip. This is the source of sparsity.

2. Information lives in the *pattern of spikes over time*, not in a single real number.

3. The β parameter is a decay constant — the membrane potential "forgets" old input
   exponentially fast. This gives the neuron a built-in temporal memory.

---

## 2. The LIF Neuron: Full Mathematics

### 2.1 Biophysical Origin (Continuous Time)

The Leaky Integrate-and-Fire neuron is a simplified model of a biological neuron. The membrane is modeled as an RC circuit:

```
                  R
  I(t) ──────/\/\/──────┬──── V(t)
                        │
                       _|_
                       ___ C
                        │
                       GND
```

The voltage across the capacitor (= membrane potential V) obeys:

```
C × dV/dt = -V/R + I(t)
```

Dividing by C, with τ_m = R × C (membrane time constant):

```
┌─────────────────────────────────────────────────┐
│   τ_m × dV/dt = -V(t) + R × I(t)               │
│                                                 │
│   τ_m: typically 10-20ms (biological)           │
│   R:   input resistance                         │
└─────────────────────────────────────────────────┘
```

With the spike condition and reset:
- **Fire**: when V(t) ≥ V_th, emit spike S = 1, then reset V ← V_reset (usually 0)
- **Refractory period**: ignore inputs for ~2ms after a spike (optional in hardware SNNs)

### 2.2 Discrete-Time Form (What Software and Hardware Use)

Apply Euler discretization with timestep Δt:

```
V[t] ← V[t-1] + (Δt/τ_m) × (-V[t-1] + R × I[t])
V[t] = (1 - Δt/τ_m) × V[t-1] + (Δt/τ_m) × R × I[t]
```

Define:

```
β ≡ 1 - Δt/τ_m  ≈  exp(-Δt/τ_m)    for small Δt
```

The update rule becomes:

```
┌─────────────────────────────────────────────────────────────────┐
│   Step 1 — Integrate:                                           │
│     V[t] = β × V[t-1]  +  W × x[t]                            │
│             ↑                ↑                                   │
│         membrane decay   synaptic input (weighted pre-spikes)   │
│                                                                 │
│   Step 2 — Fire:                                                │
│     S[t] = Θ(V[t] - V_th)                                      │
│           = 1  if V[t] ≥ V_th                                  │
│           = 0  otherwise                                        │
│                                                                 │
│   Step 3 — Reset:                                               │
│     V[t] ← V[t] - V_th × S[t]     (subtract threshold)        │
│     OR                                                          │
│     V[t] ← V[t] × (1 - S[t])      (zero reset, simpler)       │
└─────────────────────────────────────────────────────────────────┘
```

**In snnTorch code**, `snn.Leaky` implements exactly this:
```python
lif = snn.Leaky(beta=β, threshold=V_th)
spk, mem = lif(current_input, mem_prev)
# spk = S[t], mem = V[t] after reset
```

### 2.3 β and τ_m: What They Mean

β controls how fast the membrane forgets. The relationship:

| β    | τ_m (if Δt=1ms) | Behavior |
|------|----------------|---------|
| 0.99 | 100ms          | Long memory, slow response |
| 0.9  | ~9.5ms         | **Typical default** |
| 0.5  | ~1.4ms         | Fast reset, short memory |
| 0.0  | 0              | No memory (degenerates to ANN with ReLU) |

β is typically a **learned parameter** (not fixed), or treated as a hyperparameter. In the first demos, set β = 0.9.

### 2.4 What Happens Over T Timesteps

Unroll a single LIF neuron receiving a constant input I for T steps, starting from V[0] = 0:

```
V[1] = β×0 + I = I
V[2] = β×I + I = I(1 + β)
V[3] = β×I(1+β) + I = I(1 + β + β²)
...
V[t] = I × Σ_{k=0}^{t-1} β^k = I × (1 - β^t)/(1 - β)

Steady state: V[∞] = I / (1 - β)
```

Spike threshold V_th = 1.0. For β = 0.9, steady state = I/0.1 = 10×I.
The neuron fires repeatedly once V exceeds V_th, then resets.

**This is the mechanism for rate coding**: stronger input → faster firing rate.

### 2.5 Network of LIF Neurons

For a layer l with N_l neurons receiving spikes from layer l-1 with N_{l-1} neurons:

```
I_l[t]  = W_l × S_{l-1}[t]           (synaptic current, matrix-vector multiply)
V_l[t]  = β_l × V_l[t-1] + I_l[t]   (membrane update, element-wise)
S_l[t]  = Θ(V_l[t] - V_th)           (spike generation, element-wise)
V_l[t] ← V_l[t] - V_th × S_l[t]     (reset, element-wise)
```

The **only non-trivial math** at each timestep is the matrix-vector product W_l × S_{l-1}[t]. Since S_{l-1}[t] is binary and sparse, this can be reduced to **addition only** (no multiply needed for spiking inputs): just sum the columns of W_l corresponding to active spikes.

**Hardware implication**: On dedicated neuromorphic silicon, the multiply is replaced by a memory read (fetch synaptic weight) + accumulate. On FPGA, you implement a sparse accumulator, not a DSP-based systolic array.

---

## 3. Information Encoding

How you convert a real-valued input (e.g., a pixel value) into a spike train is called **encoding**. This choice significantly affects accuracy and efficiency.

### 3.1 Rate Coding

Convert intensity to firing rate. The most common approach:

```
For pixel value x ∈ [0, 1]:
  Generate T spikes over T timesteps
  Probability of spike at each timestep = x

Bernoulli sampling:
  S[t] ~ Bernoulli(x)  for t = 1..T

Result: bright pixel → frequent spikes, dark pixel → rare spikes
```

**Drawback**: Requires T ≈ 50-200 timesteps for accurate rate estimation. Information is in the *count*, not the *timing*.

**Code** (snnTorch):
```python
from snntorch import spikegen
# x: tensor of values in [0,1]
spike_data = spikegen.rate(x, num_steps=100)  # (100, *x.shape)
```

### 3.2 Latency (Time-to-First-Spike) Coding

Stronger inputs fire earlier:

```
For pixel value x ∈ [0, 1]:
  Fire at timestep t_fire = floor((1 - x) × T)

Bright pixel (x=1.0): fires at t=0
Dark pixel (x=0.0):   fires at t=T-1 (or not at all)
```

**Advantage**: First spike carries information → only needs a few timesteps (T=10-20).
**Drawback**: Timing precision is critical. Noise translates directly to error.

```python
spike_data = spikegen.latency(x, num_steps=20, tau=5, normalize=True)
```

### 3.3 Event Camera: Direct Encoding (No Conversion Needed)

This is why event cameras and SNNs are a natural match:

```
Event camera output:  (x, y, t, polarity)  — a spike has already occurred!
SNN input:            S[t][y][x][polarity] = 1 at (y, x) if event at time t

No encoding step needed. The sensor IS the spike generator.
```

When using `tonic` with event camera datasets, the `ToFrame` transform bins events into time windows and returns a (T, C, H, W) binary tensor — directly usable as SNN input.

### 3.4 Which Encoding to Use in Practice

| Task | Encoding | Why |
|------|----------|-----|
| Standard image dataset | Rate (fast demo) | Simple, widely tested |
| Fast response required | Latency | Lower latency, fewer timesteps |
| Event camera data | Direct (no encoding) | Events are already spikes |
| Analog sensor (IMU, etc.) | Rate or delta modulation | Convert to event stream |

For the demos below: use **ToFrame** (bins events into T time windows), which works well and avoids encoding complexity.

---

## 4. Network Architecture

### 4.1 Feedforward SNN (FC-SNN)

Direct translation of a fully-connected ANN, replacing ReLU with LIF:

```
ANN:
  x → [FC1] → ReLU → [FC2] → ReLU → [FC3] → Softmax → class

SNN (unrolled over T timesteps):
  For t = 0..T-1:
    cur1[t] = W1 × S0[t]              (input spikes)
    V1[t], S1[t] = LIF(cur1[t], V1[t-1])
    cur2[t] = W2 × S1[t]
    V2[t], S2[t] = LIF(cur2[t], V2[t-1])
    ...
  
  Output: sum of S_out[t] over T → argmax → class
```

### 4.2 Convolutional SNN (ConvSNN)

Replace linear layers with convolutions:

```
For t = 0..T-1:
  x[t]: (batch, channels, H, W) input frame
  
  c1[t] = Conv2D(x[t], W_conv1)       (standard convolution)
  V1[t], S1[t] = LIF(c1[t], V1[t-1]) (element-wise, channel-wise)
  
  p1[t] = MaxPool2D(S1[t])            (standard pooling, on spike map)
  
  c2[t] = Conv2D(p1[t], W_conv2)
  V2[t], S2[t] = LIF(c2[t], V2[t-1])
  ...
```

**Key insight**: The convolution operates on binary spike maps (0s and 1s). This dramatically reduces multiply-add cost vs. operating on floating-point feature maps — but frameworks still use float internally for training.

### 4.3 Recurrent SNN (LSNN / Liquid State Machine)

Add recurrent connections within a layer:

```
V[t] = β × V[t-1] + W_in × x[t] + W_rec × S[t-1]
```

The recurrent weight W_rec allows the network to maintain longer-term state. This is the SNN equivalent of an LSTM (but simpler — no gates).

**For VIO temporal integration** (accumulating evidence across many events), a recurrent SNN is the natural architecture. The membrane potential V[t] acts as an accumulator with exponential forgetting — exactly what you want when integrating event camera data.

### 4.4 Population Coding Output Layer

For classification, the output layer can use:

```
Option A — Spike rate decoding:
  prediction = argmax(Σ_t S_out[t, :])
  "Which class neuron fired most over the T timesteps?"

Option B — Membrane potential at final timestep:
  prediction = argmax(V_out[T-1, :])
  "Which output neuron had the highest membrane potential at the end?"

Option C — Time-to-first-spike:
  prediction = argmin(t_first_spike[:])
  "Which class neuron fired first?"
```

For demos: use **Option A** (spike rate). It's most robust and maps cleanly to a cross-entropy loss on firing counts.

---

## 5. Training: Surrogate Gradient and BPTT

### 5.1 The Core Problem

The spike function S[t] = Θ(V[t] - V_th) is a step function. Its derivative is:

```
dS/dV = δ(V - V_th)   (Dirac delta)
```

This is zero almost everywhere (no gradient signal) and infinite at the threshold (numeric explosion). Standard backpropagation fails.

### 5.2 Surrogate Gradient Method

The fix: keep the forward pass exactly as defined (hard threshold), but during the **backward pass only**, replace the spike function derivative with a smooth surrogate:

```
Forward:   S[t] = Θ(V[t] - V_th)           (hard threshold, unchanged)

Backward:  dS/dV ← surrogate'(V[t] - V_th)  (smooth approximation)
```

Common surrogates:

```
Fast sigmoid (snnTorch default):
  surrogate'(x) = slope / (2 × (1 + |slope × x|))²
  slope ≈ 25 works well

Piecewise linear:
  surrogate'(x) = max(0, 1 - |slope × x|)

Triangular:
  surrogate'(x) = max(0, 1 - |x|)    (slope=1 case)
```

The `slope` parameter controls the width of the surrogate:
- High slope (25-100): narrow, close to true delta — sharp gradients, can be unstable
- Low slope (1-5): wide, smooth gradients, lower accuracy

**The key insight**: This is a deliberately incorrect but useful approximation. You're "lying" to the optimizer about the derivative of the threshold, but the lie is calibrated to produce useful gradient signals. This is accepted practice.

```python
from snntorch import surrogate
spike_grad = surrogate.fast_sigmoid(slope=25)   # recommended default
lif = snn.Leaky(beta=0.9, spike_grad=spike_grad)
```

### 5.3 Backpropagation Through Time (BPTT)

The SNN is unrolled across T timesteps, forming a computation graph:

```
x[0] → LIF → S[0] → LIF → S[1] → ... → S[T-1] → Loss
         ↑ V[0]      ↑ V[1]              ↑ V[T-1]
         
         β↗          β↗
       V[-1]=0      V[0]
```

Backprop flows backward through this unrolled graph. The gradient at timestep t depends on:

```
∂L/∂W = Σ_t (∂L/∂S[t]) × (∂S[t]/∂V[t]) × (∂V[t]/∂W)
                             ↑
                        surrogate'(V[t]-V_th)
```

Temporal credit assignment through the membrane:

```
∂V[t]/∂V[t-1] = β × (1 - S[t-1])    ← spike reset gate
                 ↑
    If S[t-1]=1 (spike), reset kills gradient at that timestep
    If S[t-1]=0 (no spike), gradient flows back with attenuation β
```

This is analogous to the gradient flow in a vanilla RNN:

```
RNN:    ∂h[t]/∂h[t-1] = diag(tanh'(h[t-1]))  × W_rec^T
SNN:    ∂V[t]/∂V[t-1] = β × (1 - S[t-1])
```

The β term prevents the vanishing gradient problem somewhat (keeps gradients from decaying too fast across time). The spike reset is a form of gating — similar conceptually to the forget gate in an LSTM.

### 5.4 Loss Functions

Three standard options in snnTorch:

```python
from snntorch import functional as SF

# 1. Cross-entropy on spike rates (most common)
#    spk_out: (T, batch, num_classes)
#    targets: (batch,) — integer class labels
loss = SF.ce_rate_loss()(spk_out, targets)
# Equivalent to: CE(Σ_t spk_out[t], targets)

# 2. Cross-entropy on membrane potential at last timestep
loss = SF.ce_membrane_loss()(mem_out, targets)
# Equivalent to: CE(mem_out[-1], targets)

# 3. Mean square error on spike count
#    target_spikes: desired number of spikes for the correct class
loss = SF.mse_count_loss(correct_rate=0.8, incorrect_rate=0.2)(spk_out, targets)
```

For demos: use `ce_rate_loss`. For VIO regression tasks: use MSE on membrane potential.

### 5.5 Truncated BPTT

For long sequences (many time bins from an event camera), full BPTT is memory-expensive. Truncated BPTT processes the sequence in chunks:

```python
# Full BPTT: T=100 timesteps, unroll entire sequence
# Memory: O(T × N) = O(100 × network_size)

# Truncated BPTT: chunks of size K=10
for chunk_start in range(0, T, K):
    chunk = data[chunk_start : chunk_start + K]
    spk_out, mem_out = model(chunk, hidden_state)  # hidden_state carried forward
    loss = criterion(spk_out, targets)
    loss.backward()
    # Detach hidden state to stop gradient from flowing across chunks
    hidden_state = (mem.detach() for mem in hidden_state)
    optimizer.step()
```

For demos with T=5-10, full BPTT is fine. For Prophesee camera data (potentially thousands of events per second), truncated BPTT is necessary.

---

## 6. The Dead Neuron Problem

The main failure mode when training SNNs.

If V[t] never reaches V_th, S[t] = 0 for all t. The surrogate gradient at V[t] - V_th ≪ 0 is also approximately zero. Result: no gradient, weights don't update, neuron stays dead permanently.

**Causes**: Too high threshold, too small weights, too few timesteps, dead input.

**Solutions**:

```python
# 1. Threshold adaptation (soft reset with leak toward threshold)
lif = snn.Leaky(beta=0.9, threshold=1.0, reset_mechanism='subtract')

# 2. Batch normalization through time (BNTT) — normalize membrane potential
# Apply BatchNorm before LIF on each timestep's current

# 3. Neuron dropout — randomly reset some neurons during training
# Forces other neurons to compensate

# 4. Careful initialization
# Initialize W so that Σ_i |w_i| ≈ V_th / (1 - β)
# For β=0.9, V_th=1.0: target fan-in norm ≈ 10

# 5. Start with β < 0.5 to force more spikes early in training, increase later
```

**Monitor during training**: print `spk_out.mean()` (average spike rate). Should be in range 0.05–0.4. Below 0.01 → dying neurons. Above 0.8 → too many spikes, losing temporal information.

---

## 7. Setup: Frameworks and Installation

### 7.1 Framework Comparison

| Framework | Backend | Strength | Use For |
|-----------|---------|----------|---------|
| **snnTorch** | PyTorch | Best documentation, easiest to start | **Demos in this guide** |
| **SpikingJelly** | PyTorch | More features, cuDNN-accelerated | Serious training, publication |
| **Norse** | PyTorch | Functional style, clean API | Research experimentation |
| **Lava** | Lava (Intel) | Runs on Loihi 2/3 | Neuromorphic hardware deployment |
| **Nengo** | NumPy/TF | Biological accuracy, Loihi support | Neuroscience research |

**For the demos here**: snnTorch.
**For production training on KV260 (Vitis AI path)**: SpikingJelly (supports INT8 quantization + ONNX export).

### 7.2 Installation

```bash
# Python 3.9-3.11 recommended
pip install snntorch        # SNN framework
pip install tonic           # neuromorphic datasets (N-MNIST, DVSGesture, etc.)
pip install torch torchvision  # PyTorch

# Optional but recommended
pip install matplotlib      # visualization
pip install numpy pandas    # utilities

# Verify
python -c "import snntorch; print(snntorch.__version__)"
python -c "import tonic; print(tonic.__version__)"
```

GPU is not required for Demo 1 (N-MNIST is small). Demo 2 (DVS Gesture) trains in ~20 min on CPU, ~3 min on GPU.

### 7.3 Testing the Install

```python
import torch
import snntorch as snn

# Create a single LIF neuron and run it for 10 timesteps
beta = 0.9
lif = snn.Leaky(beta=beta)

mem = torch.zeros(1)         # initial membrane potential
spk_history = []
mem_history = []

# Step input: simulate a constant synaptic current of 0.5
for t in range(10):
    cur = torch.tensor([0.5])
    spk, mem = lif(cur, mem)
    spk_history.append(spk.item())
    mem_history.append(mem.item())

print("Spikes:   ", spk_history)
print("Membrane: ", [f"{v:.3f}" for v in mem_history])
# Expected: V builds up, eventually crosses 1.0, spikes, resets, builds again
```

Expected output (approximately):
```
Spikes:    [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
Membrane:  [0.500, 0.950, 1.355 → spike → 0.355, 0.820, 1.238 → spike...]
```

---

## 8. Demo 1: N-MNIST in 60 Lines

### 8.1 Dataset

N-MNIST is the event-camera version of MNIST. A standard MNIST digit is shown on an LCD screen while an event camera moves in a small saccade pattern. Output: stream of events `(x, y, t, polarity)` for each digit.

- 60,000 training / 10,000 test samples
- Sensor resolution: 34 × 34 pixels
- 2 polarities (ON event = brightness increase, OFF event = decrease)
- Downloads automatically via `tonic`

### 8.2 Full Training Script

```python
# demo1_nmnist.py
import torch
import torch.nn as nn
import snntorch as snn
from snntorch import surrogate, functional as SF, utils
import tonic
import tonic.transforms as transforms
from torch.utils.data import DataLoader

# ─────────────────────────────────────────────
# 1. Dataset
# ─────────────────────────────────────────────
NUM_STEPS  = 5     # number of time bins
BATCH_SIZE = 128
SENSOR_SIZE = tonic.datasets.NMNIST.sensor_size   # (34, 34, 2)

transform = transforms.Compose([
    transforms.Denoise(filter_time=10000),          # remove hot pixels
    transforms.ToFrame(sensor_size=SENSOR_SIZE,     # bin events into frames
                       n_time_bins=NUM_STEPS),      # → (5, 2, 34, 34)
])

train_set = tonic.datasets.NMNIST(save_to='./data', train=True,
                                   transform=transform)
test_set  = tonic.datasets.NMNIST(save_to='./data', train=False,
                                   transform=transform)

train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=4)
test_loader  = DataLoader(test_set,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=4)

# ─────────────────────────────────────────────
# 2. SNN Model
# ─────────────────────────────────────────────
INPUT_DIM  = 34 * 34 * 2    # 2312
HIDDEN_DIM = 1000
NUM_CLASSES = 10
BETA       = 0.9             # membrane decay
V_THRESH   = 1.0             # spike threshold

spike_grad = surrogate.fast_sigmoid(slope=25)

class FCSNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1  = nn.Linear(INPUT_DIM, HIDDEN_DIM)
        self.lif1 = snn.Leaky(beta=BETA, threshold=V_THRESH,
                               spike_grad=spike_grad, init_hidden=True)
        self.fc2  = nn.Linear(HIDDEN_DIM, NUM_CLASSES)
        self.lif2 = snn.Leaky(beta=BETA, threshold=V_THRESH,
                               spike_grad=spike_grad, init_hidden=True)

    def forward(self, x):
        # x: (batch, T, 2, 34, 34)
        utils.reset(self)                  # zero all membrane potentials
        spk_out_rec = []

        for t in range(x.shape[1]):        # iterate over time bins
            x_t = x[:, t].flatten(1)      # (batch, 2312)
            cur1 = self.fc1(x_t)
            spk1, _ = self.lif1(cur1)     # LIF layer 1
            cur2 = self.fc2(spk1)
            spk2, _ = self.lif2(cur2)     # LIF layer 2 (output)
            spk_out_rec.append(spk2)

        return torch.stack(spk_out_rec)    # (T, batch, 10)

# ─────────────────────────────────────────────
# 3. Training
# ─────────────────────────────────────────────
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model  = FCSNN().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=5e-4)
loss_fn   = SF.ce_rate_loss()

NUM_EPOCHS = 10

for epoch in range(NUM_EPOCHS):
    model.train()
    train_correct = 0

    for data, targets in train_loader:
        data    = data.float().to(device)     # (batch, 5, 2, 34, 34)
        targets = targets.long().to(device)

        spk_out = model(data)                 # (5, batch, 10)

        loss = loss_fn(spk_out, targets)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        # Accuracy: vote by summing spike counts
        predicted = spk_out.sum(0).argmax(1)
        train_correct += (predicted == targets).sum().item()

    train_acc = train_correct / len(train_set)

    # Validation
    model.eval()
    test_correct = 0
    with torch.no_grad():
        for data, targets in test_loader:
            data    = data.float().to(device)
            targets = targets.long().to(device)
            spk_out = model(data)
            predicted = spk_out.sum(0).argmax(1)
            test_correct += (predicted == targets).sum().item()

    test_acc = test_correct / len(test_set)

    print(f"Epoch {epoch+1:2d}/{NUM_EPOCHS} | "
          f"Train acc: {train_acc:.3f} | Test acc: {test_acc:.3f} | "
          f"Spike rate: {spk_out.mean().item():.3f}")

# Expected final test accuracy: ~97-98% after 10 epochs
```

### 8.3 What to Observe

Run it and watch:
```
Epoch  1/10 | Train acc: 0.891 | Test acc: 0.938 | Spike rate: 0.127
Epoch  5/10 | Train acc: 0.971 | Test acc: 0.972 | Spike rate: 0.089
Epoch 10/10 | Train acc: 0.984 | Test acc: 0.980 | Spike rate: 0.076
```

Key things to notice:
- **Spike rate ≈ 0.08**: only 8% of neurons fire per timestep. This is the sparsity that makes SNNs efficient.
- **Convergence**: similar speed to an equivalent ANN — about 10 epochs to near-peak accuracy.
- **T=5 time bins**: surprisingly few. The temporal structure of the events carries useful information even with coarse binning.

### 8.4 Modify and Learn

Try these variations to build intuition:

```python
# 1. Kill temporal structure — treat all events as one frame
NUM_STEPS = 1   # → accuracy drops to ~85%, losing temporal information

# 2. Vary β
BETA = 0.5      # fast decay → worse temporal integration → ~2% accuracy drop
BETA = 0.99     # long memory → slow response → needs more timesteps

# 3. Replace surrogate with piecewise linear
spike_grad = surrogate.straight_through_estimator()  # aggressive, noisy

# 4. Watch dead neurons
# Add this inside the training loop:
dead = (spk_out.sum(0) == 0).float().mean()
print(f"Dead output neurons: {dead:.1%}")
# Should be near 0%. If >10%, your learning rate or threshold is wrong.
```

---

## 9. Demo 2: DVS Gesture Recognition (ConvSNN)

### 9.1 Dataset

IBM DVS128 Gesture Dataset: 11 hand gestures recorded with a 128×128 event camera.
- 29 subjects, 1,342 samples
- Gestures: hand wave, arm roll, air guitar, etc.
- This is a harder problem and more representative of real event camera data.

```bash
# Note: DVSGesture requires manual download from IBM
# tonic will prompt you with download instructions on first run
```

### 9.2 ConvSNN Architecture

```python
# demo2_dvs_gesture.py
import torch
import torch.nn as nn
import snntorch as snn
from snntorch import surrogate, functional as SF, utils
import tonic
import tonic.transforms as transforms
from torch.utils.data import DataLoader

NUM_STEPS   = 10
BATCH_SIZE  = 32
SENSOR_SIZE = tonic.datasets.DVSGesture.sensor_size   # (128, 128, 2)

transform = transforms.Compose([
    transforms.Denoise(filter_time=10000),
    transforms.ToFrame(sensor_size=SENSOR_SIZE, n_time_bins=NUM_STEPS),
    # → (10, 2, 128, 128)
])

train_set = tonic.datasets.DVSGesture(save_to='./data', train=True,
                                       transform=transform)
test_set  = tonic.datasets.DVSGesture(save_to='./data', train=False,
                                       transform=transform)

train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
test_loader  = DataLoader(test_set,  batch_size=BATCH_SIZE, shuffle=False)

# ─────────────────────────────────────────────
# ConvSNN Architecture
# Input: (batch, T, 2, 128, 128)
#
# Per timestep:
#   Conv2D(2, 12, 5)    → (12, 124, 124) after no-pad conv
#   LIF
#   MaxPool2D(2)        → (12, 62, 62)
#   Conv2D(12, 32, 5)   → (32, 58, 58)
#   LIF
#   MaxPool2D(2)        → (32, 29, 29)
#   Flatten             → 26912
#   Linear(26912, 512)
#   LIF
#   Linear(512, 11)     → 11 gestures
#   LIF
# ─────────────────────────────────────────────

BETA = 0.9
spike_grad = surrogate.fast_sigmoid(slope=25)

class ConvSNN(nn.Module):
    def __init__(self):
        super().__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(2, 12, kernel_size=5)
        self.lif1  = snn.Leaky(beta=BETA, spike_grad=spike_grad,
                                init_hidden=True)
        self.pool1 = nn.MaxPool2d(2)

        self.conv2 = nn.Conv2d(12, 32, kernel_size=5)
        self.lif2  = snn.Leaky(beta=BETA, spike_grad=spike_grad,
                                init_hidden=True)
        self.pool2 = nn.MaxPool2d(2)

        # Fully connected layers
        self.fc1  = nn.Linear(32 * 29 * 29, 512)   # = 26912
        self.lif3 = snn.Leaky(beta=BETA, spike_grad=spike_grad,
                               init_hidden=True)

        self.fc2  = nn.Linear(512, 11)
        self.lif4 = snn.Leaky(beta=BETA, spike_grad=spike_grad,
                               init_hidden=True)

    def forward(self, x):
        # x: (batch, T, 2, 128, 128)
        utils.reset(self)
        spk_out_rec = []

        for t in range(x.shape[1]):
            x_t = x[:, t]               # (batch, 2, 128, 128)

            # Conv block 1
            c1 = self.conv1(x_t)        # (batch, 12, 124, 124)
            s1, _ = self.lif1(c1)
            s1 = self.pool1(s1)         # (batch, 12, 62, 62)

            # Conv block 2
            c2 = self.conv2(s1)         # (batch, 32, 58, 58)
            s2, _ = self.lif2(c2)
            s2 = self.pool2(s2)         # (batch, 32, 29, 29)

            # FC block
            c3 = self.fc1(s2.flatten(1))
            s3, _ = self.lif3(c3)

            c4 = self.fc2(s3)
            s4, _ = self.lif4(c4)
            spk_out_rec.append(s4)

        return torch.stack(spk_out_rec)  # (T, batch, 11)


device    = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model     = ConvSNN().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn   = SF.ce_rate_loss()

for epoch in range(20):
    model.train()
    correct = 0
    for data, targets in train_loader:
        data    = data.float().to(device)
        targets = targets.long().to(device)

        spk_out = model(data)
        loss    = loss_fn(spk_out, targets)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        correct += (spk_out.sum(0).argmax(1) == targets).sum().item()

    print(f"Epoch {epoch+1}: train acc = {correct/len(train_set):.3f}, "
          f"spike rate = {spk_out.mean():.3f}")

# Expected: ~85-90% test accuracy after 20 epochs
# With GPU: ~5 min total. With CPU: ~30-40 min.
```

### 9.3 What This Proves

This demo is directly relevant to the VIO project because:
1. The input is real event camera data (DVS128, same sensor family as Prophesee)
2. The task requires temporal integration — the gesture unfolds over time
3. The convolutional structure maps directly to FPGA accelerator blocks
4. The Conv + LIF + Pool pipeline is what you'd target for RTL implementation

---

## 10. Demo 3: Live Prophesee Camera Feed

If you have the Prophesee IMX636 + KV260 kit, you can run a live inference demo on your laptop (USB) before moving to the FPGA.

### 10.1 Install Prophesee SDK

```bash
# Install Metavision SDK (download from Prophesee portal)
# Requires account at https://www.prophesee.ai/
pip install metavision-sdk-core
pip install metavision-sdk-ml
```

### 10.2 Event Stream Adapter for snnTorch

```python
# demo3_live_prophesee.py
import numpy as np
import torch
import snntorch as snn
from snntorch import utils
import metavision_core as mv

# ─────────────────────────────────────────────
# 1. Connect to Prophesee camera
# ─────────────────────────────────────────────
device_mv = mv.EventCamera()                     # opens first connected camera
H, W = device_mv.get_sensor_size()              # IMX636: 720, 1280

# ─────────────────────────────────────────────
# 2. Event-to-tensor converter
# ─────────────────────────────────────────────
class EventFrameAccumulator:
    """Accumulate events into fixed-duration time bins."""
    
    def __init__(self, H, W, duration_us=5000):
        self.H = H
        self.W = W
        self.duration = duration_us   # 5ms bins

    def events_to_tensor(self, events):
        """
        events: structured array with fields (x, y, t, p)
        Returns: (1, 2, H, W) float tensor
        """
        frame = np.zeros((2, self.H, self.W), dtype=np.float32)
        if len(events) == 0:
            return torch.from_numpy(frame).unsqueeze(0)
        x = events['x'].astype(int)
        y = events['y'].astype(int)
        p = events['p'].astype(int)   # 0 = OFF, 1 = ON
        # Accumulate: ON events in channel 0, OFF in channel 1
        np.add.at(frame[0], (y[p==1], x[p==1]), 1)
        np.add.at(frame[1], (y[p==0], x[p==0]), 1)
        # Normalize to [0,1]
        frame = np.clip(frame / 20.0, 0, 1)
        return torch.from_numpy(frame).unsqueeze(0)

# ─────────────────────────────────────────────
# 3. Load trained model (from Demo 2, adapted for Prophesee resolution)
# ─────────────────────────────────────────────
# For a quick sanity demo: just visualize the event frame as an SNN input.
# For real inference: train a model on Prophesee-captured data.

model = ConvSNN()  # or load a trained checkpoint
model.eval()

accumulator = EventFrameAccumulator(H, W, duration_us=5000)

# ─────────────────────────────────────────────
# 4. Real-time loop
# ─────────────────────────────────────────────
T = 5                              # accumulate 5 time bins
frame_buffer = []

def process_events(events, ts):
    """Callback called by Metavision SDK per time window."""
    frame = accumulator.events_to_tensor(events)  # (1, 2, H, W)
    frame_buffer.append(frame)
    
    if len(frame_buffer) == T:
        batch = torch.stack(frame_buffer, dim=1)  # (1, T, 2, H, W)
        
        with torch.no_grad():
            utils.reset(model)
            spk_out_list = []
            for t in range(T):
                x_t = batch[:, t]
                # ... run through model ...
            
        frame_buffer.clear()
        # Print predicted class or visualize

device_mv.start()
device_mv.add_event_callback(process_events, delta_t=5000)  # 5ms windows
```

### 10.3 Simpler Alternative: Record and Replay

If you don't have the camera yet, Prophesee provides free sample recordings (`.raw` files):

```python
from metavision_core.event_io import EventsIterator

# Prophesee provides sample .raw files at prophesee.ai/datasets
reader = EventsIterator('./sample_recording.raw', delta_t=5000)  # 5ms bins

for events in reader:
    frame = accumulator.events_to_tensor(events)
    # ... run SNN inference ...
```

---

## 11. Hardware Path: From Demo to KV260

Once you have a trained SNN model, the path to the KV260 FPGA has two options:

### 11.1 Option A: ARM CPU on KV260 (Quickest)

The KV260 has a quad-core ARM Cortex-A53 running Linux. You can run the PyTorch model directly:

```bash
# On KV260 (PetaLinux or Ubuntu)
pip install torch-cpu   # ARM-optimized PyTorch build
# Copy your trained model
python demo1_nmnist.py  # runs on ARM, no FPGA fabric needed
```

**Performance expectation**: N-MNIST at ~5-10 fps on A53. Good enough for demo visualization, not real-time 720p.

**This is the right first step**: prove the algorithm works end-to-end on the target platform, then optimize.

### 11.2 Option B: Vitis AI + FPGA Fabric (Production Path)

Vitis AI enables INT8 quantization and compilation of PyTorch models to the KV260's DPU (Deep Processing Unit, an FPGA-implemented CNN accelerator).

```python
# Step 1: Export model to ONNX
torch.onnx.export(model, sample_input, 'snn_gesture.onnx',
                  opset_version=13,
                  input_names=['input'],
                  output_names=['output'])

# Step 2: Quantize with Vitis AI (on host machine with Docker)
# vai_q_pytorch: Vitis AI quantizer for PyTorch
from pytorch_nndct.apis import torch_quantizer
quantizer = torch_quantizer('calib', model, sample_input)
quantized_model = quantizer.quant_model
# ... run calibration data through quantized_model ...
quantizer.export_quant_config()

# Step 3: Compile for DPU target
# vaiq compile -m snn_gesture.onnx -a KV260 ...
# Output: .xmodel file deployable on KV260 DPU
```

**Limitation**: The DPU is a CNN accelerator. It handles Conv2D + ReLU well but LIF neurons (with reset and threshold) require custom RTL. Options:
1. **Approximate the LIF as ReLU** — replace LIF with ReLU in the ONNX export, deploy to DPU, lose SNN dynamics (but fast demo)
2. **Implement LIF as a custom PL (programmable logic) block** — harder, true SNN execution

### 11.3 Option C: Custom RTL SNN Accelerator

The long-term path: implement the SNN in Vivado RTL on the KV260 fabric.

The per-timestep computation per layer is:

```
For N_in=1000 inputs, N_out=10 outputs:
  Reads: check which inputs are spiking (N_in 1-bit checks)
  MACs:  only for active spikes (typically N_in × 0.15 = 150 multiplies)
  Writes: update membrane potentials V[0..N_out-1]
  Compare: V[i] vs V_th → spike or not

RTL blocks needed:
  - Spike buffer (1-bit BRAM, N_in wide)
  - Weight memory (N_in × N_out × 8-bit = 1.25 MB for 1000×1000)
  - Sparse accumulator (accumulate weighted inputs for active spikes only)
  - Membrane register file (N_out × 16-bit)
  - Threshold comparator (N_out parallel comparisons)
  - Reset logic (subtract V_th from firing neurons)
```

The sparse accumulator is the key RTL challenge. One implementation:

```verilog
// Simplified sparse accumulator for one LIF layer
// For each timestep:
// 1. For each active spike at index i, add W[i,:] to accumulator[:]
// 2. After all spikes processed, add to membrane[:]
// 3. Compare membrane[:] to threshold, generate spike outputs

module sparse_accum #(
    parameter N_IN  = 1000,
    parameter N_OUT = 10,
    parameter W_BITS = 8,
    parameter V_BITS = 16
)(
    input  logic clk, rst,
    input  logic [N_IN-1:0]          spike_in,   // which inputs fired
    input  logic [W_BITS-1:0]        weight_mem [N_IN][N_OUT],
    input  logic [V_BITS-1:0]        mem_in [N_OUT],
    output logic [N_OUT-1:0]         spike_out,
    output logic [V_BITS-1:0]        mem_out [N_OUT]
);
    // Iterate over active spikes, accumulate weights
    // Then add to membrane, compare to threshold, reset
    // Details: one active spike processed per cycle → N_in × sparsity cycles/timestep
endmodule
```

For the KV260 with 1248 DSPs and 7.1 MB BRAM, a full SNN for gesture recognition (ConvSNN from Demo 2) fits with room to spare.

### 11.4 Recommended Sequence

```
Week 1:   Run Demo 1 (N-MNIST) on laptop
          → Understand training dynamics, surrogate gradients

Week 2:   Run Demo 2 (DVS Gesture) on laptop with GPU
          → Understand ConvSNN, event camera data format

Week 3:   Deploy Demo 1 model on KV260 ARM (Option A)
          → Validate software stack, Python on KV260

Week 4-6: Adapt Demo 2 for Prophesee IMX636 resolution (320×320 first)
          → Real event camera data through trained SNN

Month 2+: Implement sparse accumulator RTL for one layer (Option C)
          → First PL-accelerated SNN on KV260
```

---

## 12. Appendix: Mathematical Reference

### The LIF Update in Full

```
Biological (continuous):
  τ_m × dV/dt = -(V - V_rest) + R × I(t)
  Fire if V(t) ≥ V_th,  then V ← V_reset

Discrete (hardware/software):
  V[t] = β × V[t-1] + W × x[t]
  S[t] = Θ(V[t] - V_th)
  V[t] ← V[t] - V_th × S[t]   (soft reset)

Parameters:
  β = exp(-Δt/τ_m)    ∈ (0, 1)
  V_th = 1.0          (set by convention, weights scale accordingly)
  W                    learned (same as ANN weights)
```

### Surrogate Gradient Reference

```
Spike function (forward):
  S = Θ(V - V_th)  →  dS/dV = δ(V - V_th)  (unusable)

Fast sigmoid surrogate (backward only):
  dS/dV ≈ slope / (2 × (1 + |slope × (V - V_th)|))²

Interpretation: this says "the spike function has gradient slope/2 at threshold,
falling off quickly on either side." The slope parameter controls how sharply
the surrogate decays.
```

### BPTT Gradient Flow

```
L = loss(S[T-1], ..., S[0])

∂L/∂W = Σ_{t=0}^{T-1} ∂L/∂S[t] × ∂S[t]/∂V[t] × ∂V[t]/∂W
                            ↑
                      surrogate'(V[t] - V_th)

Temporal chain rule (for deeper timesteps):
  ∂V[t]/∂V[0] = β^t × Π_{k=1}^{t} (1 - S[k-1])
                  ↑ decay                ↑ spike gates kill gradient
```

### Spike Rate and Efficiency

```
Effective MACs per neuron per timestep:
  = fan-in × P(spike in previous layer)
  = fan-in × spike_rate

For spike_rate = 0.10 (typical):
  Effective MACs = fan-in × 0.10
  vs. ANN:         fan-in × 1.00
  
  Savings: 10×

Energy advantage on neuromorphic hardware (add neuron activation check):
  SNN:  (spike_rate × fan-in × E_MAC) + E_check
  ANN:  fan-in × E_MAC
  
  For spike_rate=0.10, E_check ≈ 0.01 × E_MAC:
  SNN energy ≈ 0.10 × E_MAC + 0.01 × E_MAC = 0.11 × fan-in × E_MAC
  Savings: 9× at operation level, 100× on neuromorphic silicon (better E/MAC)
```

### Framework Quick Reference (snnTorch)

```python
import snntorch as snn
from snntorch import surrogate, functional as SF, utils

# Create LIF neuron
lif = snn.Leaky(beta=0.9,
                threshold=1.0,
                spike_grad=surrogate.fast_sigmoid(slope=25),
                init_hidden=True)

# Single step
spk, mem = lif(current, mem_prev)    # if init_hidden=False
spk, mem = lif(current)              # if init_hidden=True (hidden managed internally)

# Reset hidden state (call before each new sample)
utils.reset(net)

# Loss functions
loss = SF.ce_rate_loss()(spk_out_T_batch, targets)
loss = SF.mse_count_loss(correct_rate=0.8, incorrect_rate=0.2)(spk_out, targets)

# Encoding
spikes = snn.spikegen.rate(data, num_steps=100)
spikes = snn.spikegen.latency(data, num_steps=20, tau=5)
```

---

## Sources

- [snnTorch Documentation](https://snntorch.readthedocs.io/)
- [snnTorch Tutorial Series](https://snntorch.readthedocs.io/en/latest/tutorials/index.html)
- [tonic: Neuromorphic Datasets](https://tonic.readthedocs.io/)
- [Surrogate Gradient Learning in SNNs — Neftci et al. 2019](https://ieeexplore.ieee.org/document/8891809)
- [The Remarkable Robustness of Surrogate Gradients — Zenke & Neftci 2021](https://direct.mit.edu/neco/article/33/4/899/97482)
- [LIF Neuron Model — Gerstner & Kistler, Spiking Neuron Models](https://lcn.epfl.ch/~gerstner/SPNM/)
- [Intel Loihi BPTT tutorial via Lava](https://github.com/lava-nc/lava)
- [SpikingJelly (alternative framework)](https://spikingjelly.readthedocs.io/)
- [N-MNIST Dataset Paper — Orchard et al. 2015](https://www.frontiersin.org/articles/10.3389/fnins.2015.00437/full)
- [IBM DVS128 Gesture Dataset — Amir et al. 2017](https://research.ibm.com/publications/a-low-power-fully-event-based-gesture-recognition-system)
