from functools import lru_cache
from typing import Sequence, Union

import jax
import numpy as np

from .base import Generator, Generator1D


class Leja1D(Generator1D):
    """
    Generator for one-dimensional Leja nodes.

    Produces nested Leja nodes (default on [-1, 1]), with optional scaling to arbitrary bounded domains.
    """

    __nodes = np.array([0, 1, -1, 1 / np.sqrt(2), -1 / np.sqrt(2)])

    def __init__(self, domain: Union[jax.Array, np.ndarray, Sequence[float]] = None) -> None:
        """
        Initialize the one-dimensional Leja node generator.

        Parameters
        ----------
        domain : Union[jax.Array, np.ndarray, Sequence[float]], optional
            Endpoints of the domain. Defaults to `[-1, 1]` if not specified.
        """
        super().__init__(is_nested=True)
        self.__domain = domain
        self.__reference_domain = None
        if domain is not None:
            self.__domain = np.asarray(domain)
            self.__reference_domain = (-1, 1)
        self.__cached_call = self.__make_cached_call()
        self.__cached_get_quadrature_weights = self.__make_cached_get_quadrature_weights()

    @property
    def domain(self) -> Union[jax.Array, np.ndarray, Sequence[float]]:
        """
        Domain interval of the node sequence.

        Returns
        -------
        array-like of shape (2,)
        """
        return self.__domain

    @classmethod
    def __ensure_nodes(cls, n: int):
        k = cls.__nodes.shape[0]
        if n >= k:
            cls.__nodes = np.append(cls.__nodes, np.empty((n + 1 - k,)))
            for j in range(k, n + 1):
                if j % 2 == 0:
                    cls.__nodes[j] = -cls.__nodes[j - 1]
                else:
                    cls.__nodes[j] = np.sqrt((cls.__nodes[int((j + 1) / 2)] + 1) / 2)

    def __make_cached_call(self):
        @lru_cache(maxsize=None)
        def cached(n):
            self.__ensure_nodes(n)
            return self.scale(self.__nodes[: n + 1])

        return cached

    def __call__(self, n: int) -> Union[jax.Array, np.ndarray]:
        """
        Generate Leja nodes mapped to `self.domain`.

        Parameters
        ----------
        n : int
            Maximal node index (counting starts at `0`).

        Returns
        -------
        jax.Array or np.ndarray
            Leja nodes mapped to the `self.domain`.
        """
        return self.__cached_call(n)

    def __make_cached_get_quadrature_weights(self):
        @lru_cache(maxsize=None)
        def cached(n):
            self.__ensure_nodes(n)
            quadrature_points = self.__nodes[: n + 1]
            vm_matrix = np.vstack([quadrature_points**i for i in range(n + 1)])
            rhs = np.array([(1 + (-1) ** i) / (2.0 * (i + 1)) for i in range(n + 1)])
            quadrature_weights = np.linalg.solve(vm_matrix, rhs)
            return quadrature_weights

        return cached

    def scale(
        self,
        x: Union[jax.Array, np.ndarray],
        d1: Union[jax.Array, np.ndarray, Sequence[float]] = None,
        d2: Union[jax.Array, np.ndarray, Sequence[float]] = None,
    ) -> Union[jax.Array, np.ndarray]:
        """
        Map nodes or points from interval `d1` to interval `d2` by affine transformation.

        Mainly intended for internal use and testing.

        Parameters
        ----------
        x : array-like
            Points to transform.
        d1 : array-like of shape (2,), optional
            Source interval (default: reference domain `[-1, 1]`).
        d2 : array-like of shape (2,), optional
            Target interval (default: generator's domain).

        Returns
        -------
        jax.Array or np.ndarray
            Nodes or points in the target domain.
        """
        if d1 is None:
            d1 = self.__reference_domain
        if d2 is None:
            d2 = self.__domain

        assert (d1 is None) == (d2 is None)
        if d1 is None:  # no scaling if no custom domains are give
            return x

        # ensure d1, d2 have shape (2, )
        d1, d2 = np.squeeze(d1), np.squeeze(d2)
        assert d1.shape == d2.shape == (2,), f"shapes {d1.shape} and {d2.shape} do not match (2, )"
        assert d1[0] < d1[1]
        assert d2[0] < d2[1]

        # ensure x has shape (n, )
        x_shape = x.shape
        x = np.squeeze(x)
        assert x.ndim <= 1

        # ensure x in d1
        valid_lower = (x >= d1[0]) | np.isclose(x, d1[0])
        valid_upper = (x <= d1[1]) | np.isclose(x, d1[1])
        assert np.all(valid_lower), f"Assertion failed: Some values are below lower bounds\n{x[~valid_lower]}"
        assert np.all(valid_upper), f"Assertion failed: Some values are above upper bounds\n{x[~valid_upper]}"

        # scale
        x = (x - d1[0]) / (d1[1] - d1[0])
        x = x * (d2[1] - d2[0]) + d2[0]

        # Return in original shape
        return x.reshape(x_shape)

    def scale_back(self, x: Union[jax.Array, np.ndarray]) -> Union[jax.Array, np.ndarray]:
        """
        Map points from the generator's domain back to the reference domain.

        Mainly intended for internal use and testing.

        Parameters
        ----------
        x : jax.Array or np.ndarray
            Nodes or points in the custom domain.

        Returns
        -------
        jax.Array or np.ndarray
            Nodes or points in the reference domain `[-1, 1]`.
        """
        return self.scale(x, d1=self.__domain, d2=self.__reference_domain)

    def get_random(self, n: int = 1):
        """
        Sample random points uniformly on the domain.

        Parameters
        ----------
        n : int, optional
            Number of random points to sample (default is 1).

        Returns
        -------
        jax.Array or np.ndarray
            Randomly sampled points.
        """
        return self.scale(np.random.uniform(-1, 1, n))

    def get_quadrature_weights(self, n: int) -> Union[jax.Array, np.ndarray]:
        """
        Return quadrature weights for the Leja nodes.

        Parameters
        ----------
        n : int
            Weights corresponding to the first `n+1` nodes.

        Returns
        -------
        jax.Array or np.ndarray
            Quadrature weights.
        """
        return self.__cached_get_quadrature_weights(n)

    def __repr__(self) -> str:
        return f"Leja (domain = {self.__domain})"


