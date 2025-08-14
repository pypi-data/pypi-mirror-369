import numpy as np
from numba import njit, int32, int64  # , prange
from numba.typed import Dict  # , List
import math


def log_of_product_of_powers(bases, exponents):
    """
    Compute the complex logarithm of ∏ᵢ bases[i]**exponents[i] for real bases.

    Returns
    -------
    re_log : float
        ∑ᵢ exponents[i] * log|bases[i]|, the real part of the log.
    arg_over_pi : float
        (∑ᵢ exponents[i] * arg(bases[i])) / π, i.e. the logarithm’s
        imaginary part scaled by π, reduced modulo 2.

    Notes
    -----
    - If bases[i] == 0 and exponents[i] > 0, contributes −∞ to re_log.
    - If bases[i] == 0 and exponents[i] < 0, re_log accumulates +∞ (ValueError
      may be preferred if you want to reject 0**negative).
    - For bases[i] < 0, arg(bases[i]) = π so each negative base flips
      sign according to the parity of the exponent.
    """
    re_log = 0.0
    arg_over_pi = 0.0

    for b, p in zip(bases, exponents):
        if b == 0:
            if p != 0:
                re_log += -p * float("inf")
        elif b < 0:
            re_log += p * math.log(-b)
            arg_over_pi += p
        else:
            re_log += p * math.log(b)

    return re_log, (arg_over_pi % 2)


factorial_table = np.array(
    [
        1,
        1,
        2,
        6,
        24,
        120,
        720,
        5040,
        40320,
        362880,
        3628800,
        39916800,
        479001600,
        6227020800,
        87178291200,
        1307674368000,
        20922789888000,
        355687428096000,
        6402373705728000,
        121645100408832000,
        2432902008176640000,
    ],
    dtype="int64",
)

log_factorial_table = np.array(
    [
        0.0,
        0.0,
        0.6931471805599453,
        1.791759469228055,
        3.1780538303479453,
        4.787491742782046,
        6.579251212010101,
        8.525161361065415,
        10.60460290274525,
        12.80182748008147,
        15.104412573075518,
        17.502307845873887,
        19.98721449566189,
        22.552163853123425,
        25.191221182738683,
        27.899271383840894,
        30.671860106080675,
        33.50507345013689,
        36.39544520803305,
        39.339884187199495,
        42.335616460753485,
        45.38013889847691,
        48.47118135183523,
        51.60667556776438,
        54.784729398112326,
        58.003605222980525,
        61.26170176100201,
        64.55753862700634,
        67.88974313718154,
        71.25703896716801,
        74.65823634883017,
        78.09222355331532,
        81.55795945611504,
        85.05446701758153,
        88.5808275421977,
        92.13617560368711,
        95.71969454214322,
        99.33061245478744,
        102.96819861451382,
        106.63176026064347,
    ],
    dtype="float64",
)


@njit
def factorial_lookup(n):
    """
    n! for n<=20
    """
    return factorial_table[n]


@njit
def log_factorial_lookup(n):
    """
    n! for n<=29
    """
    return log_factorial_table[n]


@njit
def factorial(n):
    """ """
    if n < 21:
        return factorial_lookup(n)
    else:
        facn = factorial_lookup(20)
        for _ in range(21, n + 1):
            facn *= _
        return facn


@njit
def log_factorial(n):
    if n < 30:
        return log_factorial_lookup(n)
    result = log_factorial_lookup(29)
    for i in range(30, n + 1):
        result += np.log(i)
    return result


@njit
def integer_power_of_i(power):
    """Compute i^power"""
    power = power % 4
    if power == 0:
        return 1.0 + 0j
    elif power == 1:
        return 0.0 + 1j
    elif power == 2:
        return -1.0 + 0j
    else:  # power == 3
        return 0.0 - 1j


@njit
def Ylm_alt0(l, m, theta, phi):
    """
    factorials make this unstable for large l
    """
    B = (
        1j ** (m + abs(m))
        * np.sqrt((2 * l + 1) * factorial(l + m) * factorial(l - m) + 0.0)
        / (2 ** (abs(m) + 1) * np.sqrt(np.pi))
    )

    val = np.exp(1j * m * phi)
    val_sum = 0.0 * theta + 0j
    for k in range(1 + int((l - abs(m)) / 2)):
        val_sum += (
            (
                (-1) ** k
                * B
                / (
                    4**k
                    * factorial(l - abs(m) - 2 * k)
                    * factorial(k + abs(m))
                    * factorial(k)
                )
            )
            * np.cos(theta) ** (l - abs(m) - 2 * k)
            * np.sin(theta) ** (abs(m) + 2 * k)
        )
    return val * val_sum


