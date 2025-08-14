# DuoAI: Two-System AI Agents

<p align="center">
  <img src="images/logo.png" alt="DuoAI Logo" width="30%">
</p>

DuoAI is a research framework for building agents that mimic human [dual cognitive system](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow). In this release, we focus on tackling the [YRC problem](https://arxiv.org/pdf/2502.09583): deciding which system should decide the next action at a given time. This codebase provide modular abstractions, benchmark environments, and baseline implementations to help you quickly develop and test your ideas.

---

## 🔧 Features

- ⚙️ Unified abstractions for coordination policies, decision-making agents, and environments.
- 🧪 Benchmark suite of gridworld and visual decision-making tasks (e.g., MiniGrid, Procgen).
- 📈 Baselines: uncertainty-based and reinforcement learning.
- 🧩 Compositional design: Easily add your own policies, algorithms, or environments.
- 📚 Extensive documentation and examples for rapid experimentation.

---

## 📦 Installation

Install from PyPI:

```bash
pip install duo_ai
```

Or install from source:

```bash
git clone --recurse-submodules https://github.com/khanhptnk/duo-ai.git
cd duo-ai
pip install -e .
```

---

## 📚 Documentation

See the full documentation at:
[https://duo-ai.readthedocs.io](https://duo-ai.readthedocs.io)

---

## 🧪 Citing DuoAI


If you use the DuoAI package in your research, please cite:

```bibtex
@misc{DuoAI2025,
  author       = {Khanh Nguyen},
  title        = {DuoAI: Two-System AI Agents},
  year         = {2025},
  howpublished = {\url{https://github.com/khanhptnk/duo-ai}},
  note         = {Python package. Version 1.0},
}
```

---

## 🤝 Contributing

We welcome pull requests, feature suggestions, and bug reports!
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🛡 License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for more details.

---

## 🙏 Acknowledgments

DuoAI draws inspiration from [YRC-Bench](https://github.com/modanesh/YRC-Bench), a public benchmark Khanh Nguyen co-developed with colleagues at UC Berkeley, but is not an official continuation of that work.
This repository also includes code from the public [procgenAISC](https://github.com/JacobPfau/procgenAISC) and [pyod](https://github.com/yzhao062/pyod) projects as Git submodules. We thank the original authors of these projects for making their work publicly available.
DuoAI builds upon a number of open-source frameworks and libraries, including PyTorch, StableBaselines3, Procgen, MiniGrid, Gym, and Gymnasium. We acknowledge and thank the developers and maintainers of these projects.


