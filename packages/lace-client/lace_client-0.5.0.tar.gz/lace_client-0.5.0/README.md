# Lace - AI Training Transparency Protocol

[![PyPI version](https://badge.fury.io/py/lace-client.svg)](https://badge.fury.io/py/lace-client)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/pypi/pyversions/lace-client.svg)](https://pypi.org/project/lace-client/)

**Prevent copyright lawsuits by proving what you DIDN'T train on.**

Lace provides cryptographic proof of AI training provenance through loss trajectory monitoring. When model outputs resemble copyrighted content, you can prove definitively whether that content was in your training data.

## 🚀 Quick Start

```bash
pip install lace-client
```

```python
import lace

# Before training: Create attestation of your dataset
attestation_id = lace.attest("./training_data")

# During training: One-line integration (zero overhead)
lace.monitor()  # Automatically hooks into PyTorch/TensorFlow

# After training: Verify training relationship
result = lace.verify(attestation_id)
print(f"Correlation: {result['correlation']['score']:.3f}")
print(f"Legal verdict: {result['correlation']['verdict']}")
```

## 🔑 Get Your API Key

All processing happens in our secure cloud infrastructure for IP protection.

**Get your free API key:** [https://withlace.ai/dashboard](https://withlace.ai/dashboard)

```bash
export LACE_API_KEY=your_api_key_here
```

## 💡 How It Works

1. **Attestation**: Before training, Lace creates a cryptographic fingerprint of your dataset
2. **Monitoring**: During training, Lace captures loss trajectories with zero overhead
3. **Correlation**: After training, Lace proves the training relationship through loss curve analysis
4. **Legal Evidence**: Get legally-sufficient evidence for copyright defense

## 📊 Integration Examples

### HuggingFace Transformers

```python
from transformers import Trainer
import lace

# Create attestation
attestation_id = lace.attest("./data")

# Train with monitoring
trainer = Trainer(model, args, dataset)
monitor = lace.monitor(attestation_id)
trainer.train()

# Get correlation
result = monitor.finalize()
```

### PyTorch

```python
import torch
import lace

# Start monitoring
lace.monitor()

# Your normal training loop
for epoch in range(epochs):
    for batch in dataloader:
        loss = model(batch)
        loss.backward()  # Automatically captured!
        optimizer.step()
```

### TensorFlow/Keras

```python
import tensorflow as tf
import lace

# Start monitoring
lace.monitor()

# Your normal training
model.fit(x_train, y_train, epochs=10)  # Automatically captured!
```

## 🛡️ Legal Protection

Lace provides evidence that meets civil legal standards:

- **0.80+ correlation**: Clear and convincing evidence
- **0.65+ correlation**: Substantial evidence  
- **0.50+ correlation**: Preponderance of evidence

When accused of training on copyrighted content, you can prove definitively whether it was in your dataset.

## 🏢 Enterprise Features

- **Unlimited attestations**: No limits on dataset size
- **Priority support**: Direct Slack access to our team
- **SLA guarantees**: 99.9% uptime commitment
- **Custom deployment**: On-premise options available

**Contact:** enterprise@withlace.ai

## 📖 Documentation

- **Docs:** [https://docs.withlace.ai](https://docs.withlace.ai)
- **API Reference:** [https://docs.withlace.ai/api](https://docs.withlace.ai/api)
- **Examples:** [https://github.com/lace-ai/examples](https://github.com/lace-ai/examples)

## 🤝 Support

- **Email:** support@withlace.ai
- **Discord:** [Join our community](https://discord.gg/lace)
- **Issues:** [GitHub Issues](https://github.com/lace-ai/lace-client/issues)

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details.

---

**Stop worrying about copyright lawsuits. Start building with confidence.**

[Get Started Free →](https://withlace.ai/dashboard)