class Leja(Generator):
    """
    Container for multiple 1D Leja node generators with potentially custom domains in each dimension.
    """

    def __init__(
        self,
        *,
        domains: list[Union[jax.Array, np.ndarray, Sequence[float]]] = None,
        dim: int = None,
    ):
        """
        Initialize the multidimensional Leja node generator.

        Parameters
        ----------
        domains : list of Union[jax.Array, np.ndarray, Sequence[float]], optional
            List of 1D domains (each as a 2-element sequence) for each dimension.
            If provided, `dim` must be None.
        dim : int, optional
            The number of dimensions. If provided without `domains`, uses `[-1, 1]`
            as the default domain in each dimension.

        Raises
        ------
        ValueError
            If the dimension cannot be inferred from inputs.
        """
        self.__domains = None
        self.__reference_domains = None
        if domains is not None:
            Generator.__init__(self, [Leja1D(domain) for domain in domains])
            self.__domains = np.asarray(domains)
            self.__reference_domains = np.array([[-1, 1]] * len(domains))
        elif dim is not None:
            Generator.__init__(self, [Leja1D()] * dim)
        else:
            raise ValueError("Must specify one of 'domains' or 'dim'.")

    def scale(
        self,
        x: Union[jax.Array, np.ndarray],
        d1: Union[jax.Array, np.ndarray, Sequence[float]] = None,
        d2: Union[jax.Array, np.ndarray, Sequence[float]] = None,
    ) -> Union[jax.Array, np.ndarray]:
        """
        Map nodes or points from interval `d1` to interval `d2` by affine transformation.

        Mainly intended for internal use and testing.

        Parameters
        ----------
        x : array-like
            Points to transform.
        d1 : array-like of shape (2,), optional
            Source interval (default: reference domain `[-1, 1]`).
        d2 : array-like of shape (2,), optional
            Target interval (default: generator's domain).

        Returns
        -------
        jax.Array or np.ndarray
            Nodes or points in the target domain.
        """
        if d1 is None:
            d1 = self.__reference_domains
        if d2 is None:
            d2 = self.__domains

        assert (d1 is None) == (d2 is None)
        if d1 is None:  # no scaling if no custom domains are given
            return x

        # ensure d1, d2 have shape (d, 2)
        d1, d2 = np.asarray(d1), np.asarray(d2)
        assert d1.shape == d2.shape, f"shapes {d1.shape} and {d2.shape} do not match"
        d = 1 if len(d1.shape) == 1 else d1.shape[0]
        if len(d1.shape) == 1:
            d1 = d1.reshape((1, 2))
            d2 = d2.reshape((1, 2))
        for i in range(d):
            assert d1[i, 0] < d1[i, 1]
            assert d2[i, 0] < d2[i, 1]

        # ensure x has shape (n, d)
        x = np.asarray(x)
        x_shape = x.shape
        if x_shape == ():
            x = np.array([[x]])
        else:
            if len(x.shape) == 1:
                if x.shape[0] == d:
                    x = x.reshape((1, len(x)))
                else:
                    x = x.reshape((len(x), 1))

        # ensure x in d1
        valid_lower = (x >= d1[:, 0]) | np.isclose(x, d1[:, 0])
        valid_upper = (x <= d1[:, 1]) | np.isclose(x, d1[:, 1])
        assert np.all(valid_lower), f"Assertion failed: Some values are below lower bounds\n{x[~valid_lower]}"
        assert np.all(valid_upper), f"Assertion failed: Some values are above upper bounds\n{x[~valid_upper]}"

        # check
        assert len(x.shape) == len(d1.shape) == len(d2.shape) == 2
        assert x.shape[1] == d1.shape[0] == d2.shape[0]
        assert d1.shape[1] == d2.shape[1] == 2

        # scale
        x = (x - d1[:, 0]) / (d1[:, 1] - d1[:, 0])
        x = x * (d2[:, 1] - d2[:, 0]) + d2[:, 0]

        # Return in original shape
        return x.reshape(x_shape)

    def scale_back(self, x: Union[jax.Array, np.ndarray]) -> Union[jax.Array, np.ndarray]:
        """
        Map points from the generator's domain back to the reference domain.

        Mainly intended for internal use and testing.

        Parameters
        ----------
        x : jax.Array or np.ndarray
            Nodes or points in the custom domain.

        Returns
        -------
        jax.Array or np.ndarray
            Nodes or points with each componenent mapped to the reference domain `[-1, 1]`.
        """
        return self.scale(x, d1=self.__domains, d2=self.__reference_domains)

    def __repr__(self) -> str:
        if self.__domains is not None:
            return f"Leja (d = {self.dim}, domains = {self.__domains.tolist()})"
        else:
            return f"Leja (d = {self.dim})"