@njit
def Ylm_alt1(l, m, theta, phi):
    """
    no safeguards for sin/cos of theta/phi
    Spherical harmonic Ylm(l, m) at angles theta, phi. Works for arrays of angles.

    Args:
        l (int): 0,1,2,...
        m (int): -l,...,l
        theta (float): polar angle in radians
        phi (float): azimuthal angle in radians

    Returns:
        complex: value of spherical harmonic Ylm at angles theta, phi
    """
    abs_m = abs(m)
    exp_itheta = np.exp(1j * theta)
    cos_theta = exp_itheta.real
    sin_theta = exp_itheta.imag
    cos_theta_sqr = cos_theta * cos_theta
    sin_theta_sqr = sin_theta * sin_theta
    q1 = cos_theta ** (l - abs_m) * sin_theta ** (abs_m)
    log_q2 = (
        0.5 * log_factorial(l + abs_m)
        - 0.5 * log_factorial(l - abs_m)
        - log_factorial(abs_m)
    )
    val = q1 * np.exp(log_q2)
    for k in range(1, 1 + int((l - abs_m) / 2)):
        q1 *= -sin_theta_sqr / (4 * cos_theta_sqr)
        log_q2 += (
            np.log(l - abs_m - 2 * k + 2)
            + np.log(l - abs_m - 2 * k + 1)
            - np.log(k + abs_m)
            - np.log(k)
        )
        val += q1 * np.exp(log_q2)
    return (
        val
        * np.exp(1j * m * phi)
        * (
            integer_power_of_i(m + abs_m)
            * np.sqrt((2 * l + 1))
            / (2 ** (abs_m + 1) * np.sqrt(np.pi))
        )
    )


@njit("f8(i8, i8, f8)")
def phi_independent_problem_angle_small_scalarYlm(l, m, theta):
    """
    phi independent part of spherical harmonic Ylm(l, m).
    works for small/zero cos(theta) or sin(theta)

    Args:
        l (int): 0,1,2,...
        m (int): -l,...,l
        theta (float): polar angle in radians [0, pi]

    Returns:
        real: value of Ylm(l, m, theta, phi)/exp(1j*m*phi)
    """

    abs_m = abs(m)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    rlm = 1 / (2 * np.sqrt(np.pi))
    if m > 0:
        if m % 2 == 1:
            rlm *= -1
    log_qk = (
        0.5 * np.log(2 * l + 1)
        + 0.5 * log_factorial(l + abs_m)
        - abs_m * np.log(2)
        - 0.5 * log_factorial(l - abs_m)
        - log_factorial(abs_m)
    )
    trig_term = cos_theta ** (l - abs_m) * sin_theta**abs_m
    sk = 1
    sum_Qk = sk * np.exp(log_qk) * trig_term
    minus_log4 = np.log(0.25)
    for k in range(1, 1 + int((l - abs_m) / 2)):
        sk *= -1
        log_qk += (
            minus_log4
            + np.log(l - abs_m - 2 * k + 2)
            + np.log(l - abs_m - 2 * k + 1)
            - np.log(abs_m + k)
            - np.log(k)
        )
        trig_term = cos_theta ** (l - abs_m - 2 * k) * sin_theta ** (abs_m + 2 * k)
        sum_Qk += sk * np.exp(log_qk) * trig_term
    return rlm * sum_Qk


