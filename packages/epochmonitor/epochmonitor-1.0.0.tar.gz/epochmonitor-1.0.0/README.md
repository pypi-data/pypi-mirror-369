# EpochMonitor ⏱️

[![PyPI version](https://badge.fury.io/py/epochmonitor.svg)](https://badge.fury.io/py/epochmonitor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, lightweight, and versatile profiler for monitoring your machine learning training loops. `EpochMonitor` helps you track training time, CPU/RAM usage, and NVIDIA GPU memory usage with minimal code changes.

Get crucial insights into your model's performance and resource consumption, all presented with a clean, dynamic progress bar.

[Image of a dynamic terminal progress bar]

---

## Features

- **Easy Integration**: Use it as a simple function decorator or a flexible context manager.
- **Comprehensive Metrics**: Tracks epoch duration, total training time, CPU utilization, and RAM usage (in % and MB).
- **NVIDIA GPU Support**: Automatically detects NVIDIA GPUs and monitors memory usage per epoch.
- **Dynamic Display**: Uses `tqdm` to provide a clean, non-disruptive progress bar that updates in place.
- **Flexible Logging**: Automatically saves a detailed history of all metrics to a CSV or JSON file for later analysis.
- **Multi-GPU Aware**: Allows you to specify which GPU to monitor on systems with multiple cards.

---

## Installation

You can install `EpochMonitor` directly from PyPI:

```bash
pip install epochmonitor
```


## Usage

### As a Decorator (Simplest Method)

Just add `@EpochMonitor()` on top of your training function.  
The monitor object will be injected into your function as a keyword argument.

```python
import time
from epochmonitor import EpochMonitor
from tqdm import tqdm

@EpochMonitor(log_file_prefix="my_model_log", file_format="json")
def train_my_model(epochs, learning_rate, monitor=None):
    for epoch in tqdm(range(epochs), desc="Training Model"):
        monitor.start_epoch()
        print(f"-> Training with lr={learning_rate}...")
        time.sleep(2)  # Simulating work
        monitor.end_epoch()

train_my_model(epochs=5, learning_rate=0.01)
```


### As a Context Manager (More Control)

Use a `with` statement for explicit control.

```python
import time
from epochmonitor import EpochMonitor
from tqdm import tqdm

def another_training_run(epochs):
    with EpochMonitor(log_file_prefix="context_run_log") as monitor:
        for epoch in tqdm(range(epochs), desc="Training Model"):
            monitor.start_epoch()
            time.sleep(1.5)  # Simulating work
            monitor.end_epoch()

another_training_run(epochs=3)
```


### Listing Available GPUs
If you have multiple GPUs, list them first:
```python
from epochmonitor import EpochMonitor

# Prints all detected NVIDIA GPUs and indices
EpochMonitor.list_gpus()

# Example: Monitor GPU at index 1
# @EpochMonitor(gpu_index=1)
# def train_on_second_gpu(...):
#     ...
```

### Contributing
Contributions are welcome!
Whether it's:

    Reporting a bug 🐛

    Suggesting a feature 💡

    Submitting a pull request 📥

Please read the Contributing Guidelines before starting.

### License

This project is licensed under the MIT License.
See the LICENSE file for details.