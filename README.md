# 📈 AutoTrend: Local Linear Trend Extraction

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**AutoTrend** is a lightweight, iterative method for extracting local linear trends from time series data. Unlike traditional sliding window approaches that fit a model at every point, AutoTrend achieves computational efficiency by training a single linear regression model per focus region and extending the trend forward, measuring prediction errors without repeated model fitting.

#### 🚀 Demo: [Google Colab](https://colab.research.google.com/drive/1jifMsj8nI_ZV-FL3ZScFP4wJJLQp97jH?usp=sharing)

---

## 🚀 Quick Start

```python
import numpy as np
from autotrend import decompose_llt, plot_full_decomposition

# Generate or load your time series
sequence = np.sin(np.linspace(0, 50, 500)) + np.linspace(0, 5, 500)

# Run LLT decomposition
result = decompose_llt(
    seq=sequence,
    max_models=5,
    window_size=10,
    error_percentile=40
)

# Visualize results
plot_full_decomposition(sequence, result)

# Access results
print(f"Number of iterations: {result.get_num_iterations()}")
print(f"Trend segments: {result.get_trend_segments()}")
```

**Output:**
- `result.trend_marks`: Array indicating which iteration labeled each point
- `result.prediction_marks`: Predicted values for each point
- `result.models`: List of LinearRegression models from each iteration
- `result.process_logs`: Detailed logs for visualization

---

## 💡 Core Concept

### The Problem
Traditional sliding window regression methods fit a new model at every time point, leading to high computational costs. Change point detection methods often require complex algorithms and parameter tuning.

### The Solution
AutoTrend uses an **iterative, focus-based approach**:

1. **Single Model per Region**: Train one linear regression model at the start of each focus region
2. **Trend Extension**: Extend the trend line forward without retraining
3. **Error-Based Refinement**: Identify high-error points and focus on them in the next iteration
4. **Adaptive Segmentation**: Automatically discover trend boundaries based on prediction error

### Key Advantages

✅ **Computationally Efficient**: Minimal model training compared to full sliding windows  
✅ **Adaptive**: Automatically discovers trend boundaries without predefined change points  
✅ **Interpretable**: Clear linear segments with explicit slopes and intercepts  
✅ **Flexible**: Adjustable error thresholds and iteration limits  
✅ **Lightweight**: No complex optimization or parameter search required

---

## ⚙️ Algorithm Overview

### Input
- **Sequence**: Univariate time series `y = [y₀, y₁, ..., yₜ]`
- **Parameters**:
  - `window_size`: Size of training window (default: 10)
  - `max_models`: Maximum iterations (default: 5)
  - `error_percentile`: Error threshold percentile (default: 40)
  - `percentile_step`: Increment per iteration (default: 0)
  - `update_threshold`: Whether to update threshold each iteration (default: False)

### Process

#### **Step 1: Initialization**
Define initial focus targets covering all predictable points:
```
focus_targets = [window_size, window_size+1, ..., T-1]
```

#### **Step 2: Train Linear Model**
For each iteration, train a model on the first window of the focus region:
```python
X_train = [0, 1, ..., window_size-1]
y_train = sequence[start:end]
model = LinearRegression().fit(X_train, y_train)
```

#### **Step 3: Extend Trend and Measure Error**
Predict forward using the trained model's trend offset:
```
Δ = ŷ_window_size - y_start
ŷ_t = y_(t-window_size) + Δ
error_t = |y_t - ŷ_t|
```

#### **Step 4: Segment by Error Threshold**
```python
threshold = percentile(errors, error_percentile)
low_error_points = {t | error_t ≤ threshold}
high_error_points = {t | error_t > threshold}
```

- **Low error points**: Assigned to current iteration, marked as resolved
- **High error points**: Become focus targets for next iteration

#### **Step 5: Iterate**
Repeat Steps 2-4 on high-error regions until:
- All points meet the error criterion, OR
- Maximum iterations reached

### Output
```python
LLTResult(
    trend_marks: np.ndarray,      # Iteration labels for each point
    prediction_marks: np.ndarray,  # Predicted values
    models: List[LinearRegression], # Trained models per iteration
    process_logs: List[Tuple]      # Detailed iteration logs
)
```

---

## 📂 Directory Structure

```
autotrend/
├── autotrend/
│   ├── __init__.py                    # Main package exports
│   ├── core/
│   │   ├── __init__.py
│   │   ├── local_linear_trend.py      # Core LLT algorithm
│   │   └── utility.py                 # Helper functions (extract_ranges, split_by_gap)
│   ├── data/
│   │   ├── __init__.py
│   │   └── gen_data.py                # Synthetic data generators
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plot.py                    # Main plotting module
│   │   ├── plot_error.py              # Error analysis visualization
│   │   ├── plot_slope.py              # Slope comparison plots
│   │   ├── plot_full_decomposition.py # Full decomposition view
│   │   ├── plot_iteration_grid.py     # Iteration grid visualization
│   │   └── plot_model_statistics.py   # Model statistics plots
│   └── decomposition/
│       └── __init__.py                # Future: Trend-seasonal decomposition
├── demo/
│   ├── demo_utils.py                  # Demo configuration and utilities
│   ├── simple_wave.py                 # Sine wave demo
│   ├── piecewise_linear.py            # Piecewise linear demo
│   └── run_all.py                     # Run all demos
├── output/                            # Generated plots and logs
│   ├── simple_wave/
│   └── piecewise_linear/
├── README.md
└── requirements.txt
```