@njit("f8(i8, i8, f8)")
def phi_independent_problem_angle_same_scalarYlm(l, m, theta):
    """
    phi independent part of spherical harmonic Ylm(l, m).
    works for cos(theta)~sin(theta) or cos(theta)=sin(theta)

    Args:
        l (int): 0,1,2,...
        m (int): -l,...,l
        theta (float): polar angle in radians [0, pi]

    Returns:
        real: value of Ylm(l, m, theta, phi)/exp(1j*m*phi)
    """
    # # assumes theta = pi/4 or 3*pi/4 exactly
    # cos_theta = np.cos(theta)
    # tan_theta = np.tan(theta)
    # abs_m = abs(m)
    # rlm = np.sign(cos_theta**l * tan_theta**abs_m) / (2 * np.sqrt(np.pi))
    # if m > 0:
    #     if m % 2 == 1:
    #         rlm *= -1
    # log_qk = (
    #     0.5 * np.log(2 * l + 1)
    #     + 0.5 * log_factorial(l + abs_m)
    #     - 0.5 * l * np.log(2.0)
    #     - abs_m * np.log(2)
    #     - 0.5 * log_factorial(l - abs_m)
    #     - log_factorial(abs_m)
    # )
    # sk = 1
    # sum_Qk = sk * np.exp(log_qk)
    # minus_log4 = np.log(0.25)
    # for k in range(1, 1 + int((l - abs_m) / 2)):
    #     sk *= -1
    #     log_qk += (
    #         minus_log4
    #         + np.log(l - abs_m - 2 * k + 2)
    #         + np.log(l - abs_m - 2 * k + 1)
    #         - np.log(abs_m + k)
    #         - np.log(k)
    #     )
    #     sum_Qk += sk * np.exp(log_qk)
    # return rlm * sum_Qk
    #
    #
    #
    cos_theta = np.cos(theta)
    tan_theta = np.tan(theta)
    abs_cos_theta = abs(cos_theta)
    abs_tan_theta = abs(tan_theta)
    log_abs_cos_theta = np.log(abs_cos_theta)
    log_abs_tan_theta = np.log(abs_tan_theta)
    abs_m = abs(m)
    rlm = np.sign(cos_theta**l * tan_theta**abs_m) / (2 * np.sqrt(np.pi))
    if m > 0:
        if m % 2 == 1:
            rlm *= -1
    log_qk = (
        0.5 * np.log(2 * l + 1)
        + 0.5 * log_factorial(l + abs_m)
        + l * log_abs_cos_theta
        + abs_m * log_abs_tan_theta
        - abs_m * np.log(2)
        - 0.5 * log_factorial(l - abs_m)
        - log_factorial(abs_m)
    )
    sk = 1
    sum_Qk = sk * np.exp(log_qk)
    minus_log4 = np.log(0.25)
    for k in range(1, 1 + int((l - abs_m) / 2)):
        sk *= -1
        log_qk += (
            2 * log_abs_tan_theta
            + minus_log4
            + np.log(l - abs_m - 2 * k + 2)
            + np.log(l - abs_m - 2 * k + 1)
            - np.log(abs_m + k)
            - np.log(k)
        )
        sum_Qk += sk * np.exp(log_qk)
    return rlm * sum_Qk


@njit("f8(i8, i8, f8)")
def phi_independent_scalarYlm(l, m, theta):
    """
    phi independent part of spherical harmonic Ylm(l, m)
    Args:
        l (int): 0,1,2,...
        m (int): -l,...,l
        theta (float): polar angle in radians [0, pi]

    Returns:
        real: value of Ylm(l, m, theta, phi)/exp(1j*m*phi)
    """
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    abs_cos_theta = abs(cos_theta)
    abs_sin_theta = abs(sin_theta)
    epsilon = 1e-8
    if abs_cos_theta < epsilon:
        return phi_independent_problem_angle_small_scalarYlm(l, m, theta)
    if abs_sin_theta < epsilon:
        return phi_independent_problem_angle_small_scalarYlm(l, m, theta)
    if abs(abs_cos_theta - abs_sin_theta) < epsilon:
        return phi_independent_problem_angle_same_scalarYlm(l, m, theta)
    log_abs_cos_theta = np.log(abs_cos_theta)
    log_abs_sin_theta = np.log(abs_sin_theta)
    abs_m = abs(m)
    rlm = np.sign(cos_theta ** (l - abs_m) * sin_theta**abs_m) / (2 * np.sqrt(np.pi))
    if m > 0:
        if m % 2 == 1:
            rlm *= -1
    # ep, en, op, on
    # +, +, -, +
    #
    #
    #
    # if m % 2 == 1:
    #     rlm *= -1
    # ep,en,op,on
    # +, +, -, -
    #
    #
    #
    #
    #
    # if m < 0:
    #     if m % 2 == 1:
    #         rlm *= -1
    # ep,en,op,on
    # +, +, +, -
    #
    #
    #
    #
    log_qk = (
        0.5 * np.log(2 * l + 1)
        + 0.5 * log_factorial(l + abs_m)
        + (l - abs_m) * log_abs_cos_theta
        + abs_m * log_abs_sin_theta
        - abs_m * np.log(2)
        - 0.5 * log_factorial(l - abs_m)
        - log_factorial(abs_m)
    )
    sk = 1
    sum_Qk = sk * np.exp(log_qk)
    minus_log4 = np.log(0.25)
    for k in range(1, 1 + int((l - abs_m) / 2)):
        sk *= -1
        log_qk += (
            -2 * log_abs_cos_theta
            + 2 * log_abs_sin_theta
            + minus_log4
            + np.log(l - abs_m - 2 * k + 2)
            + np.log(l - abs_m - 2 * k + 1)
            - np.log(abs_m + k)
            - np.log(k)
        )
        sum_Qk += sk * np.exp(log_qk)
    return rlm * sum_Qk


