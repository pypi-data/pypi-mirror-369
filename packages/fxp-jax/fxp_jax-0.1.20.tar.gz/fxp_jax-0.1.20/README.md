[![PyPI](https://badge.fury.io/py/FixedPointJAX.svg)](https://badge.fury.io/py/FixedPointJAX)
[![CI](https://github.com/esbenscriver/FixedPointJAX/actions/workflows/ci.yml/badge.svg)](https://github.com/esbenscriver/FixedPointJAX/actions)
# Fixed-point solver
FixedPointJAX is a simple implementation of a fixed-point iteration algorithm for root finding in JAX. The implementation allow the user to solve the system of fixed point equations by standard fixed point iterations and the SQUAREM accelerator, see [Du and Varadhan (2020)](https://www.jstatsoft.org/article/view/v092i07).

* Strives to be minimal
* Has no dependencies other than JAX

## Installation

```bash
pip install FixedPointJAX
```

## Usage

```python

import jax.numpy as jnp
from jax import random

from FixedPointJAX import FixedPointRoot

# Define the logit probabilities
def logit(x, axis=1):
	nominator = jnp.exp(x - jnp.max(x, axis=axis, keepdims=True))
	denominator = jnp.sum(nominator, axis=axis, keepdims=True)
	return nominator / denominator
	
# Define the function for the fixed-point iteration
def fxp(x):
	s = logit(x)
	z = jnp.log(s0 / s)
	return x + z, z

# Dimensions of system of fixed-point equations
I, J = 3, 4

# Simulate probabilities
s0 = random.dirichlet(key=random.PRNGKey(123), alpha=jnp.ones((J,)), shape=(I,))

# Initial guess
x0 = jnp.zeros_like(s0)

print('-----------------------------------------')
# Solve the fixed-point equation
x, (step_norm, root_norm, iterations) = FixedPointRoot(fxp, x0)
print('-----------------------------------------')
print(f'System of fixed-point equations is solved: {jnp.allclose(x,fxp(x)[0])}.')
print(f'Probabilities are identical: {jnp.allclose(s0, logit(x))}.')
print('-----------------------------------------')
```
