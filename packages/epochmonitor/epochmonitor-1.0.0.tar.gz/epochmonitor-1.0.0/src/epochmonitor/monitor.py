import time
import psutil
import csv
import json
from functools import wraps
from tqdm import tqdm

# Try to import NVIDIA library, handle case where it's not installed
try:
    import pynvml

    pynvml.nvmlInit()
    GPU_AVAILABLE = True
except (ImportError, pynvml.NVMLError):
    GPU_AVAILABLE = False


class EpochMonitor:
    """
    A versatile profiler for machine learning training loops.

    Tracks time, CPU, RAM, and NVIDIA GPU usage per epoch with a dynamic display.

    Args:
        log_file_prefix (str): Prefix for the log file name.
        file_format (str): 'csv' or 'json' for the log file format.
        gpu_index (int): The index of the NVIDIA GPU to monitor (default: 0).
    """

    def __init__(self, log_file_prefix="training_log", file_format="csv", gpu_index=0):
        self.log_file_prefix = log_file_prefix
        self.file_format = file_format.lower()
        self.gpu_index = gpu_index
        self.history = []
        self.epoch_start_time = None
        self.total_start_time = None

        if GPU_AVAILABLE:
            try:
                self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_index)
            except pynvml.NVMLError:
                print(
                    f"Warning: GPU with index {self.gpu_index} not found. Disabling GPU monitoring."
                )
                self.gpu_handle = None
        else:
            self.gpu_handle = None

    @staticmethod
    def list_gpus():
        """Lists available NVIDIA GPUs and their indices."""
        if not GPU_AVAILABLE:
            print("NVIDIA driver or pynvml is not installed. Cannot list GPUs.")
            return

        try:
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count == 0:
                print("No NVIDIA GPUs found.")
                return

            print(f"Found {device_count} NVIDIA GPU(s):")
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                print(f"  - Index {i}: {name}")
        except Exception as e:
            print(f"An error occurred while listing GPUs: {e}")

    def _get_stats(self):
        """Fetches the current system and GPU stats."""
        ram_info = psutil.virtual_memory()  # Get RAM info object
        stats = {
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": ram_info.percent,
            "ram_used_mb": ram_info.used
            / (1024**2),  # New line: Calculate used RAM in MB
            "gpu_mem_percent": "N/A",
            "gpu_mem_used_mb": "N/A",
        }
        if self.gpu_handle:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            stats["gpu_mem_percent"] = f"{(mem_info.used / mem_info.total) * 100:.2f}"
            stats["gpu_mem_used_mb"] = mem_info.used / (1024**2)
        return stats

    def start_epoch(self):
        """Marks the beginning of an epoch."""
        self.epoch_start_time = time.time()

    def end_epoch(self):
        """Marks the end of an epoch, calculates duration, and logs stats."""
        if self.epoch_start_time:
            duration = time.time() - self.epoch_start_time
            stats = self._get_stats()

            epoch_data = {
                "epoch": len(self.history) + 1,
                "duration_seconds": round(duration, 2),
                **stats,
            }
            self.history.append(epoch_data)

            # Updated log_str to include the new RAM metric
            log_str = (
                f"Epoch {epoch_data['epoch']} Summary | "
                f"Duration: {epoch_data['duration_seconds']}s, "
                f"CPU: {epoch_data['cpu_percent']}%, "
                f"RAM: {epoch_data['ram_used_mb']:.2f}MB ({epoch_data['ram_percent']}%)"
            )
            if self.gpu_handle:
                log_str += f", GPU Mem: {epoch_data['gpu_mem_used_mb']:.2f}MB"

            tqdm.write(log_str)
            self.epoch_start_time = None

    def __call__(self, func):
        """Allows the class to be used as a decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self as monitor:
                return func(*args, monitor=monitor, **kwargs)

        return wrapper

    def __enter__(self):
        """Context manager entry."""
        self.total_start_time = time.time()
        tqdm.write("🚀 Starting Training Run...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: print summary and save logs."""
        total_duration = time.time() - self.total_start_time
        summary = "\n" + "=" * 30 + "\n🎉 Training Run Finished!\n"
        summary += f"Total Time: {total_duration:.2f}s\n"
        if self.history:
            avg_epoch_time = sum(e["duration_seconds"] for e in self.history) / len(
                self.history
            )
            summary += f"Average Epoch Time: {avg_epoch_time:.2f}s\n"
            self._save_log()
        summary += "=" * 30
        tqdm.write(summary)

        # if GPU_AVAILABLE:
        #     pynvml.nvmlShutdown()

    def _save_log(self):
        filename = f"{self.log_file_prefix}.{self.file_format}"
        try:
            with open(filename, "w", newline="") as f:
                if self.file_format == "csv" and self.history:
                    writer = csv.DictWriter(f, fieldnames=self.history[0].keys())
                    writer.writeheader()
                    writer.writerows(self.history)
                elif self.file_format == "json":
                    json.dump(self.history, f, indent=4)
            tqdm.write(f"Log saved to '{filename}'")
        except Exception as e:
            tqdm.write(f"Error saving log file: {e}")


# --- Example Usage ---
@EpochMonitor(log_file_prefix="my_model_v1_log", gpu_index=0)
def train_model(epochs, monitor=None):
    for _ in tqdm(range(epochs), desc="Training Progress"):
        monitor.start_epoch()
        time.sleep(2)
        monitor.end_epoch()


if __name__ == "__main__":
    EpochMonitor.list_gpus()
    train_model(epochs=3)
