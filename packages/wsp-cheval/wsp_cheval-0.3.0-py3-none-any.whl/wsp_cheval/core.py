"""Collection of pure-Numba functions for sampling & probability computation"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from numba import boolean as nbool
from numba import float32 as nfloat
from numba import float64 as ndouble
from numba import int64 as nlong
from numba import njit
from numba import optional as maybe
from numba import prange, void
from numba.core.types import Tuple as NTuple
from numpy.typing import NDArray

MIN_RANDOM_VALUE = np.finfo(np.float64).tiny
MAX_RANDOM_VALUE = np.iinfo(np.int32).max

TREE_INFO_TYPE = NTuple((nlong[:], nlong[:], ndouble[:]))


class UtilityBoundsError(ValueError):
    pass


# region Sampling


@njit(nlong(ndouble[:], ndouble), nogil=True, cache=True)
def sample_once(p_array: NDArray, r: float) -> int:
    r = max(r, MIN_RANDOM_VALUE)
    cumsum = 0.0
    index = 0
    for p in p_array:
        cumsum += p
        if r <= cumsum:
            return index
        index += 1
    return len(p_array) - 1


@njit(nlong(ndouble, ndouble[:]), nogil=True, cache=True)
def logarithmic_search(r: float, cps: NDArray) -> int:
    """Logarithmic (binary) search algorithm for finding the greatest index whose cumulative probability is <= the
    random draw.

    Allows for cells with 0 probability.

    Args:
        r (float): The random draw to compare against.
        cps (float[]): The cumulative probabilities to search

    Returns:
        int: The found index.
    """

    # The check below is required to avoid a very specific edge case in which there is more than one 0-probability
    # choice at the start of the probability array, e.g. [0, 0, 0, 0.1, 0.3, 0.7, 1.0]. The randomizer draws on the
    # interval [0, 1), so it's a (very) small possibility, but nonetheless would yield potentially very wrong results
    if r == 0:
        r = MIN_RANDOM_VALUE

    ncols = len(cps)

    lower_bound, upper_bound = 0, ncols - 1
    while (upper_bound - lower_bound) > 1:
        mid_index = np.uint32((upper_bound + lower_bound) // 2)
        cp_at_mid = cps[mid_index]
        if r <= cp_at_mid:  # left branch
            upper_bound = mid_index
        else:  # right branch
            lower_bound = mid_index

    cp_at_left = cps[lower_bound]
    if r <= cp_at_left:
        return lower_bound
    else:
        return upper_bound


@njit(void(ndouble[:]), nogil=True, cache=True)
def nbf_cumsum(array: NDArray):
    accum = 0.0
    length = len(array)
    for i in range(length):
        accum += array[i]
        array[i] = accum


@njit(nlong[:](nlong, nlong), nogil=True, cache=True)
def generate_rand_ints_for_parallel(seed: int, n: int) -> NDArray:
    """Wrap random sampling in a separate function with parallel=False for stable results"""
    np.random.seed(seed)
    return np.random.randint(0, MAX_RANDOM_VALUE, n)


@njit(ndouble[:](nlong, nlong), nogil=True, cache=True)
def generate_rand_floats_for_parallel(seed: int, n: int) -> NDArray:
    """Wrap random sampling in a separate function with parallel=False for stable results"""
    np.random.seed(seed)
    return np.random.uniform(MIN_RANDOM_VALUE, 1, n)


@njit(nlong[:](ndouble[:], nlong, nlong, maybe(nlong[:])), nogil=True, cache=True)
def sample_multi(p_array: NDArray, n: int, random_seed: int, out_array: NDArray = None) -> NDArray:
    """Sample from a probability distribution multiple times using binary search"""
    np.random.seed(random_seed)

    nbf_cumsum(p_array)

    if out_array is None:
        out_array = np.zeros(n, dtype=np.int64)
    else:
        assert len(out_array) == n

    for i in range(n):
        r = np.random.uniform(MIN_RANDOM_VALUE, 1.0, 1)[0]
        out_array[i] = logarithmic_search(r, p_array)
    return out_array


# endregion


# region Probability Computation


@njit(ndouble[:](ndouble[:]), nogil=True, cache=True)
def simple_probabilities(weights: NDArray) -> NDArray:
    return weights / weights.sum()


@njit(
    [
        NTuple((ndouble[:], ndouble, ndouble[:]))(ndouble[:], nbool),
        NTuple((ndouble[:], ndouble, ndouble[:]))(nfloat[:], nbool),
    ],
    nogil=True,
    cache=True,
)
def multinomial_probabilities(utilities: NDArray, check_infeasible: bool) -> Tuple[NDArray, float, NDArray]:
    """Computes probabilities given a multinomial logit model formulation."""
    n_cols = len(utilities)
    p = np.zeros(n_cols, dtype=np.float64)  # Return value
    ls_terms = np.zeros(n_cols, dtype=np.float64)

    total_ls = 0.0  # Logsum
    for i, u in enumerate(utilities):
        expu = np.exp(u)
        total_ls += expu
        p[i] = expu
        ls_terms[i] = expu

    if total_ls <= 0:
        if check_infeasible:
            raise UtilityBoundsError("MNL utilities all exceeded minimum value (Logsum == 0.0)")
        for i in range(n_cols):
            p[i] = 0  # ensure that `p` will return all zeros
    else:
        for i in range(n_cols):
            p[i] = p[i] / total_ls

    return p, total_ls, ls_terms


@njit(
    [
        NTuple((ndouble[:], ndouble, ndouble[:]))(ndouble[:], nlong[:], nlong[:], ndouble[:], nbool[:], nbool, nbool),
        NTuple((ndouble[:], ndouble, ndouble[:]))(nfloat[:], nlong[:], nlong[:], ndouble[:], nbool[:], nbool, nbool),
    ],
    nogil=True,
    cache=True,
)
def nested_probabilities(
    utilities: NDArray,
    hierarchy,
    levels,
    logsum_scales,
    bottom_flags,
    scale_utilities: bool,
    check_infeasible: bool,
) -> Tuple[NDArray, float, NDArray]:
    """Probability evaluation of a nested logit model, without needing a tree structure or any recursion."""

    n_cells = len(utilities)
    probabilities = utilities.astype(np.float64)
    top_logsum = 0
    grouped_logsums = np.zeros(n_cells, dtype=np.float64)
    final_logsums = np.zeros(n_cells, dtype=np.float64)

    # Step 1: Exponentiate the utilities and collect logsums
    max_level = levels.max()
    current_level = max_level
    for _ in range(max_level + 1):
        # Go through levels in reverse order (e.g. starting at the bottom)
        for index, level in enumerate(levels):
            if level != current_level:
                continue  # This is still faster than using np.where()

            parent = hierarchy[index]
            parent_ls_scale = 1.0 if not scale_utilities or parent < 0 else logsum_scales[parent]
            is_bottom = bottom_flags[index]

            if is_bottom:
                # If this node is at the bottom of the tree, no need to lookup the previously-stored logsum
                expu = np.exp(probabilities[index] / parent_ls_scale)
            else:
                existing_logsum = grouped_logsums[index]
                current_ls_scale = logsum_scales[index]

                # Note: It is deliberate to take the log of 0 in some cases. This can occur when all children in a nest
                # exponentiate to 0 (e.g. have very low utility, usually deliberately to disable some choices). The
                # function np.log() evaluates to -inf, which is exactly what we want it to be: the upper choice should
                # also get disabled.
                expu = np.exp((probabilities[index] + current_ls_scale * np.log(existing_logsum)) / parent_ls_scale)

            if parent >= 0:
                grouped_logsums[parent] += expu
            else:
                top_logsum += expu
            probabilities[index] = expu
            final_logsums[index] = expu
        current_level -= 1

    if top_logsum <= 0:
        if check_infeasible:
            raise UtilityBoundsError("Nested logit top-level logsum is 0.0")

    # Step 2: Use logsums to compute conditional probabilities
    for index, parent in enumerate(hierarchy):
        ls = top_logsum if parent == -1 else grouped_logsums[parent]

        # Logsums of 0 can happen sometimes when all choices in a nest are -inf, so just fix the probabilities to 0
        p = 0.0 if ls <= 0 else probabilities[index] / ls
        probabilities[index] = p

    # Step 3: Compute absolute probabilities for child nodes, collecting parent nodes
    for current_level in range(1, max_level + 1):
        for index, level in enumerate(levels):
            if level != current_level:
                continue
            parent = hierarchy[index]
            probabilities[index] *= probabilities[parent]

    # Step 4: Zero-out parent node probabilities
    # This does not use a Set because Numba sets are really slow
    for parent in hierarchy:
        if parent < 0:
            continue
        probabilities[parent] = 0.0

    return probabilities, top_logsum, final_logsums


# endregion


# region Middle functions


@njit(nlong(ndouble[:], ndouble), nogil=True, cache=True)
def simple_sample(weights: NDArray, r: float) -> int:
    """Samples once from an array of weights, from an existing random draw"""
    p_array = simple_probabilities(weights)
    return sample_once(p_array, r)


@njit(nlong[:](ndouble[:], nlong, nlong, maybe(nlong[:])), nogil=True, cache=True)
def simple_multisample(weights: NDArray, n: int, seed: int, out: NDArray = None) -> NDArray:
    """Samples multiple times from an array of weights, based on a random seed. Thread-safe."""
    p_array = simple_probabilities(weights)
    return sample_multi(p_array, n, seed, out)


@njit(
    [NTuple((nlong, ndouble))(ndouble[:], ndouble), NTuple((nlong, ndouble))(nfloat[:], ndouble)],
    nogil=True,
    cache=True,
)
def multinomial_sample(utilities: NDArray, r: float) -> Tuple[int, float]:
    """Samples once from an array of multinomial logit utilities, from an existing random draw"""
    p_array, ls, _ = multinomial_probabilities(utilities, True)  # Check infeasible req'd (for sampling)
    return sample_once(p_array, r), ls


@njit(
    [
        NTuple((nlong[:], ndouble))(ndouble[:], nlong, nlong, maybe(nlong[:])),
        NTuple((nlong[:], ndouble))(nfloat[:], nlong, nlong, maybe(nlong[:])),
    ],
    nogil=True,
    cache=True,
)
def multinomial_multisample(utilities: NDArray, n: int, seed: int, out: NDArray = None) -> Tuple[NDArray, float]:
    """Samples multiple times from an array of multinomial logit utilities, based on a random seed. Thread-safe."""
    p_array, ls, _ = multinomial_probabilities(utilities, True)  # Check infeasible req'd (for sampling)
    return sample_multi(p_array, n, seed, out), ls


@njit(
    [
        NTuple((nlong, ndouble))(ndouble[:], ndouble, nlong[:], nlong[:], ndouble[:], nbool[:], nbool),
        NTuple((nlong, ndouble))(nfloat[:], ndouble, nlong[:], nlong[:], ndouble[:], nbool[:], nbool),
    ],
    nogil=True,
    cache=True,
)
def nested_sample(
    utilities: NDArray, r: float, parents, levels, ls_scales, bottom_flags, scale_utilities: bool
) -> Tuple[int, float]:
    """Samples once from an array of nested logit utilities, from an existing random draw"""
    p_array, ls, _ = nested_probabilities(
        utilities,
        parents,
        levels,
        ls_scales,
        bottom_flags,
        scale_utilities,
        True,  # Check infeasible req'd (for sampling)
    )
    return sample_once(p_array, r), ls


@njit(
    [
        NTuple((nlong[:], ndouble))(
            ndouble[:], nlong[:], nlong[:], ndouble[:], nbool[:], nlong, nlong, nbool, maybe(nlong[:])
        ),
        NTuple((nlong[:], ndouble))(
            nfloat[:], nlong[:], nlong[:], ndouble[:], nbool[:], nlong, nlong, nbool, maybe(nlong[:])
        ),
    ],
    nogil=True,
    cache=True,
)
def nested_multisample(
    utilities: NDArray,
    parents,
    levels,
    ls_scales,
    bottom_flags,
    n: int,
    seed: int,
    scale_utilities: bool,
    out: NDArray = None,
) -> Tuple[NDArray, float]:
    """Samples multiple times from an array of nested logit utilities, based on a random seed. Thread-safe."""
    p_array, ls, _ = nested_probabilities(
        utilities,
        parents,
        levels,
        ls_scales,
        bottom_flags,
        scale_utilities,
        True,  # Check infeasible req'd (for sampling)
    )
    return sample_multi(p_array, n, seed, out), ls


# endregion


# region High level functions


@njit(nlong[:, :](ndouble[:, :], nlong, nlong), parallel=True, nogil=True, cache=True)
def worker_weighted_sample(weights: NDArray, n: int, seed: int) -> NDArray:
    n_rows = weights.shape[0]
    result = np.zeros((n_rows, n), dtype=np.int64)

    np.random.seed(seed)
    if n <= 1:
        r_array = np.random.uniform(MIN_RANDOM_VALUE, 1.0, n_rows)
        for i in prange(n_rows):
            weight_row = weights[i, :]
            r = r_array[i]
            result[i, 0] = simple_sample(weight_row, r)
    else:
        seed_array = np.random.randint(0, MAX_RANDOM_VALUE, n_rows)
        for i in prange(n_rows):
            weight_row = weights[i, :]
            seed_i = seed_array[i]
            _, ls = simple_multisample(weight_row, n, seed_i, result[i, :])
    return result


@njit(
    [
        NTuple((nlong[:, :], ndouble[:]))(ndouble[:, :], nlong, nlong),
        NTuple((nlong[:, :], ndouble[:]))(nfloat[:, :], nlong, nlong),
    ],
    parallel=True,
    nogil=True,
    cache=True,
)
def worker_multinomial_sample(utilities: NDArray, n: int, seed: int) -> Tuple[NDArray, NDArray]:
    """Runs multinomial_sample or multinomial_multisample in parallel."""
    n_rows = utilities.shape[0]
    result = np.zeros((n_rows, n), dtype=np.int64)
    ls_array = np.zeros(n_rows, dtype=np.float64)

    if n <= 1:
        r_array = generate_rand_floats_for_parallel(seed, n_rows)
        for i in prange(n_rows):
            utility_row = utilities[i, :]
            r = r_array[i]
            result[i, 0], ls = multinomial_sample(utility_row, r)
            ls_array[i] = ls
    else:
        seed_array = generate_rand_ints_for_parallel(seed, n_rows)
        for i in prange(n_rows):
            utility_row = utilities[i, :]
            seed_i = seed_array[i]
            _, ls = multinomial_multisample(utility_row, n, seed_i, result[i, :])
            ls_array[i] = ls
    return result, ls_array


@njit(
    [
        NTuple((ndouble[:, :], ndouble[:], ndouble[:, :]))(ndouble[:, :], nbool),
        NTuple((ndouble[:, :], ndouble[:], ndouble[:, :]))(nfloat[:, :], nbool),
    ],
    parallel=True,
    nogil=True,
    cache=True,
)
def worker_multinomial_probabilities(utilities: NDArray, check_infeasible: bool) -> Tuple[NDArray, NDArray, NDArray]:
    """Runs multinomial_probabilities in parallel"""
    n_rows, n_cols = utilities.shape
    result = np.zeros((n_rows, n_cols), dtype=np.float64)
    top_ls_array = np.zeros(n_rows, dtype=np.float64)
    nested_ls_terms = np.zeros((n_rows, n_cols), dtype=np.float64)

    for i in prange(n_rows):
        utility_row = utilities[i, :]
        p_array, top_ls, nested_ls = multinomial_probabilities(utility_row, check_infeasible)
        result[i, :] = p_array
        top_ls_array[i] = top_ls
        nested_ls_terms[i, :] = nested_ls

    return result, top_ls_array, nested_ls_terms


@njit(
    [
        NTuple((nlong[:, :], ndouble[:]))(ndouble[:, :], nlong[:], nlong[:], ndouble[:], nbool[:], nlong, nlong, nbool),
        NTuple((nlong[:, :], ndouble[:]))(nfloat[:, :], nlong[:], nlong[:], ndouble[:], nbool[:], nlong, nlong, nbool),
    ],
    parallel=True,
    nogil=True,
    cache=True,
)
def worker_nested_sample(
    utilities: NDArray,
    parents,
    levels,
    ls_scales,
    bottom_flags,
    n: int,
    seed: int,
    scale_utilities: bool,
) -> Tuple[NDArray, NDArray]:
    """Runs nested_sample or nested_multisample in parallel."""
    n_rows = len(utilities)
    result = np.zeros((n_rows, n), dtype=np.int64)
    ls_array = np.zeros(n_rows, dtype=np.float64)

    if n <= 1:
        r_array = generate_rand_floats_for_parallel(seed, n_rows)
        for i in prange(n_rows):
            utility_row = utilities[i, :]
            r = r_array[i]
            this_result, ls = nested_sample(utility_row, r, parents, levels, ls_scales, bottom_flags, scale_utilities)
            result[i, 0] = this_result
            ls_array[i] = ls
    else:
        seed_array = generate_rand_ints_for_parallel(seed, n_rows)
        for i in prange(n_rows):
            utility_row = utilities[i, :]
            seed_i = seed_array[i]
            _, ls = nested_multisample(
                utility_row, parents, levels, ls_scales, bottom_flags, n, seed_i, scale_utilities, out=result[i, :]
            )
            ls_array[i] = ls
    return result, ls_array


@njit(
    [
        NTuple((ndouble[:, :], ndouble[:], ndouble[:, :]))(
            ndouble[:, :], nlong[:], nlong[:], ndouble[:], nbool[:], nbool, nbool
        ),
        NTuple((ndouble[:, :], ndouble[:], ndouble[:, :]))(
            nfloat[:, :], nlong[:], nlong[:], ndouble[:], nbool[:], nbool, nbool
        ),
    ],
    parallel=True,
    nogil=True,
    cache=True,
)
def worker_nested_probabilities(
    utilities: NDArray,
    parents,
    levels,
    ls_scales,
    bottom_flags,
    scale_utilities: bool,
    check_infeasible: bool,
) -> Tuple[NDArray, NDArray, NDArray]:
    """Runs nested_probabilities in parallel"""
    n_rows, n_cols = utilities.shape
    result = np.zeros((n_rows, n_cols), dtype=np.float64)
    top_ls_array = np.zeros(n_rows, dtype=np.float64)
    nested_ls_terms = np.zeros((n_rows, n_cols), dtype=np.float64)

    for i in prange(n_rows):
        utility_row = utilities[i, :]
        p_array, top_ls, nested_ls = nested_probabilities(
            utility_row, parents, levels, ls_scales, bottom_flags, scale_utilities, check_infeasible
        )
        result[i, :] = p_array
        top_ls_array[i] = top_ls
        nested_ls_terms[i, :] = nested_ls

    return result, top_ls_array, nested_ls_terms


# endregion


# region Misc functions


def fast_indexed_add(out: NDArray, addition: NDArray, row_index: NDArray = None, col_index: NDArray = None):
    """Parallel "a += b" function for large matrices. Also allows "a[:, indexer] += b" for partial tables."""
    rows_a, cols_a = addition.shape
    rows_o, cols_o = out.shape

    if row_index is None:
        assert rows_a == rows_o
    else:
        assert len(row_index) == rows_a
        assert row_index.min() >= 0 and row_index.max() < rows_o

    if col_index is None:
        assert cols_a == cols_o
    else:
        assert len(col_index) == cols_a
        assert col_index.min() >= 0 and col_index.max() < cols_o

    ri_is_none, ci_is_none = row_index is None, col_index is None

    if ri_is_none and ci_is_none:
        _fast_indexed_add_n_n(out, addition)
    elif ri_is_none:
        _fast_indexed_add_n_i(out, addition, col_index)
    elif ci_is_none:
        _fast_indexed_add_i_n(out, addition, row_index)
    else:
        _fast_indexed_add_i_i(out, addition, row_index, col_index)


@njit(parallel=True, cache=True)
def _fast_indexed_add_n_n(out, addition):
    rows_a, cols_a = addition.shape
    for offset in prange(rows_a * cols_a):
        row, col = divmod(offset, cols_a)
        rowi, coli = int(row), int(col)
        out[rowi, coli] += addition[rowi, coli]


@njit(parallel=True, cache=True)
def _fast_indexed_add_n_i(out, addition, col_index):
    rows_a, cols_a = addition.shape
    for offset in prange(0, rows_a * cols_a):
        row, col = divmod(offset, cols_a)
        rowi, coli = int(row), int(col)
        target_col = col_index[coli]
        out[rowi, target_col] += addition[rowi, coli]


@njit(parallel=True, cache=True)
def _fast_indexed_add_i_n(out, addition, row_index):
    rows_a, cols_a = addition.shape
    for offset in prange(rows_a * cols_a):
        row, col = divmod(offset, cols_a)
        rowi, coli = int(row), int(col)
        target_row = row_index[rowi]
        out[target_row, coli] += addition[rowi, coli]


@njit(parallel=True, cache=True)
def _fast_indexed_add_i_i(out, addition, row_index, col_index):
    rows_a, cols_a = addition.shape
    for offset in prange(rows_a * cols_a):
        row, col = divmod(offset, cols_a)
        rowi, coli = int(row), int(col)
        target_row = row_index[rowi]
        target_col = col_index[coli]
        out[target_row, target_col] += addition[rowi, coli]


# endregion
