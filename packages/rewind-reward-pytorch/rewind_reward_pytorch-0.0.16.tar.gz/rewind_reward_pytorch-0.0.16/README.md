
<img src="./rewind.png" width="400px"></img>

<img src="./fig9.png" width="400px"></img>

## ReWiND Reward - Pytorch (wip)

Implementation of [ReWiND, "Language-Guided Rewards Teach Robot Policies without New Demonstrations"](https://rewind-reward.github.io/), from USC / Amazon Robotics

## Install

```bash
$ pip install rewind-reward-pytorch
```

## Usage

```python
import torch
from rewind_reward_pytorch import RewardModel

reward_model = RewardModel()

commands = [
  'pick up the blue ball and put it in the red tray',
  'pick up the red cube and put it in the green bin'
]

videos = torch.rand(2, 3, 16, 224, 224)

loss = reward_model(commands, videos, rewards = torch.randn(2, 16))

loss.backward()

# after much training

pred = reward_model(commands, videos)

assert pred.shape == (2, 16)
```

## Citations

```bibtex
@article{Zhang2025ReWiNDLR,
    title   = {ReWiND: Language-Guided Rewards Teach Robot Policies without New Demonstrations},
    author  = {Jiahui Zhang and Yusen Luo and Abrar Anwar and Sumedh Anand Sontakke and Joseph J. Lim and Jesse Thomason and Erdem Biyik and Jesse Zhang},
    journal = {ArXiv},
    year    = {2025},
    volume  = {abs/2505.10911},
    url     = {https://api.semanticscholar.org/CorpusID:278714746}
}
```