@njit("c16(i8, i8, f8, f8)")
def scalarYlm(l, m, theta, phi):
    """
    Spherical harmonic Ylm(l, m)
    Args:
        l (int): 0,1,2,...
        m (int): -l,...,l
        theta (float): polar angle in radians
        phi (float): polar angle in radians

    Returns:
        complex: value of Ylm(l, m, theta, phi)
    """
    return np.exp(1j * m * phi) * phi_independent_scalarYlm(l, m, theta)


@njit("c16[:](i8, i8, f8[:], f8[:])")
def Ylm(l, m, theta, phi):
    """
    Vectorized spherical harmonic Ylm(l, m)

    Args:
        l (int): 0,1,2,...
        m (int): -l,...,l
        theta (array): polar angle in radians
        phi (array): azimuthal angle in radians


    Returns:
        array: values of spherical harmonic Ylm at angles theta, phi
    """
    Ns = len(theta)
    Y = np.zeros(Ns)
    for s in range(Ns):
        Y[s] = phi_independent_scalarYlm(l, m, theta[s])
    return np.exp(1j * m * phi) * Y


@njit("f8[:](i8, i8, f8[:], f8[:])")
def real_Ylm(l, m, theta, phi):
    """
    Real form of spherical harmonic.
    """
    abs_m = abs(m)
    Ns = len(theta)
    Y = np.zeros(Ns)
    for s in range(Ns):
        Y[s] = phi_independent_scalarYlm(l, abs_m, theta[s])
    if m < 0:
        return np.sqrt(2) * (-1) ** abs_m * np.sin(abs_m * phi) * Y
    elif m == 0:
        return Y
    else:  # m >0
        return np.sqrt(2) * (-1) ** abs_m * np.cos(abs_m * phi) * Y


def test_Ylm_against_scipy():
    from scipy.special import sph_harm_y

    Ylm_fun = Ylm  # up to l=54
    # Ylm_fun = Ylm_alt0  # up to l=10
    # Ylm_fun = Ylm_alt1  # up to l=19

    def n_LM(l, m):
        return m + l**2 + l

    def lm_N(n):
        l = int(np.sqrt(n))
        m = n - (l**2 + l)
        return l, m

    local_tol = 1e-8
    l_min = 0
    l_max = 200
    Theta = np.pi * np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    Phi = np.pi * np.array([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0])
    Theta = np.array([*Theta, *np.linspace(0, np.pi, 11)[1:-1]])
    Phi = np.array([*Phi, *np.linspace(2 * np.pi, 22)[1:]])

    ThetaPhi = np.array([[t, p] for t in Theta for p in Phi])
    n_max = n_LM(l_max, l_max)
    n_min = n_LM(l_min, -l_min)
    deltainf = np.zeros(n_max + 1 - n_min)
    LM = np.zeros((n_max + 1 - n_min, 2), dtype=np.int64)
    print(20 * "_")
    l_good = -99999
    m_good = -99999
    for n in range(n_min, n_max + 1):
        _n = n - n_min
        l, m = lm_N(n)
        LM[_n] = l, m
        print(f"testing l={l}, m={m}        ", end="\r")
        Y = Ylm_fun(l, m, *ThetaPhi.T)
        sciY = sph_harm_y(l, m, *ThetaPhi.T)
        dY = np.abs((Y - sciY))
        deltainf[_n] = np.linalg.norm(dY, np.inf)
        if deltainf[_n] > local_tol:
            print(f"\nmax error={deltainf[_n]}")
            badThetaPhi = ThetaPhi[np.where(dY > local_tol)] / np.pi
            print("over tolerance at angles (theta, phi):")
            print(badThetaPhi)
            break
        else:
            l_good = l
            m_good = m

    print(
        f"\ngood up to l={l_good}, m={m_good} (first {n_LM(l_good, m_good)+1} spherical harmonics)"
    )
    # LMbad = LM[np.where(deltainf > local_tol)]
    # return (deltainf, LMbad)


