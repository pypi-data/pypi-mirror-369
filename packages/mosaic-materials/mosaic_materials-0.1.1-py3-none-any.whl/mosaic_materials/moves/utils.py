from ctypes import Array, c_int

import numpy as np
import numpy.typing as npt
from numba import njit


def ids2cids(ids: list[int]) -> Array[c_int]:
    """Convert a list of integers to a ctypes array of c_int."""

    lenids = len(ids)
    cids = (lenids * c_int)()
    for i in range(lenids):
        cids[i] = ids[i]

    return cids


@njit(fastmath=True)
def unit_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalise a 1x3 vector to a unit vector.

    Parameters:
    ----------
    v : np.ndarray
        Input vector of shape (3,).

    Returns:
    -------
    np.ndarray
        Normalized unit vector of shape (3,).
    """
    return vector / np.sqrt(np.sum(np.square(vector)))


@njit(fastmath=True)
def random_vector(rand1: float, rand2: float) -> npt.NDArray[np.floating]:
    """Generate a random unit vector using two random numbers."""

    phi = rand1 * 2 * np.pi
    z = rand2 * 2 - 1

    z2 = z * z
    x = np.sqrt(1 - z2) * np.cos(phi)
    y = np.sqrt(1 - z2) * np.sin(phi)

    return np.array([x, y, z])


@njit
def rodrigues(
    a: npt.NDArray[np.floating], b: npt.NDArray[np.floating], theta: float
) -> npt.NDArray[np.floating]:
    """
    Apply Rodrigues' rotation formula to rotate a vector about another vector.

    Parameters:
    ----------
    a
        The vector to rotate of shape (3,).
    b
        The rotation axis vector of shape (3,). Must be a unit vector.
    theta
        The rotation angle in radians.

    Returns:
    -------
    The rotated vector of shape (3,).
    """

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    term1 = a * cos_theta
    term2 = np.cross(b, a) * sin_theta
    term3 = b * np.dot(b, a) * (1 - cos_theta)

    return term1 + term2 + term3


@njit(fastmath=True)
def _rotate_cluster_inplace(
    pos_old,   # float64[:,3]  wrapped
    img_old,   # int32[:,3]
    L,         # float64[3]
    axis,      # float64[3], unit
    theta,     # float64
    w,         # float64[:]  (masses for COM; ones for centroid)
    pos_new,   # float64[:,3]
    img_new,   # int32[:,3]
) -> None:

    n = pos_old.shape[0]

    # --- weighted centroid in unwrapped coords ---
    wsum = 0.0
    c0 = 0.0
    c1 = 0.0
    c2 = 0.0
    for i in range(n):
        wi = w[i]
        a0 = pos_old[i, 0] + img_old[i, 0] * L[0]
        a1 = pos_old[i, 1] + img_old[i, 1] * L[1]
        a2 = pos_old[i, 2] + img_old[i, 2] * L[2]
        c0 += wi * a0
        c1 += wi * a1
        c2 += wi * a2
        wsum += wi

    invw = 1.0 / wsum
    c0 *= invw
    c1 *= invw
    c2 *= invw

    # --- Rodrigues rotation about centroid ---
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    one_mc = 1.0 - cos_t
    b0, b1, b2 = axis[0], axis[1], axis[2]

    for i in range(n):
        a0 = pos_old[i, 0] + img_old[i, 0] * L[0]
        a1 = pos_old[i, 1] + img_old[i, 1] * L[1]
        a2 = pos_old[i, 2] + img_old[i, 2] * L[2]

        v0 = a0 - c0
        v1 = a1 - c1
        v2 = a2 - c2

        cx = b1 * v2 - b2 * v1
        cy = b2 * v0 - b0 * v2
        cz = b0 * v1 - b1 * v0

        dot = b0 * v0 + b1 * v1 + b2 * v2

        r0 = v0 * cos_t + cx * sin_t + b0 * dot * one_mc
        r1 = v1 * cos_t + cy * sin_t + b1 * dot * one_mc
        r2 = v2 * cos_t + cz * sin_t + b2 * dot * one_mc

        abs0 = r0 + c0
        abs1 = r1 + c1
        abs2 = r2 + c2

        img0 = int(np.floor(abs0 / L[0]))
        img1 = int(np.floor(abs1 / L[1]))
        img2 = int(np.floor(abs2 / L[2]))

        pos_new[i, 0] = abs0 - img0 * L[0]
        pos_new[i, 1] = abs1 - img1 * L[1]
        pos_new[i, 2] = abs2 - img2 * L[2]
        img_new[i, 0] = img0
        img_new[i, 1] = img1
        img_new[i, 2] = img2