# MathUtils

mathematical utilities with C++ backend for high-performance numerical computations.



# Create build venv
python -m venv .venv/mathutils_build
source .venv/mathutils_build/bin/activate
pip install build twine
# Clean previous builds
rm -rf dist/ build/ *.egg-info
# Build source distribution and wheel
python -m build
# Verify files were created
ls -la dist/
# Check package validity
python -m twine check dist/*
# Upload only .tar.gz to avoid platform-specific wheel issues
python -m twine upload dist/*.tar.gz
# test
deactivate
python -m venv .venv/mathutils_test
source .venv/mathutils_test/bin/activate
pip install -r requirements_testing.txt


in C++ 

`(false)`$\mapsto$ `0`

`(true)`$\mapsto$ `1`

`0`$\mapsto$ `false`

`1`$\mapsto$ `true`

`13`$\mapsto$ `true`

<!-- # MathUtils

Fast mathematical utilities with optimized C++ backend for high-performance numerical computations.

## Features

- **Fast factorial computations**: Optimized log-factorial with lookup tables
- **Spherical harmonics**: High-performance Ylm calculations  
- **C++ backend**: Optimized implementations with Python bindings
- **NumPy integration**: Seamless array operations
- **Vectorized operations**: Process arrays efficiently

## Installation

```bash
pip install mathutils-fast
```

## Quick Start

```python
import mathutils
import numpy as np

# Fast log factorial
result = mathutils.log_factorial(100)
print(f"log(100!) = {result}")

# Vectorized spherical harmonics
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 100)
ylm = mathutils.Ylm_vectorized(2, 1, theta, phi)
print(f"Y_2^1 shape: {ylm.shape}, dtype: {ylm.dtype}")
```

## Spherical Harmonics

The spherical harmonics $Y_{\ell}^m(\theta, \phi)$ are defined as:

$$
Y_{\ell}^m(\theta, \phi) = \sqrt{\frac{2\ell+1}{4\pi} \frac{(\ell-|m|)!}{(\ell+|m|)!}} P_{\ell}^{|m|}(\cos\theta) e^{im\phi}
$$

where:
- $\ell \geq 0$ is the degree (angular momentum quantum number)
- $-\ell \leq m \leq \ell$ is the order (magnetic quantum number)  
- $P_{\ell}^{|m|}$ are the associated Legendre polynomials
- $\theta \in [0, \pi]$ is the polar angle
- $\phi \in [0, 2\pi]$ is the azimuthal angle

From the Herglotz generating function, we find
$$
e^{-im\phi}Y_{\ell}^m(\theta, \phi)
= 
r_{\ell, m, \theta}
\sum_{k=1}^{k_{max}}
Q_{k}
$$

$$
\log(q_0)
=
(1/2)\log(2\ell+1)
+
(1/2)\log((\ell+|m|)!)
-(1/2)\log((\ell-|m|)!)
-\log(|m|!)
-|m|\log(2)
$$

$$
\log(q_k)
=
(\ell-|m|)\log|\cos\theta|
+
|m|\log|\sin\theta|
$$

where:
- $k_{max} = \lfloor(\ell-|m|)/2\rfloor$ 

$$
e^{-im\phi}Y_{\ell}^m(\theta, \phi)
= 
(-1)^{(m+|m|)/2}
\sqrt{
\frac{
(2\ell+1)(\ell+|m|)!(\ell-|m|)!
}{
4^{|m|+1}
\pi
}
}
\sum_{k=0?}^{\lfloor(\ell-m)/2\rfloor}
\frac{
(-1)^k
\cos[k](\theta)
}
{
4^k
(\ell-|m|-2k)!
(|m|+k)!
k!
}
$$




### Special Properties

- **Orthonormality**: $\int_0^{2\pi} d\phi \int_0^{\pi} \sin\theta \, d\theta \, Y_{\ell}^m(\theta,\phi)^* Y_{\ell'}^{m'}(\theta,\phi) = \delta_{\ell\ell'}\delta_{mm'}$
- **Completeness**: Any function on the sphere can be expanded in spherical harmonics
- **Symmetry**: $Y_{\ell}^{-m}(\theta,\phi) = (-1)^m [Y_{\ell}^m(\theta,\phi)]^*$

## API Reference

### Core Functions

#### `log_factorial(n)`
Compute the natural logarithm of n!

```python
result = mathutils.log_factorial(50)  # Uses optimized C++ implementation
```

**Parameters:**
- `n` (int): Non-negative integer

**Returns:**
- `float`: ln(n!)

#### `Ylm_vectorized(l, m, theta, phi)`
Compute spherical harmonics for arrays of angles

```python
theta = np.linspace(0, np.pi, 50)
phi = np.linspace(0, 2*np.pi, 100)
ylm = mathutils.Ylm_vectorized(3, 2, theta, phi)
```

**Parameters:**
- `l` (int): Degree (l ≥ 0)
- `m` (int): Order (-l ≤ m ≤ l)
- `theta` (array_like): Polar angles in radians
- `phi` (array_like): Azimuthal angles in radians

**Returns:**
- `ndarray`: Complex array of Y_l^m values

### Indexing Functions

#### `spherical_harmonic_index_n_LM(l, m)`
Convert (l,m) quantum numbers to linear index

```python
index = mathutils.spherical_harmonic_index_n_LM(2, 1)  # Returns 5
```

#### `spherical_harmonic_index_lm_N(n)`
Convert linear index back to (l,m) quantum numbers

```python
l, m = mathutils.spherical_harmonic_index_lm_N(5)  # Returns (2, 1)
```

## Performance

MathUtils provides significant speedups over pure Python implementations:

```python
import time
import numpy as np
import mathutils

# Benchmark log_factorial
n = 1000
start = time.time()
for i in range(10000):
    result = mathutils.log_factorial(n)
cpp_time = time.time() - start

# Compare with Python
import math
start = time.time()
for i in range(10000):
    result = math.lgamma(n + 1)
python_time = time.time() - start

print(f"Speedup: {python_time/cpp_time:.2f}x")
```

## Examples

### Plotting Spherical Harmonics

```python
import numpy as np
import matplotlib.pyplot as plt
import mathutils

# Create sphere coordinates
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2*np.pi, 200)
theta_grid, phi_grid = np.meshgrid(theta, phi, indexing='ij')

# Compute Y_2^1
l, m = 2, 1
ylm = mathutils.Ylm_vectorized(l, m, theta_grid.flatten(), phi_grid.flatten())
ylm = ylm.reshape(theta_grid.shape)

# Plot real part
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
x = np.sin(theta_grid) * np.cos(phi_grid)
y = np.sin(theta_grid) * np.sin(phi_grid)  
z = np.cos(theta_grid)

colors = plt.cm.seismic(ylm.real / np.max(np.abs(ylm.real)))
ax.plot_surface(x, y, z, facecolors=colors, alpha=0.8)
ax.set_title(f'$Y_{{{l}}}^{{{m}}}$ (Real Part)')
plt.show()
```

### Spherical Harmonic Analysis

```python
import numpy as np
import mathutils

def analyze_function_on_sphere(func, l_max=10):
    """Decompose a function into spherical harmonic coefficients."""
    
    # Create integration grid
    n_theta, n_phi = 2*l_max+1, 4*l_max+1
    theta = np.linspace(0, np.pi, n_theta)
    phi = np.linspace(0, 2*np.pi, n_phi)
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing='ij')
    
    # Evaluate function on grid
    f_values = func(theta_grid, phi_grid)
    
    # Compute coefficients
    coefficients = {}
    for l in range(l_max + 1):
        for m in range(-l, l + 1):
            ylm = mathutils.Ylm_vectorized(l, m, theta_grid.flatten(), phi_grid.flatten())
            ylm = ylm.reshape(theta_grid.shape)
            
            # Numerical integration
            integrand = f_values * np.conj(ylm) * np.sin(theta_grid)
            coeff = np.trapz(np.trapz(integrand, phi), theta)
            coefficients[(l, m)] = coeff
    
    return coefficients

# Example: analyze a simple function
def my_function(theta, phi):
    return np.cos(theta) + np.sin(theta) * np.cos(phi)

coeffs = analyze_function_on_sphere(my_function, l_max=5)
print("Dominant coefficients:")
for (l, m), coeff in sorted(coeffs.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
    print(f"Y_{l}^{m}: {coeff:.6f}")
```

## Requirements

- Python ≥ 3.8
- NumPy ≥ 1.20.0
- C++17 compatible compiler (for building from source)

## Building from Source

```bash
git clone https://github.com/yourusername/mathutils.git
cd mathutils
pip install -e .
```

### Dependencies for Building
- CMake ≥ 3.15
- Eigen3 library
- pybind11

## Testing

```bash
# Install test dependencies
pip install pytest numpy

# Run tests
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use MathUtils in your research, please cite:

```bibtex
@software{mathutils2024,
  title={MathUtils: Fast Mathematical Utilities with C++ Backend},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/mathutils}
}
```

## Acknowledgments

- Built with [pybind11](https://github.com/pybind/pybind11)
- Uses [Eigen](https://eigen.tuxfamily.org/) for linear algebra
- Inspired by [SciPy](https://scipy.org/) special functions


# Step-by-Step Guide: Publishing Python Package with C++ Extensions to PyPI

## Prerequisites
- Python package with C++ extensions (using pybind11)
- GitHub repository
- C++ code compiles successfully locally

## Step 1: Package Configuration

### 1.1 Create/Update `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=61.0", "pybind11", "numpy"]
build-backend = "setuptools.build_meta"

[project]
name = "your-unique-package-name"  # Check if name is available on PyPI
version = "0.1.0"
description = "Your package description"
authors = [{ name = "Your Name", email = "your.email@example.com" }]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.7"
dependencies = ["numpy", "scipy"]  # Add your dependencies
keywords = ["mathematics", "scientific-computing"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Mathematics",
]

[project.urls]
Homepage = "https://github.com/yourusername/yourrepo"
Repository = "https://github.com/yourusername/yourrepo"
Issues = "https://github.com/yourusername/yourrepo/issues"

[project.optional-dependencies]
dev = ["pytest", "build", "twine"]

[tool.setuptools]
packages = ["your_module_name"]

[tool.setuptools.package-dir]
your_module_name = "your_module_name"
```

### 1.2 Create `MANIFEST.in`
```plaintext
include README.md
include pyproject.toml
recursive-include include *.hpp
recursive-include src *.cpp
```

### 1.3 Fix `__init__.py` imports
```python
"""Your Package - Description."""

try:
    from .your_backend import *
except ImportError as e:
    raise ImportError(f"Failed to import C++ backend: {e}")

__version__ = "0.1.0"
```

### 1.4 Ensure `setup.py` has correct paths
```python
from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11

ext_modules = [
    Pybind11Extension(
        "your_module.your_backend",
        ["src/cpp/bindings.cpp"],
        include_dirs=[
            "include",
            "/usr/include/eigen3",  # If using Eigen
        ],
        cxx_std=17,
        define_macros=[("VERSION_INFO", '"dev"')],
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
```

## Step 2: Build Setup

### 2.1 Install build tools
```bash
pip install build twine
```

### 2.2 Clean and build package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

### 2.3 Check build results
```bash
# Verify files were created
ls -la dist/

# Check package validity
python -m twine check dist/*
```

## Step 3: PyPI Account Setup

### 3.1 Create PyPI account
- Go to https://pypi.org/account/register/
- Create account and verify email

### 3.2 Create API token
- Go to https://pypi.org/manage/account/token/
- Create new token with scope "Entire account"
- Copy the token (starts with `pypi-`)

## Step 4: Upload to PyPI

### 4.1 Upload source distribution only
```bash
# Upload only .tar.gz to avoid platform-specific wheel issues
python -m twine upload dist/*.tar.gz
```

### 4.2 Enter credentials when prompted
- Username: `__token__`
- Password: Your API token

## Step 5: Test Installation

### 5.1 Test install
```bash
pip install your-package-name
```

### 5.2 Test import
```python
import your_module
print("Success!")
```

## Step 6: (Optional) GitHub Actions for Automated Publishing

### 6.1 Create `.github/workflows/publish.yml`
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y libeigen3-dev  # If using Eigen
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*.tar.gz
```

### 6.2 Add PyPI token to GitHub secrets
- Go to GitHub repo → Settings → Secrets and variables → Actions
- Add secret: `PYPI_API_TOKEN` = your PyPI token

## Step 7: Future Releases

### 7.1 For new versions
```bash
# 1. Update version in pyproject.toml
# 2. Clean and rebuild
rm -rf dist/ build/ *.egg-info
python -m build

# 3. Upload
python -m twine upload dist/*.tar.gz
```

### 7.2 Or use GitHub releases (if using Actions)
- Create new GitHub release with tag like `v0.2.0`
- GitHub Actions will automatically publish to PyPI

## Common Issues and Solutions

### Issue: "Binary wheel has unsupported platform tag"
**Solution**: Upload only source distribution (`*.tar.gz`)

### Issue: "Invalid authentication"
**Solutions**:
- Verify email on PyPI
- Create fresh API token
- Use `__token__` as username

### Issue: "Package name already exists"
**Solution**: Choose unique name like `yourpackage-username`

### Issue: C++ compilation fails
**Solutions**:
- Check `include_dirs` in `setup.py`
- Ensure `MANIFEST.in` includes all necessary files
- Install system dependencies (like Eigen)

## Verification Checklist

- [ ] Package builds successfully (`python -m build`)
- [ ] Package checks pass (`python -m twine check dist/*`)
- [ ] PyPI account created and email verified
- [ ] API token created and saved
- [ ] Package name is unique
- [ ] Upload successful
- [ ] Package installs via pip
- [ ] Package imports correctly

## Result

Your package will be available at:
`https://pypi.org/project/your-package-name/`

Users can install with:
```bash
pip install your-package-name
``` -->


