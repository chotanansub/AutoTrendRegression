# 📈 Sliding Window Linear Regression Ensemble

This method performs localized linear regression over a time series using a sliding window. It iteratively refines its focus on high-error regions based on prediction performance.

---

Demo: [Google Colab](https://colab.research.google.com/drive/1jifMsj8nI_ZV-FL3ZScFP4wJJLQp97jH?usp=sharing)



## Problem Setup

Given a univariate sequence:

```
y = [y_0, y_1, ..., y_T]
```

We aim to predict future values using local linear trends and adaptively refocus on regions with large prediction errors.

---

## Parameters

- `w`: Window size for local regression  
- `N`: Number of iterations (ensemble rounds)  
- `p(i)`: Error percentile threshold at iteration `i`

---

## Algorithm Description

### 1. Initialization

Define initial windows:

```
W(0) = {(t, t + w) | t = 0 to T - w}
```

---

### 2. Linear Model Training

For a given window `(t, t+w)`:

- Input: `X = [0, 1, ..., w-1]`
- Target: `y = [y_t, y_{t+1}, ..., y_{t+w-1}]`
- Fit a line: `ŷ_{t+k} = a * k + b`
- Compute trend offset: `Δ = ŷ_w - y_t`

---

### 3. Prediction and Error Evaluation

For each target index `t`:

- Predict: `ŷ_t = y_{t-w} + Δ`
- Error: `e_t = |y_t - ŷ_t|`

---

### 4. Focus Refinement

- Threshold: `τ(i) = percentile(e, p(i))`
- High-error indices:  
  ```
  I(i+1) = { t | e_t > τ(i) }
  ```
- Group into ranges:  
  ```
  R(i+1) = contiguous_ranges(I(i+1))
  ```

---

### 5. Iterative Training

Repeat steps 2–4 for `i = 1 to N`, incrementing `p(i)` at each step.  
Stop early if no high-error regions remain.

---

## Output Per Iteration

Each iteration returns:

- `ŷ(i)`: Predicted values  
- `e(i)`: Filtered error values  
- `R(i)`: Focused high-error ranges

---

## Use Cases

- Detecting local trend or non-stationarity  
- Improving forecasting in regions where error is high  
