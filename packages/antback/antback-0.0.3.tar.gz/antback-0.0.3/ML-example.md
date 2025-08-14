# Antback: Machine Learning-Driven Trading Strategy Example

[![Antback Logo](https://github.com/ts-kontakt/antback/blob/main/antback-report.png?raw=true)](https://github.com/ts-kontakt/antback)

**Antback** is a fast, transparent, and debuggable backtesting engine for Python. This repository demonstrates an advanced use case: a **machine learning-powered trading strategy** that combines technical indicators, feature engineering, and walk-forward backtesting using state-of-the-art tools.

> 🔍 *No black boxes — every signal, trade, and prediction is visible and inspectable.*

---

## 📌 Overview

This example implements a predictive trading strategy using:
- **Feature Engineering**: Rolling technical and temporal features
- **Target Definition**: Forward-looking returns (e.g., 2-day ahead)
- **Model Training**: `LGBMClassifier` (LightGBM) for high-performance classification
- **Backtesting**: Event-driven simulation with realistic execution logic via **Antback**

The pipeline is fully sequential, avoiding lookahead bias, and supports interactive reporting for deep analysis.

---

## 🧠 Strategy Logic

### 1. Feature Extraction
A rich set of features is computed over a rolling window (default: 90 days) using `NamedRollingLists`:
- **Technical Indicators**: RSI, ROC, EMA crossovers
- **Candlestick Patterns**: Tall candles, lower lows, gap detection
- **Price Action**: Drawdowns, open-close volatility
- **Temporal Features**: Day of week, start/end of month

These are aggregated using a custom `get_aggregation_function`.

### 2. Target Generation
The target is defined as:
```python
target = 1 if forward_return > 0.01 else 0