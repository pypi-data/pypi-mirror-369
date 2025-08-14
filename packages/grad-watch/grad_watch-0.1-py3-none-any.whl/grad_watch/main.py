
import torch
from collections import defaultdict

class GradientMonitor:
    def __init__(self, model, explode_threshold=1e3, vanish_threshold=1e-6):
        self.model = model
        self.explode_threshold = explode_threshold
        self.vanish_threshold = vanish_threshold
        self.history = defaultdict(list)
        self._register_hooks()

    def _register_hooks(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                param.register_hook(lambda grad, name=name: self._log_grad(name, grad))

    def _log_grad(self, name, grad):
        if grad is None:
            return
        grad_abs = grad.abs()
        max_val = grad_abs.max().item()
        min_val = grad_abs.min().item()
        mean_val = grad_abs.mean().item()

        self.history[name].append({"max": max_val, "min": min_val, "mean": mean_val})

        if max_val > self.explode_threshold:
            print(f"⚠️ Exploding gradient in {name} (max={max_val:.4e})")
        if mean_val < self.vanish_threshold:
            print(f"⚠️ Vanishing gradient in {name} (mean={mean_val:.4e})")

    def get_history(self):
        return dict(self.history)

    def plot(self, layer_name):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib is required for plotting. Install with `pip install matplotlib`.")

        if layer_name not in self.history:
            raise ValueError(f"No history for layer '{layer_name}'.")

        max_vals = [x["max"] for x in self.history[layer_name]]
        mean_vals = [x["mean"] for x in self.history[layer_name]]

        plt.figure(figsize=(8,4))
        plt.plot(max_vals, label="Max Gradient")
        plt.plot(mean_vals, label="Mean Gradient")
        plt.title(f"Gradient Trends - {layer_name}")
        plt.xlabel("Steps")
        plt.ylabel("Gradient Magnitude")
        plt.legend()
        plt.grid(True)
        plt.show()


# Example usage only when running directly
if __name__ == "__main__":
    import torch.nn as nn
    import torch.optim as optim

    model = nn.Sequential(nn.Linear(10, 50), nn.ReLU(), nn.Linear(50, 1))
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    grad_monitor = GradientMonitor(model)

    for step in range(5):
        x = torch.randn(16, 10)
        y = torch.randn(16, 1)
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

    grad_monitor.plot("0.weight")