def build_sh_module():
    from numba.pycc import CC

    @njit
    def jit_n_LM(l, m):
        """
        Enumeration of spherical harmonic indices.

        (0, 0) -> 0
        (1, -1) -> 1
        (1, 0) -> 2
        (1, 1) -> 3
        (2, -2) -> 4
        .
        .
        .
        """
        return m + l**2 + l

    @njit
    def jit_lm_N(n):
        """
        get (l, m) spherical harmonic indices from n

        0 -> (0, 0)
        1 -> (1, -1)
        2 -> (1, 0)
        3 -> (1, 1)
        4 -> (2, -2)
        .
        .
        .
        """
        l = int(np.sqrt(n))
        m = n - (l**2 + l)
        return l, m

    cc = CC("spherical_harmonics")
    cc.output_dir = "./build/pybrane"
    cc.verbose = True

    @cc.export("n_LM", "i8(i8, i8)")
    def n_LM(l, m):
        return m + l**2 + l

    @cc.export("lm_N", "i8[:](i8)")
    def lm_N(n):
        lm = np.zeros(2, dtype=np.int64)
        lm[0] = int(np.sqrt(n))
        lm[1] = n - (lm[0] ** 2 + lm[0])
        return lm

    @cc.export("Ylm", "c16[:](i8, i8, f8[:], f8[:])")
    def _Ylm(l, m, theta, phi):
        return Ylm(l, m, theta, phi)

    @cc.export("real_Ylm", "f8[:](i8, i8, f8[:], f8[:])")
    def _real_Ylm(l, m, theta, phi):
        return real_Ylm(l, m, theta, phi)

    cc.compile()


# ##################################################
# ##################################################
# ##################################################
# ##################################################
# ##################################################


@njit
def jitnorm(V, axis=-1):
    return np.sqrt(np.sum(V**2, axis=axis))


@njit
def fib_disc(Npoints=100):
    xy = np.zeros((Npoints, 2))
    ga = np.pi * (3.0 - np.sqrt(5.0))  # golden angle

    for i in range(Npoints):
        rad = np.sqrt(i / (Npoints - 1))  # radius at z

        theta = ga * i  # angle increment
        x = rad * np.cos(theta)
        y = rad * np.sin(theta)

        xy[i] = np.array([x, y])

    return xy


@njit
def fib_sphere(Npoints=100):
    xyz = np.zeros((Npoints, 3))
    ga = np.pi * (3.0 - np.sqrt(5.0))  # golden angle

    for i in range(Npoints):
        z = 1.0 - 2 * i / (Npoints - 1)  # -1<=z<=1
        rad = np.sqrt(1.0 - z**2)  # radius at z

        theta = ga * i  # angle increment

        x = rad * np.cos(theta)
        y = rad * np.sin(theta)

        xyz[i] = np.array([x, y, z])

    return xyz


# @njit
def uniform_sphere(Npoints=100):
    V = np.random.randn(3, Npoints)
    V /= jitnorm(V, axis=0)
    return V.T


@njit
def jit_get_halfedge_index_of_twin(H, h):
    """
    Find the half-edge twin to h in the list of half-edges H.

    Parameters
    ----------
    H : list
        List of half-edges [[v0, v1], ...]
    h : int
        Index of half-edge in H

    Returns
    -------
    h_twin : int
        Index of H[h_twin]=[v1,v0] in H, where H[h]=[v0,v1]. Returns -1 if twin not found.
    """
    Nhedges = len(H)
    v0 = H[h][0]
    v1 = H[h][1]
    for h_twin in range(Nhedges):
        if H[h_twin][0] == v1 and H[h_twin][1] == v0:
            return h_twin

    return -1


