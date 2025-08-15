# 🚀 PyMBO - Python Multi-objective Bayesian Optimization

[![PyPI version](https://badge.fury.io/py/pymbo.svg)](https://pypi.org/project/pymbo/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![GitHub stars](https://img.shields.io/github/stars/jakub-jagielski/pymbo)](https://github.com/jakub-jagielski/pymbo/stargazers)

> **A comprehensive multi-objective Bayesian optimization framework with advanced visualization and screening capabilities.**

Transform your optimization challenges with PyMBO's intuitive GUI, powerful algorithms, and real-time visualizations. Perfect for researchers, engineers, and data scientists working with complex parameter spaces.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **Multi-objective Optimization** | Advanced Bayesian optimization with PyTorch/BoTorch backend |
| ⚡ **Hybrid Sequential/Parallel** | Intelligent switching between sequential and parallel execution modes |
| 📊 **Real-time Visualizations** | Interactive acquisition function heatmaps and 3D surfaces |
| 🔍 **SGLBO Screening** | Efficient parameter space exploration before detailed optimization |
| 🎮 **Interactive GUI** | User-friendly interface with drag-and-drop controls |
| 📈 **Comprehensive Analytics** | Parameter importance, correlation analysis, and trend visualization |
| 🚀 **Strategy Benchmarking** | Compare multiple optimization algorithms in parallel |
| 💾 **Export & Reporting** | Generate detailed reports in multiple formats |
| 🔬 **Scientific Utilities** | Built-in validation and analysis tools |

## 🚀 Quick Start

### Installation (Recommended)

```bash
pip install pymbo
```

### Run the Application

```bash
python -m pymbo
```

**That's it!** 🎉 PyMBO will launch with a modern GUI ready for your optimization projects.

### Alternative Installation

If you prefer to install from source:

```bash
git clone https://github.com/jakub-jagielski/pymbo.git
cd pymbo
pip install -r requirements.txt
python main.py
```

## 🎮 How to Use PyMBO

### 🖥️ **Graphical Interface**
Launch the GUI and follow these simple steps:

1. **🔧 Configure Parameters** - Define your optimization variables (continuous, discrete, categorical)
2. **🎯 Set Objectives** - Specify what you want to optimize (maximize, minimize, or target values)  
3. **▶️ Run Optimization** - Watch real-time visualizations as PyMBO finds optimal solutions
4. **📊 Analyze Results** - Export detailed reports and generate publication-ready plots

### 🔬 **SGLBO Screening Module**
For complex parameter spaces, start with efficient screening:

```bash
python -m pymbo  # Launch GUI → Select "SGLBO Screening"
```

**Screening Features:**
- 📈 **Response Trends Over Time** - Track optimization progress
- 📊 **Parameter Importance Analysis** - Identify key variables  
- 🔄 **Correlation Matrix** - Understand parameter interactions
- 🎯 **Design Space Generation** - Create focused regions for detailed optimization

### 💻 **Programmatic Usage** 

```python
from pymbo import EnhancedMultiObjectiveOptimizer, SimpleController

# Basic optimization (sequential mode)
optimizer = EnhancedMultiObjectiveOptimizer(
    bounds=[(0, 10), (0, 10)],
    objectives=['maximize']
)

# Run optimization
controller = SimpleController(optimizer)
controller.run_optimization()
```

### ⚡ **Hybrid Parallel Optimization** 

PyMBO now features intelligent hybrid architecture that automatically switches between sequential and parallel execution:

```python
from pymbo.core.controller import SimpleController

# Initialize controller (now with hybrid orchestrator)
controller = SimpleController()

# This runs SEQUENTIALLY (interactive mode)
suggestions = controller.optimizer.suggest_next_experiment(n_suggestions=1)

# This runs in PARALLEL (benchmarking mode detected automatically)
benchmark_results = controller.benchmark_optimization_strategies(
    strategies=['ehvi', 'ei', 'random'],
    n_suggestions=10
)

# Parallel what-if analysis
what_if_results = controller.run_what_if_analysis([
    {'name': 'conservative', 'n_suggestions': 5},
    {'name': 'aggressive', 'n_suggestions': 15}
], parallel=True)
```

## 🏗️ Architecture

PyMBO is built with a modular architecture for maximum flexibility:

```
pymbo/
├── 🧠 core/          # Optimization algorithms, orchestrator, and controllers
│   ├── optimizer.py          # Core multi-objective optimization
│   ├── orchestrator.py       # Hybrid sequential/parallel architecture  
│   └── controller.py         # Enhanced controller with parallel methods
├── 🎮 gui/           # Interactive graphical interface
│   ├── gui.py                # Main application interface
│   └── parallel_optimization_controls.py  # Parallel optimization controls
├── 🔍 screening/     # SGLBO screening module  
├── 🛠️ utils/         # Plotting, reporting, and scientific utilities
├── 🧪 tests/         # Comprehensive test suite organized by category
│   ├── core/         # Core optimization tests
│   ├── gpu/          # GPU acceleration tests
│   ├── gui/          # GUI component tests
│   ├── performance/  # Performance benchmarks
│   ├── integration/  # Integration tests
│   ├── validation/   # Model validation tests
│   └── debug/        # Debug and fix verification tests
├── 🔧 scripts/       # Standalone utility scripts
├── 📚 examples/      # Usage examples and demonstrations
└── 📖 docs/          # Organized documentation
    ├── manuals/      # Complete user manuals
    ├── reports/      # Technical implementation reports
    └── summaries/    # Architecture and workflow overviews
```

### 🚀 **Hybrid Architecture Benefits**

The new hybrid sequential/parallel architecture provides:

- **🔄 Automatic Mode Detection**: Intelligently switches between sequential and parallel execution
- **⚡ Performance Gains**: 2-10x speedup for benchmarking and large-scale analysis  
- **🔒 Backward Compatibility**: All existing code continues to work unchanged
- **🎯 Smart Resource Usage**: Optimizes CPU and memory usage based on task type
- **📊 Built-in Benchmarking**: Compare multiple optimization strategies simultaneously

### 🔍 **Advanced Screening (SGLBO)**

The **Stochastic Gradient Line Bayesian Optimization** module revolutionizes parameter space exploration:

**Why Use SGLBO Screening?**
- ⚡ **10x Faster** initial exploration vs. full Bayesian optimization  
- 🎯 **Smart Parameter Selection** - Focus on variables that matter most
- 📊 **Rich Visualizations** - 4 different plot types for comprehensive analysis
- 🔄 **Seamless Integration** - Export results directly to main optimization

```python
from pymbo.screening import ScreeningOptimizer

# Quick screening setup
optimizer = ScreeningOptimizer(
    params_config=config["parameters"],
    responses_config=config["responses"]
)

# Get results with built-in analysis
results = optimizer.run_screening()
```

## ⚡ Advanced Parallel Features

### 🏁 **Strategy Benchmarking**

Compare multiple optimization algorithms simultaneously with automatic performance tracking:

```python
# Benchmark multiple strategies in parallel
benchmark_results = controller.benchmark_optimization_strategies(
    strategies=['ehvi', 'ei', 'random', 'weighted'],
    n_suggestions=20,
    parallel=True  # 5-10x faster than sequential
)

# Results include timing, convergence, and performance metrics
for strategy, result in benchmark_results.items():
    print(f"{strategy}: {result['execution_time']:.2f}s")
```

### 🔮 **What-If Analysis**

Run multiple optimization scenarios in parallel to explore different strategies:

```python
# Define multiple scenarios
scenarios = [
    {'name': 'conservative', 'n_suggestions': 5, 'strategy': 'ei'},
    {'name': 'aggressive', 'n_suggestions': 15, 'strategy': 'ehvi'},
    {'name': 'exploratory', 'n_suggestions': 10, 'strategy': 'random'}
]

# Run scenarios in parallel (2-10x faster)
what_if_results = controller.run_what_if_analysis(
    scenarios=scenarios, 
    parallel=True
)
```

### 📊 **Parallel Data Loading**

Process large historical datasets efficiently with parallel chunk processing:

```python
# Load large datasets in parallel chunks
loading_results = controller.load_large_dataset_parallel(
    data_df=large_historical_data,
    chunk_size=1000  # Process 1000 rows per chunk
)

# 3-8x faster than sequential loading for large datasets
```

### 🎮 **GUI Parallel Controls**

Access all parallel features through the intuitive GUI:

1. **Launch PyMBO**: `python -m pymbo`
2. **Navigate to**: "⚡ Parallel Optimization" tab
3. **Configure**: Select strategies, set parameters, choose parallel execution
4. **Monitor**: Real-time progress and performance statistics
5. **Analyze**: View detailed results and export reports

## 🎓 Academic Use & Licensing

### 📜 **License**: Creative Commons BY-NC-ND 4.0

PyMBO is **free for academic and research use**! 

✅ **Permitted:**
- Academic research projects
- Publishing results in journals, theses, conferences  
- Educational use in universities
- Non-commercial research applications

❌ **Not Permitted:**
- Commercial applications without license
- Redistribution of modified versions

> 📖 **For Researchers**: You can freely use PyMBO in your research and publish your findings. We encourage academic use!

## 📚 How to Cite

If PyMBO helps your research, please cite it:

```bibtex
@software{jagielski2025pymbo,
  author = {Jakub Jagielski},
  title = {PyMBO: A Python library for multivariate Bayesian optimization and stochastic Bayesian screening},
  version = {3.6.3},
  year = {2025},
  url = {https://github.com/jakub-jagielski/pymbo}
}
```

## 🧪 Development & Testing

### Running Tests

PyMBO includes a comprehensive test suite organized by category:

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test category
python tests/run_all_tests.py gpu          # GPU acceleration tests
python tests/run_all_tests.py gui          # GUI component tests
python tests/run_all_tests.py performance  # Performance benchmarks
python tests/run_all_tests.py core         # Core optimization tests

# Fast mode (skip performance tests)
python tests/run_all_tests.py --fast

# Verbose output
python tests/run_all_tests.py --verbose
```

### Project Structure for Developers

- **`pymbo/`**: Main package with core functionality
- **`tests/`**: Organized test suite with category-based structure
- **`scripts/`**: Standalone utility scripts for setup and maintenance
- **`examples/`**: Usage examples and implementation demonstrations
- **`docs/`**: Comprehensive documentation including manuals and reports

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. 💻 **Make** your changes  
4. ✅ **Add** tests if applicable (use appropriate `tests/` subdirectory)
5. 🧪 **Run** the test suite: `python tests/run_all_tests.py`
6. 📝 **Commit** changes (`git commit -m 'Add amazing feature'`)
7. 📤 **Push** to branch (`git push origin feature/amazing-feature`)
8. 🔄 **Open** a Pull Request

### 🐛 **Found a Bug?**
[Open an issue](https://github.com/jakub-jagielski/pymbo/issues) with:
- Clear description of the problem
- Steps to reproduce  
- Expected vs actual behavior
- System information (OS, Python version)

## ⭐ **Show Your Support**

If PyMBO helps your work, please:
- ⭐ **Star** this repository
- 🐦 **Share** with your colleagues  
- 📝 **Cite** in your publications
- 🤝 **Contribute** improvements

---

<div align="center">

**Made with ❤️ for the optimization community**

[⬆️ Back to Top](#-pymbo---python-multi-objective-bayesian-optimization)

</div>