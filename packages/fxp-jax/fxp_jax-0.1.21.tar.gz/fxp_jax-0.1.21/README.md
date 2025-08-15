[![PyPI version](https://img.shields.io/pypi/v/fxp-jax.svg)](https://pypi.org/project/fxp-jax/)
[![CI](https://github.com/esbenscriver/fxp-jax/actions/workflows/ci.yml/badge.svg)](https://github.com/esbenscriver/fxp-jax/actions/workflows/ci.yml)
[![CD](https://github.com/esbenscriver/fxp-jax/actions/workflows/cd.yml/badge.svg)](https://github.com/esbenscriver/fxp-jax/actions/workflows/cd.yml)
# Fixed-point solver
FixedPointJAX is a simple implementation of a fixed-point iteration algorithm for root finding in JAX. The implementation allow the user to solve the system of fixed point equations by standard fixed point iterations and the SQUAREM accelerator, see [Du and Varadhan (2020)](https://www.jstatsoft.org/article/view/v092i07).

## Installation

```bash
pip install fxp-jax
```

## Usage

```python

import jax.numpy as jnp
from jax import random

from fxp_jax import fxp_root

# Define the logit probabilities
def logit(x, axis=1):
	nominator = jnp.exp(x - jnp.max(x, axis=axis, keepdims=True))
	denominator = jnp.sum(nominator, axis=axis, keepdims=True)
	return nominator / denominator
	
# Define the function for the fixed-point iteration
def fun(x):
	s = logit(x)
	z = jnp.log(s0 / s)
	return x + z, z

# Dimensions of system of fixed-point equations
I, J = 3, 4

# Simulate probabilities
s0 = random.dirichlet(key=random.PRNGKey(123), alpha=jnp.ones((J,)), shape=(I,))

# Initial guess
x0 = jnp.zeros_like(s0)

print('--------------------------------------------------------')
# Solve the fixed-point equation
fxp = fxp_root(
        fun,
    )
result = fxp.solve(guess=jnp.zeros_like(s0), accelerator="None")
print('--------------------------------------------------------')
print(f'System of fixed-point equations is solved: {jnp.allclose(result.x,fun(result.x)[0])}.')
print(f'Probabilities are identical: {jnp.allclose(s0, logit(result.x))}.')
print('--------------------------------------------------------')
```