@njit(parallel=True)
def jit_vf_samples_to_he_samples(V, F):
    # (V, F) = source_samples
    Nfaces = len(F)
    Nvertices = len(V)

    H = []
    h_out_V = Nvertices * [-1]
    v_origin_H = []
    h_next_H = []
    f_left_H = []
    h_bound_F = np.zeros(Nfaces, dtype=np.int32)

    # h = 0
    for f in range(Nfaces):
        h_bound_F[f] = 3 * f
        for i in range(3):
            h = 3 * f + i
            h_next = 3 * f + (i + 1) % 3
            v0 = F[f][i]
            v1 = F[f][(i + 1) % 3]
            H.append([v0, v1])
            v_origin_H.append(v0)
            f_left_H.append(f)
            h_next_H.append(h_next)
            if h_out_V[v0] == -1:
                h_out_V[v0] = h
    need_twins = set([_ for _ in range(len(H))])
    need_next = set()
    h_twin_H = len(H) * [-2]  # -2 means not set
    while need_twins:
        h = need_twins.pop()
        if h_twin_H[h] == -2:  # if twin not set
            h_twin = jit_get_halfedge_index_of_twin(
                H, h
            )  # returns -1 if twin not found
            if h_twin == -1:  # if twin not found
                h_twin = len(H)
                v0, v1 = H[h]
                H.append([v1, v0])
                v_origin_H.append(v1)
                need_next.add(h_twin)
                h_twin_H[h] = h_twin
                h_twin_H.append(h)
                f_left_H.append(-1)
            else:
                h_twin_H[h], h_twin_H[h_twin] = h_twin, h
                need_twins.remove(h_twin)

    h_next_H.extend([-1] * len(need_next))
    while need_next:
        h = need_next.pop()
        h_next = h_twin_H[h]
        # rotate ccw around origin of twin until we find nex h on boundary
        while f_left_H[h_next] != -1:
            h_next = h_twin_H[h_next_H[h_next_H[h_next]]]
        h_next_H[h] = h_next

    # find and enumerate boundaries -1,-2,...
    H_need2visit = set([h for h in range(len(H)) if f_left_H[h] < 0])
    bdry_count = 0
    while H_need2visit:
        bdry_count += 1
        h_start = H_need2visit.pop()
        f_left_H[h_start] = -bdry_count
        h = h_next_H[h_start]
        while h != h_start:
            H_need2visit.remove(h)
            f_left_H[h] = -bdry_count
            h = h_next_H[h]

    target_samples = (
        V,
        h_out_V,
        v_origin_H,
        h_next_H,
        h_twin_H,
        f_left_H,
        h_bound_F,
    )
    return target_samples


@njit
def vertex_pair_key(v0, v1):
    return min(v0, v1) * 1000000 + max(v0, v1)


@njit
def jit_refine_icososphere(Vm1, Fm1, r):
    # Nfaces = len(Fm1)
    # F = np.zeros((4*Nfaces, 3), dtype=np.int32)
    F = []
    V = [xyz for xyz in Vm1]
    v_midpt_vv = Dict.empty(key_type=int64, value_type=int32)
    for tri in Fm1:
        v0, v1, v2 = tri
        key01 = vertex_pair_key(v0, v1)
        key12 = vertex_pair_key(v1, v2)
        key20 = vertex_pair_key(v2, v0)
        v01 = v_midpt_vv.get(key01, int32(-1))
        v12 = v_midpt_vv.get(key12, int32(-1))
        v20 = v_midpt_vv.get(key20, int32(-1))
        if v01 == int32(-1):
            v01 = int32(len(V))
            xyz01 = (V[v0] + V[v1]) / 2
            xyz01 *= r / np.linalg.norm(xyz01)
            V.append(xyz01)
            v_midpt_vv[key01] = v01
        if v12 == int32(-1):
            v12 = int32(len(V))
            xyz12 = (V[v1] + V[v2]) / 2
            xyz12 *= r / np.linalg.norm(xyz12)
            V.append(xyz12)
            v_midpt_vv[key12] = v12
        if v20 == int32(-1):
            v20 = int32(len(V))
            xyz20 = (V[v2] + V[v0]) / 2
            xyz20 *= r / np.linalg.norm(xyz20)
            V.append(xyz20)
            v_midpt_vv[key20] = v20
        F.append([v0, v01, v20])
        F.append([v01, v1, v12])
        F.append([v20, v12, v2])
        F.append([v01, v12, v20])

    Nv = len(V)
    Nf = len(F)
    xyz_coord_V = np.zeros((Nv, 3), dtype=np.float64)
    V_cycle_F = np.zeros((Nf, 3), dtype=np.int32)
    for v in range(Nv):
        xyz_coord_V[v] = V[v]
    for f in range(Nf):
        V_cycle_F[f] = F[f]
    return xyz_coord_V, V_cycle_F


@njit
def vf_orientation_correct(a, b, c, cm):
    abc = (a + b + c) / 3
    n = np.cross(a, b) + np.cross(b, c) + np.cross(c, a)
    return np.dot(n, abc - cm) > 0


@njit
def check_vf_list_orientation(V, F0):
    cm = np.sum(V, axis=0) / len(V)
    F = np.zeros_like(F0)
    for f in range(len(F0)):
        i, j, k = F0[f]
        a, b, c = V[i], V[j], V[k]

        if vf_orientation_correct(a, b, c, cm):
            F[f, :] = np.array([i, j, k])
        else:
            F[f, :] = np.array([i, k, j])
    return F
