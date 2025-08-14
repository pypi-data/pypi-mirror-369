#pragma once

/**
 * @file funs.hpp
 * @brief Numerical functions
 */

#include "mathutils/log_factorial_lookup_table.hpp"
#include "mathutils/simple_generator.hpp"
#include "mathutils/spherical_harmonics_index_lookup_table.hpp"
#include <Eigen/Dense>
#include <array>
#include <cmath>
#include <complex>
#include <coroutine>
#include <cstdint>
#include <stdexcept>

/////////////////////////////////////
/////////////////////////////////////
// Simple non-vectorized functions //
/////////////////////////////////////
/////////////////////////////////////
namespace mathutils {
/**
 * @brief Compute the sign (1,-1, or 0) of a value.
 *
 * @tparam T The type of the input value (must be comparable to T{0}).
 * @param x The input value.
 * @return The sign of the input value.
 */
template <typename T> inline int sign(T x) { return (x > T{0}) - (x < T{0}); }

/**
 * @brief Convert Cartesian coordinates (x, y, z) to spherical coordinates (r,
 * theta, phi).
 *
 * @param xyz The input Cartesian coordinates [...(x,y,z)...] (N, 3)
 * @return The spherical coordinates [...(r, theta, phi)...] (N, 3)
 */
inline Eigen::MatrixXd rthetaphi_from_xyz(const Eigen::MatrixXd &xyz) {
  if (xyz.cols() != 3) {
    throw std::invalid_argument("xyz must have 3 columns");
  }
  int num_points = xyz.rows();
  Eigen::MatrixXd rthetaphi(num_points, 3);
  rthetaphi.setZero();
  for (int i = 0; i < num_points; ++i) {
    double x = xyz(i, 0);
    double y = xyz(i, 1);
    double z = xyz(i, 2);
    double r = std::sqrt(x * x + y * y + z * z);
    double rho = std::sqrt(x * x + y * y);
    double theta = std::atan2(rho, z);
    double phi = std::atan2(y, x);
    rthetaphi(i, 0) = r;
    rthetaphi(i, 1) = theta;
    rthetaphi(i, 2) = phi;
  }
  return rthetaphi;
}

/**
 * @brief Convert spherical coordinates (r, theta, phi) to Cartesian coordinates
 * (x, y, z).
 *
 * @param rthetaphi The input spherical coordinates [...(r, theta, phi)...] (N,
 * 3)
 * @return The Cartesian coordinates [...(x, y, z)...] (N, 3)
 */
inline Eigen::MatrixXd xyz_from_rthetaphi(const Eigen::MatrixXd &rthetaphi) {
  if (rthetaphi.cols() != 3) {
    throw std::invalid_argument("rthetaphi must have 3 columns");
  }
  int num_points = rthetaphi.rows();
  Eigen::MatrixXd xyz(num_points, 3);
  xyz.setZero();
  for (int i = 0; i < num_points; ++i) {
    double r = rthetaphi(i, 0);
    double theta = rthetaphi(i, 1);
    double phi = rthetaphi(i, 2);
    xyz(i, 0) = r * std::sin(theta) * std::cos(phi);
    xyz(i, 1) = r * std::sin(theta) * std::sin(phi);
    xyz(i, 2) = r * std::cos(theta);
  }
  return xyz;
}

/**
 * @brief Convert Cartesian coordinates (x, y, z) to unit sphere coordinates
 * (theta, phi) by projecting onto the unit sphere.
 *
 * @param xyz The input Cartesian coordinates [...(x,y,z)...] (N, 3)
 * @return The spherical coordinates [...(theta, phi)...] (N, 2)
 */
inline Eigen::MatrixXd thetaphi_from_xyz(const Eigen::MatrixXd &xyz) {
  if (xyz.cols() != 3) {
    throw std::invalid_argument("xyz must have 3 columns");
  }
  int num_points = xyz.rows();
  Eigen::MatrixXd thetaphi(num_points, 2);
  thetaphi.setZero();
  for (int i = 0; i < num_points; ++i) {
    double x = xyz(i, 0);
    double y = xyz(i, 1);
    double z = xyz(i, 2);
    double rho = std::sqrt(x * x + y * y);
    double theta = std::atan2(rho, z);
    double phi = std::atan2(y, x);
    thetaphi(i, 0) = theta;
    thetaphi(i, 1) = phi;
  }
  return thetaphi;
}
} // namespace mathutils
/////////////////////////////////////
/////////////////////////////////////
/////////////////////////////////////
/////////////////////////////////////
/////////////////////////////////////

/////////////////////////////////////
/////////////////////////////////////
// Special functions ////////////////
/////////////////////////////////////
/////////////////////////////////////
namespace mathutils {
namespace special {

/**
 * @brief Compute \f$(-1)^n\f$ for integer n.
 */
inline int minus_one_to_int_pow(int n) {
  // Returns -1 if n is odd, 1 if n is even
  return 1 - 2 * (n & 1);
}

/**
 * @brief Compute \f$\ln(n!)\f$ for a non-negative integer n.
 * Uses a lookup table for small values and lgamma for larger values.
 *
 * @param n The non-negative integer for which to compute log(n!).
 * @return The logarithm of the factorial of n.
 */
inline double log_factorial(uint64_t n) {
  return (n < LOG_FACTORIAL_LOOKUP_TABLE_SIZE)
             ? LOG_FACTORIAL_LOOKUP_TABLE[n]
             : std::lgamma(static_cast<double>(n + 1)); // lgamma(n+1) = log(n!)
}

/**
 * @brief The Heaviside step function. Returns 0.0 for negative values, 1.0 for
 * positive values, and 0.5 for zero.
 *
 * @tparam T The type of the input value (must be comparable to T{0}).
 * @param x The input value.
 * @return The Heaviside step function value.
 */
template <typename T> inline double Heaviside(T x) {
  return 0.5 + 0.5 * ((x > T{0}) - (x < T{0}));
}

/**
 * @brief Compute the real part of the complex logarithm \f$Re(Log(x))=
 * ln(|x|)\f$. Returns \f$Re(Log(0))=-\infty\f$ for \f$x=0\f$.
 *
 * \f[\mathbb{C}\rightarrow \mathbb{R}\cup\lbrace-\infty\rbrace\\
 * x\mapsto Re(Log(x))
 * \f]
 *
 * @param x The input value (can be floating-point or integral).
 * @return The logarithm of the input value.
 */
template <typename T> inline double ReLog(const T &x) {
  return (x == T{0}) ? -std::numeric_limits<double>::infinity()
                     : std::log(std::abs(x));
}

/**
 * @brief Compute \f$Re(Log(Re(x)))\f$ and \f$Im(Log(Re(x)))/\pi\f$
 *
 * @param x The input value (can be floating-point or integral).
 * @return std::pair<double, int> {re_log, arg_over_pi}
 */
template <typename T>
inline std::pair<double, int> ReLogRe_ImLogRe_over_pi(const T &x) {
  if constexpr (std::is_floating_point_v<T> || std::is_integral_v<T>) {
    // return (x == T{0}) ? {-std::numeric_limits<double>::infinity(), 0}
    //                    : {std::log(std::abs(x)), static_cast<int>(x < T{0})};
    return (x == T{0})
               ? std::make_pair(-std::numeric_limits<double>::infinity(), 0)
               : std::make_pair(std::log(std::abs(x)),
                                static_cast<int>(x < T{0}));
  } else {
    double Re_x = static_cast<double>(x);
    // return (Re_x == 0.0)
    //            ? {-std::numeric_limits<double>::infinity(), 0}
    //            : {std::log(std::abs(Re_x)), static_cast<int>(Re_x < 0.0)};
    return (Re_x == 0.0)
               ? std::make_pair(-std::numeric_limits<double>::infinity(), 0)
               : std::make_pair(std::log(std::abs(Re_x)),
                                static_cast<int>(Re_x < 0.0));
  }
}

template <typename T>
inline std::pair<double, int> ReLogRe_ImLogRe_over_pi_of_x_to_pow(const T &x,
                                                                  int n) {
  if constexpr (std::is_floating_point_v<T> || std::is_integral_v<T>) {
    return (n == 0) ? std::make_pair(0.0, 0)
           : (x == T{0})
               ? std::make_pair(-n * std::numeric_limits<double>::infinity(), 0)
               : std::make_pair(n * std::log(std::abs(x)),
                                static_cast<int>(x < T{0} && (n & 1)));
  } else {
    double Re_x = static_cast<double>(x);
    return (n == 0) ? std::make_pair(0.0, 0)
           : (Re_x == 0.0)
               ? std::make_pair(-n * std::numeric_limits<double>::infinity(), 0)
               : std::make_pair(n * std::log(std::abs(Re_x)),
                                static_cast<int>(Re_x < 0.0 && (n & 1)));
  }
}

/////////////////////////
// Spherical harmonics //
/////////////////////////

/**
 * @brief Compute the index of (l,m) in [(0,0), (1,-1), (1,0), (1,1), (2,-2),
 * ...]
 *
 * @param l The degree (non-negative).
 * @param m The order (must be in the range [-l, l]).
 * @return int The spherical harmonic index.
 */
inline int spherical_harmonic_index_n_LM(int l, int m) {
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  return l * (l + 1) + m;
}

/**
 * @brief Compute the n-th element of the sequence [(0,0), (1,-1), (1,0), (1,1),
 * (2,-2),
 * ...]
 *
 * @param n The linear index (must be non-negative).
 * @return std::array<int, 2> The (l,m) pair.
 */
inline std::array<int, 2> spherical_harmonic_index_lm_N(int n) {
  if (n < 0) {
    throw std::out_of_range("n must be non-negative");
  }
  if (n > SPHERICAL_HARMONIC_INDEX_N_MAX) {
    int l = static_cast<int>(std::floor(std::sqrt(n)));
    return {l, n - l * (l + 1)};
  }
  return {SPHERICAL_HARMONIC_INDEX_LM_N_LOOKUP_TABLE[n][0],
          SPHERICAL_HARMONIC_INDEX_LM_N_LOOKUP_TABLE[n][1]};
}

/**
 * @brief Compute the associated Legendre polynomial with spherical harmonics
 * normalization \f$P_{m m}(\theta) = e^{-im\phi}Y_{m m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi/2\f$ and \f$m\geq 0\f$. Used to initialize the
 * recursion. Does not check the validity of \f$m\f$ or \f$\theta\f$.
 * @param m Degree/order of the polynomial (\f$m=0,1,\ldots\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi/2\f$).
 * @return double Value of the associated normalized Legendre polynomial.
 */
inline double reduced_spherical_Pmm(int m, double theta) {
  // if (theta == 0.0) {
  //   if (m == 0) {
  //     return 1.0 / std::sqrt(4 * M_PI);
  //   }
  //   return 0.0;
  // }
  // double sigma = (1 - 2 * (m & 1)); // this is just std::pow(-1, m);
  // return sigma * std::exp(m * std::log(std::sin(theta)) -
  //                         0.5 * std::log(4 * M_PI) - m * std::log(2) +
  //                         0.5 * std::lgamma(2 * m + 2) - std::lgamma(m + 1));
  return (theta == 0.0)
             ? (m == 0) / std::sqrt(4 * M_PI)
             : (1 - 2 * (m & 1)) *
                   std::exp(m * std::log(std::sin(theta)) -
                            0.5 * std::log(4 * M_PI) - m * std::log(2) +
                            0.5 * std::lgamma(2 * m + 2) - std::lgamma(m + 1));
}

/**
 * @brief Generate a sequence of associated Legendre polynomials with spherical
 * harmonics normalization \f$P_{\ell m}(\theta) = e^{-im\phi}Y_{\ell m}(\theta,
 * \phi)\f$ for fixed order \f$m=\ell_{start}\f$ and degree \f$\ell =
 * \ell_{start}, \ell_{start} + 1, \ldots, \ell_{end}\f$. Does not check the
 * validity of \f$\theta\f$.
 *
 * @param l_start Starting value \f$\ell\f$. Equivalent
 * @param l_end Final value of \f$\ell\f$.
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi/2\f$).
 */
mathutils::SimpleGenerator<double>
generate_reduced_spherical_Plm_recursion_three_term_upward_ell(int l_start,
                                                               int l_end,
                                                               double theta) {
  if (l_start < 0 || l_end < l_start) {
    co_return;
  }
  int m = l_start;
  double P_ell_minus_one_m = reduced_spherical_Pmm(m, theta);
  // ell = l_start
  co_yield P_ell_minus_one_m;
  if (l_start == l_end) {
    co_return;
  }
  double cos_theta = std::cos(theta);
  double P_ell_m = cos_theta * std::sqrt(2 * m + 3) * P_ell_minus_one_m;
  // ell = l_start + 1
  co_yield P_ell_m;
  for (int ell = m + 2; ell <= l_end; ++ell) {
    const double den_ell_m = (ell - m) * 1.0 * (ell + m);
    const double c_ell_m =
        std::sqrt(((2.0 * ell - 1.0) * (2.0 * ell + 1.0)) / den_ell_m);
    const double den_ell_minus_one_m =
        (ell - m) * 1.0 * (ell + m) * (2.0 * ell - 3.0);
    const double c_ell_minus_one_m =
        std::sqrt(((ell - m - 1.0) * (ell + m - 1.0) * (2.0 * ell + 1.0)) /
                  den_ell_minus_one_m);
    const double q =
        cos_theta * c_ell_m * P_ell_m - c_ell_minus_one_m * P_ell_minus_one_m;
    P_ell_minus_one_m = P_ell_m;
    P_ell_m = q;
    co_yield P_ell_m;
  }
}

/**
 * @brief Generate a sequence of associated Legendre polynomials with spherical
 * harmonics normalization \f$P_{\ell m}(\theta) = e^{-im\phi}Y_{\ell m}(\theta,
 * \phi)\f$ for fixed order \f$m=\ell_{start}\f$ and degree \f$\ell =
 * \ell_{start}, \ell_{start} + 1, \ldots, \ell_{end}\f$. Yields pairs of (l,
 * P_ell_m). Does not check the validity of \f$\theta\f$.
 *
 * @param l_start Starting value \f$\ell\f$. Equivalent
 * @param l_end Final value of \f$\ell\f$.
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi/2\f$).
 */
mathutils::SimpleGenerator<std::pair<int, double>>
enumerate_reduced_spherical_Plm_recursion_three_term_upward_ell(int l_start,
                                                                int l_end,
                                                                double theta) {
  if (l_start < 0 || l_end < l_start) {
    co_return;
  }
  int m = l_start;
  double P_ell_minus_one_m = reduced_spherical_Pmm(m, theta);
  // ell = l_start
  co_yield {l_start, P_ell_minus_one_m};
  if (l_start == l_end) {
    co_return;
  }
  double cos_theta = std::cos(theta);
  double P_ell_m = cos_theta * std::sqrt(2 * m + 3) * P_ell_minus_one_m;
  // ell = l_start + 1
  co_yield {l_start + 1, P_ell_m};
  for (int ell = m + 2; ell <= l_end; ++ell) {
    const double den_ell_m = (ell - m) * 1.0 * (ell + m);
    const double c_ell_m =
        std::sqrt(((2.0 * ell - 1.0) * (2.0 * ell + 1.0)) / den_ell_m);
    const double den_ell_minus_one_m =
        (ell - m) * 1.0 * (ell + m) * (2.0 * ell - 3.0);
    const double c_ell_minus_one_m =
        std::sqrt(((ell - m - 1.0) * (ell + m - 1.0) * (2.0 * ell + 1.0)) /
                  den_ell_minus_one_m);
    const double q =
        cos_theta * c_ell_m * P_ell_m - c_ell_minus_one_m * P_ell_minus_one_m;
    P_ell_minus_one_m = P_ell_m;
    P_ell_m = q;
    co_yield {ell, P_ell_m};
  }
}

/**
 * @brief Compute the associated Legendre polynomial with spherical harmonics
 * normalization \f$P_{\ell m}(\theta) = e^{-im\phi}Y_{\ell m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi/2\f$ and \f$m\geq 0\f$. Does not check the validity
 * of inputs.
 *
 * @param l Degree of the polynomial (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the polynomial (\f$m=0,1,\ldots,\ell\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi/2\f$).
 * @return double Value of the associated normalized Legendre polynomial.
 */
inline double reduced_spherical_Plm(int l, int m, double theta) {
  // double cos_theta = std::cos(theta);
  // // P_{m m}
  // double P_ell_minus_one_m = reduced_spherical_Pmm(m, theta);
  // if (l == m) {
  //   return P_ell_minus_one_m;
  // }
  // // P_{m+1 m}
  // double P_ell_m = cos_theta * std::sqrt(2 * m + 3) * P_ell_minus_one_m;
  // for (int ell = m + 2; ell <= l; ++ell) {
  //   // double q =
  //   //     cos_theta *
  //   //         std::sqrt((2 * ell - 1) * (2 * ell + 1) / ((ell - m) * (ell +
  //   //         m))) * P_ell_m -
  //   //     std::sqrt((ell - m - 1) * (ell + m - 1) * (2 * ell + 1) /
  //   //               ((ell - m) * (ell + m) * (2 * ell - 3))) *
  //   //         P_ell_minus_one_m;
  //   const double den_ell_m = (ell - m) * 1.0 * (ell + m);
  //   const double c_ell_m =
  //       std::sqrt(((2.0 * ell - 1.0) * (2.0 * ell + 1.0)) / den_ell_m);
  //   const double den_ell_minus_one_m =
  //       (ell - m) * 1.0 * (ell + m) * (2.0 * ell - 3.0);
  //   const double c_ell_minus_one_m =
  //       std::sqrt(((ell - m - 1.0) * (ell + m - 1.0) * (2.0 * ell + 1.0)) /
  //                 den_ell_minus_one_m);
  //   const double q =
  //       cos_theta * c_ell_m * P_ell_m - c_ell_minus_one_m *
  //       P_ell_minus_one_m;
  //   P_ell_minus_one_m = P_ell_m;
  //   P_ell_m = q;
  // }
  // return P_ell_m;
  double P_ell_m{0.0};
  for (auto P : generate_reduced_spherical_Plm_recursion_three_term_upward_ell(
           m, l, theta)) {
    // ell_start = m
    // ell_end = l
    P_ell_m = P;
  }
  return P_ell_m;
}

/**
 * @brief Compute the associated Legendre polynomial with spherical harmonics
 * normalization \f$P_{\ell m}(\theta) = e^{-im\phi}Y_{\ell m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the polynomial (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the polynomial (\f$m=-\ell,\ldots,\ell\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi\f$).
 * @return double Value of the associated normalized Legendre polynomial.
 */
inline double spherical_Plm(int l, int m, double theta) {
  int abs_m = std::abs(m);
  // int sigma = 1;
  // if (m < 0) {
  //   sigma *= std::pow(-1, m);
  // }
  // if (theta > M_PI_2) {
  //   sigma *= std::pow(-1, l-abs_m);
  // }
  // sign difference between spherical_Plm and reduced_spherical_Plm
  // int sigma =
  //     ((m < 0) && (m & 1)) ^ ((theta > M_PI_2) && ((l - abs_m) & 1)) ? -1 :
  //     1;
  // // transform theta to [0, pi/2]
  // theta = std::min(theta, M_PI - theta);
  // m = abs_m;
  // return sigma * reduced_spherical_Plm(l, abs_m, theta);
  return ((m < 0) && (m & 1)) ^ ((theta > M_PI_2) && ((l - abs_m) & 1))
             ? -reduced_spherical_Plm(l, abs_m, std::min(theta, M_PI - theta))
             : reduced_spherical_Plm(l, abs_m, std::min(theta, M_PI - theta));
}

/**
 * @brief Compute the real spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the spherical harmonic (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the spherical harmonic (\f$m=-\ell,\ldots,\ell\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi\f$).
 * @param phi Azimuthal angle in radians (\f$0\leq\phi<2\pi\f$).
 * @return double Value of the real spherical harmonic.
 */
inline double recursive_real_Ylm(int l, int m, double theta, double phi) {
  // int abs_m = std::abs(m);
  // double Plm = spherical_Plm(l, abs_m, theta);
  // if (m < 0) {
  //   return (1 - 2 * (m & 1)) * std::sqrt(2) * std::sin(abs_m * phi) * Plm;
  // } else if (m > 0) {
  //   return (1 - 2 * (m & 1)) * std::sqrt(2) * std::cos(abs_m * phi) * Plm;
  // }
  // // m == 0
  // return Plm;
  if (m < 0) {
    return -std::sqrt(2) * std::sin(m * phi) * spherical_Plm(l, m, theta);
  } else if (m > 0) {
    return (1 - 2 * (m & 1)) * std::sqrt(2) * std::cos(m * phi) *
           spherical_Plm(l, m, theta);
  }
  // m == 0
  return spherical_Plm(l, m, theta);
}

/**
 * @brief Compute the real spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the spherical harmonic (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the spherical harmonic (\f$m=-\ell,\ldots,\ell\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi\f$).
 * @param phi Azimuthal angle in radians (\f$0\leq\phi<2\pi\f$).
 * @return double Value of the real spherical harmonic.
 */
inline double real_Ylm(int l, int m, double theta, double phi) {
  // check l and m
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (theta < 0 || theta > M_PI) {
    throw std::out_of_range("theta must be in the range [0, pi]");
  }
  return recursive_real_Ylm(l, m, theta, phi);
}

/**
 * @brief Compute the real spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the spherical harmonic (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the spherical harmonic (\f$m=-\ell,\ldots,\ell\f$).
 * @param thetaphi_coord_P Matrix containing the polar and azimuthal angles.
 * @return Eigen::VectorXd Values of the real spherical harmonics.
 */
Eigen::VectorXd real_Ylm(int l, int m,
                         const Eigen::MatrixXd &thetaphi_coord_P) {
  // check l and m
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  Eigen::VectorXd result(thetaphi_coord_P.rows());
  for (int i = 0; i < thetaphi_coord_P.rows(); ++i) {
    double theta = thetaphi_coord_P(i, 0);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double phi = thetaphi_coord_P(i, 1);
    result(i) = recursive_real_Ylm(l, m, theta, phi);
  }
  return result;
}

/**
 * @brief Compute real spherical harmonics \f$y_{l m}(\theta, \phi)\f$ for
 * \f$\ell=0,...,\ell_{max}\f$ at the given coordinates.
 *
 * @param l_max The maximum order of the spherical harmonics (non-negative
 * integer).
 * @param thetaphi_coord_P A matrix of shape (num_points, 2) where each row
 * contains the polar angle \f$\theta\f$ and azimuthal angle \f$\phi\f$ in
 * radians.
 * @return A matrix of shape (num_points, num_modes=l_max * (l_max + 2) + 1).
 * Mode index is related to (l,m) by
 * spherical_harmonic_index_n_LM/spherical_harmonic_index_lm_N functions.
 */
Eigen::MatrixXd compute_all_real_Ylm(int l_max,
                                     const Eigen::MatrixXd &thetaphi_coord_P) {
  // check l_max
  if (l_max < 0) {
    throw std::out_of_range("l_max must be non-negative");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int num_points = thetaphi_coord_P.rows();
  if (num_points <= 0) {
    throw std::invalid_argument("thetaphi_coord_P must have at least one row");
  }
  //////////////////////////////////
  int num_modes = l_max * (l_max + 2) + 1; // = n_LM(l_max, l_max)+1
  Eigen::MatrixXd Y(num_points, num_modes);
  Y.setZero();

  for (int p{0}; p < num_points; ++p) {
    double theta = thetaphi_coord_P(p, 0);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double phi = thetaphi_coord_P(p, 1);
    double reduced_theta =
        std::min(theta, M_PI - theta); // transform theta to [0, pi/2]
    // m = 0
    for (auto [l, reduced_P] :
         enumerate_reduced_spherical_Plm_recursion_three_term_upward_ell(
             0, l_max, reduced_theta)) {
      int n = l * (l + 1);
      Y(p, n) = ((theta > M_PI_2) && (l & 1)) ? -reduced_P : reduced_P;
    }
    // m = +/-1, ... , +/-l_max
    for (int m = 1; m <= l_max; ++m) {
      for (auto [l, reduced_P] :
           enumerate_reduced_spherical_Plm_recursion_three_term_upward_ell(
               m, l_max, reduced_theta)) {
        int n_plus = l * (l + 1) + m;
        int n_minus = l * (l + 1) - m;
        // Q = (-1)^m * sqrt(2) * P_{l|m|}(theta)
        double Q = ((m & 1) ^ ((theta > M_PI_2) && ((l - m) & 1)))
                       ? -std::sqrt(2) * reduced_P
                       : std::sqrt(2) * reduced_P;
        // Y_{l |m|} = (-1)^m * sqrt(2) * P_{l|m|}*cos(|m|*phi)
        Y(p, n_plus) = std::cos(m * phi) * Q;
        // Y_{l, -|m|} = (-1)^m * sqrt(2) * P_{l|m|}*sin(|m|*phi)
        Y(p, n_minus) = std::sin(m * phi) * Q;
      }
    }
  } // end for p
  return Y;
}

/**
 * @brief Compute the spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the spherical harmonic (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the spherical harmonic (\f$m=-\ell,\ldots,\ell\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi\f$).
 * @param phi Azimuthal angle in radians (\f$0\leq\phi<2\pi\f$).
 * @return std::complex<double> Value of the spherical harmonic.
 */
inline std::complex<double> recursive_Ylm(int l, int m, double theta,
                                          double phi) {
  return spherical_Plm(l, m, theta) *
         std::exp(std::complex<double>(0, m * phi));
}

/**
 * @brief Compute the spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the spherical harmonic (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the spherical harmonic (\f$m=-\ell,\ldots,\ell\f$).
 * @param theta Polar angle in radians (\f$0\leq\theta\leq\pi\f$).
 * @param phi Azimuthal angle in radians (\f$0\leq\phi<2\pi\f$).
 * @return std::complex<double> Value of the spherical harmonic.
 */
inline std::complex<double> Ylm(int l, int m, double theta, double phi) {
  // check l and m
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (theta < 0 || theta > M_PI) {
    throw std::out_of_range("theta must be in the range [0, pi]");
  }
  return recursive_Ylm(l, m, theta, phi);
}

/**
 * @brief Compute the spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l Degree of the spherical harmonic (\f$\ell=0,1,\ldots\f$).
 * @param m Order of the spherical harmonic (\f$m=-\ell,\ldots,\ell\f$).
 * @param thetaphi_coord_P Matrix containing the polar and azimuthal angles.
 * @return Eigen::VectorXcd Values of the spherical harmonics.
 */
Eigen::VectorXcd Ylm(int l, int m, const Eigen::MatrixXd &thetaphi_coord_P) {

  // check l and m
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  Eigen::VectorXcd result(thetaphi_coord_P.rows());
  for (int i = 0; i < thetaphi_coord_P.rows(); ++i) {
    double theta = thetaphi_coord_P(i, 0);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double phi = thetaphi_coord_P(i, 1);
    result(i) = recursive_Ylm(l, m, theta, phi);
  }
  return result;
}

/**
 * @brief Compute the spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * for \f$0\leq\theta\leq\pi\f$ and \f$-\ell \leq m\geq \ell\f$.
 *
 * @param l_max The maximum order of the spherical harmonics (non-negative
 * integer).
 * @param thetaphi_coord_P A matrix of shape (num_points, 2) where each row
 * contains the polar angle \f$\theta\f$ and azimuthal angle \f$\phi\f$ in
 * radians.
 * @return A matrix of shape (num_points, num_modes=l_max * (l_max + 2) + 1).
 * Mode index is related to (l,m) by
 * spherical_harmonic_index_n_LM/spherical_harmonic_index_lm_N functions.
 */
Eigen::MatrixXcd compute_all_Ylm(int l_max,
                                 const Eigen::MatrixXd &thetaphi_coord_P) {
  // check l_max
  if (l_max < 0) {
    throw std::out_of_range("l_max must be non-negative");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int num_points = thetaphi_coord_P.rows();
  if (num_points <= 0) {
    throw std::invalid_argument("thetaphi_coord_P must have at least one row");
  }
  //////////////////////////////////
  int num_modes = l_max * (l_max + 2) + 1; // = n_LM(l_max, l_max)+1
  Eigen::MatrixXcd Y(num_points, num_modes);
  Y.setZero();

  for (int p{0}; p < num_points; ++p) {
    double theta = thetaphi_coord_P(p, 0);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double phi = thetaphi_coord_P(p, 1);
    double reduced_theta =
        std::min(theta, M_PI - theta); // transform theta to [0, pi/2]
    // m = 0
    for (auto [l, reduced_P] :
         enumerate_reduced_spherical_Plm_recursion_three_term_upward_ell(
             0, l_max, reduced_theta)) {
      int n = l * (l + 1);
      Y(p, n) = ((theta > M_PI_2) && (l & 1)) ? -reduced_P : reduced_P;
    }
    // m = +/-1, ... , +/-l_max
    for (int m = 1; m <= l_max; ++m) {
      for (auto [l, reduced_P] :
           enumerate_reduced_spherical_Plm_recursion_three_term_upward_ell(
               m, l_max, reduced_theta)) {
        int n_plus = l * (l + 1) + m;
        int n_minus = l * (l + 1) - m;
        // Y_{l |m|} = P_{l|m|}*exp(i|m|phi)
        Y(p, n_plus) =
            ((theta > M_PI_2) && ((l - m) & 1))
                ? -reduced_P * std::exp(std::complex<double>(0, m * phi))
                : reduced_P * std::exp(std::complex<double>(0, m * phi));
        // Y_{l, -|m|} = (-1)^m conj(Y_{l|m|})
        Y(p, n_minus) =
            (m & 1) ? -std::conj(Y(p, n_plus)) : std::conj(Y(p, n_plus));
      }
    }
  } // end for p
  return Y;
}

//////////////////////////////////////////////////////
// Alternative implementations of spherical harmonics.
// May be unstable for large l and m.

/**
 * @brief Compute real spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * using series expansion in cos(theta) and sin(theta). Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
inline double series_real_Ylm(int l, int m, double theta, double phi) {
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (theta < 0 || theta > M_PI) {
    throw std::out_of_range("theta must be in the range [0, pi]");
  }
  int abs_m = std::abs(m);
  double cos_theta = std::cos(theta);
  double sin_theta = std::sin(theta);
  auto [log_abs_cos_theta, arg_over_pi_cos_theta] =
      ReLogRe_ImLogRe_over_pi(cos_theta);
  auto [log_abs_sin_theta, arg_over_pi_sin_theta] =
      ReLogRe_ImLogRe_over_pi(sin_theta);
  double Xlm = 0.0;
  for (int k{0}; k <= (l - abs_m) / 2; k++) {
    int ImLog_over_pi_Xklm =
        k + (l - abs_m) * arg_over_pi_cos_theta + abs_m * arg_over_pi_sin_theta;
    double ReLog_Xklm =
        -0.5 * std::log(4 * M_PI) - (abs_m + 2 * k) * std::log(2) +
        0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l + abs_m) +
        0.5 * log_factorial(l - abs_m) - log_factorial(l - abs_m - 2 * k) -
        log_factorial(abs_m + k) - log_factorial(k);
    //  +
    // (l - abs_m - 2 * k) * log_abs_cos_theta +
    // (abs_m + 2 * k) * log_abs_sin_theta;
    int pow_cos = (l - abs_m - 2 * k);
    int pow_sin = (abs_m + 2 * k);
    ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
    ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
    Xlm += minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
  }
  return (m < 0)   ? std::sqrt(2) * std::sin(abs_m * phi) * Xlm
         : (m > 0) ? std::sqrt(2) * std::cos(abs_m * phi) * Xlm
                   : Xlm;
}

/**
 * @brief Compute real spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * using series expansion in cos(theta) and sin(theta). Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
Eigen::VectorXd series_real_Ylm(int l, int m,
                                const Eigen::MatrixXd &thetaphi_coord_P) {

  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int abs_m = std::abs(m);
  int num_points = thetaphi_coord_P.rows();
  Eigen::VectorXd Y(num_points);
  Y.setZero();
  for (int p = 0; p < num_points; ++p) {
    double theta = thetaphi_coord_P(p, 0);
    double phi = thetaphi_coord_P(p, 1);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double cos_theta = std::cos(theta);
    double sin_theta = std::sin(theta);
    auto [log_abs_cos_theta, arg_over_pi_cos_theta] =
        ReLogRe_ImLogRe_over_pi(cos_theta);
    auto [log_abs_sin_theta, arg_over_pi_sin_theta] =
        ReLogRe_ImLogRe_over_pi(sin_theta);
    double Xlm = 0.0;
    for (int k{0}; k <= (l - abs_m) / 2; k++) {
      int ImLog_over_pi_Xklm = k + (l - abs_m) * arg_over_pi_cos_theta +
                               abs_m * arg_over_pi_sin_theta;
      double ReLog_Xklm =
          -0.5 * std::log(4 * M_PI) - (abs_m + 2 * k) * std::log(2) +
          0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l + abs_m) +
          0.5 * log_factorial(l - abs_m) - log_factorial(l - abs_m - 2 * k) -
          log_factorial(abs_m + k) - log_factorial(k);
      // +
      // (l - abs_m - 2 * k) * log_abs_cos_theta +
      // (abs_m + 2 * k) * log_abs_sin_theta;
      int pow_cos = (l - abs_m - 2 * k);
      int pow_sin = (abs_m + 2 * k);
      ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
      ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
      Xlm += minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
    }
    Y(p) = (m < 0)   ? std::sqrt(2) * std::sin(abs_m * phi) * Xlm
           : (m > 0) ? std::sqrt(2) * std::cos(abs_m * phi) * Xlm
                     : Xlm; // m == 0
  }
  return Y;
}

/**
 * @brief Compute spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * using series expansion in cos(theta) and sin(theta). Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
inline std::complex<double> series_Ylm(int l, int m, double theta, double phi) {
  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (theta < 0 || theta > M_PI) {
    throw std::out_of_range("theta must be in the range [0, pi]");
  }
  int abs_m = std::abs(m);
  double cos_theta = std::cos(theta);
  double sin_theta = std::sin(theta);
  auto [log_abs_cos_theta, arg_over_pi_cos_theta] =
      ReLogRe_ImLogRe_over_pi(cos_theta);
  auto [log_abs_sin_theta, arg_over_pi_sin_theta] =
      ReLogRe_ImLogRe_over_pi(sin_theta);
  double Xlm = 0.0;
  for (int k{0}; k <= (l - abs_m) / 2; k++) {
    int ImLog_over_pi_Xklm =
        k + (l - abs_m) * arg_over_pi_cos_theta + abs_m * arg_over_pi_sin_theta;
    double ReLog_Xklm = -0.5 * std::log(4 * M_PI) - abs_m * std::log(2) +
                        0.5 * std::log(2 * l + 1) +
                        0.5 * log_factorial(l + abs_m) +
                        0.5 * log_factorial(l - abs_m) - 2 * k * std::log(2) -
                        log_factorial(l - abs_m - 2 * k) -
                        log_factorial(abs_m + k) - log_factorial(k);
    int pow_cos = (l - abs_m - 2 * k);
    int pow_sin = (abs_m + 2 * k);
    ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
    ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
    Xlm += minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
  }
  return (m < 0) ? std::exp(std::complex<double>(0, m * phi)) * Xlm
         : (m > 0)
             ? static_cast<std::complex<double>>(minus_one_to_int_pow(m)) *
                   std::exp(std::complex<double>(0, m * phi)) * Xlm
             : static_cast<std::complex<double>>(Xlm);
}

/**
 * @brief Compute spherical harmonics \f$Y_{l m}(\theta, \phi)\f$
 * using series expansion in cos(theta) and sin(theta). Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
Eigen::VectorXcd series_Ylm(int l, int m,
                            const Eigen::MatrixXd &thetaphi_coord_P) {

  if (l < 0) {
    throw std::out_of_range("l must be non-negative");
  }
  if (m < -l || m > l) {
    throw std::out_of_range("m must be in the range [-l, l]");
  }
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int abs_m = std::abs(m);
  int num_points = thetaphi_coord_P.rows();
  Eigen::VectorXcd Y(num_points);
  Y.setZero();
  for (int p = 0; p < num_points; ++p) {
    double theta = thetaphi_coord_P(p, 0);
    double phi = thetaphi_coord_P(p, 1);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double cos_theta = std::cos(theta);
    double sin_theta = std::sin(theta);
    auto [log_abs_cos_theta, arg_over_pi_cos_theta] =
        ReLogRe_ImLogRe_over_pi(cos_theta);
    auto [log_abs_sin_theta, arg_over_pi_sin_theta] =
        ReLogRe_ImLogRe_over_pi(sin_theta);
    for (int k{0}; k <= (l - abs_m) / 2; k++) {
      // adding (m + abs_m) / 2 here takes care of (-1)^m for m>0
      int ImLog_over_pi_Xklm = (m + abs_m) / 2 + k +
                               (l - abs_m) * arg_over_pi_cos_theta +
                               abs_m * arg_over_pi_sin_theta;
      double ReLog_Xklm =
          -0.5 * std::log(4 * M_PI) - (abs_m + 2 * k) * std::log(2) +
          0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l + abs_m) +
          0.5 * log_factorial(l - abs_m) - log_factorial(l - abs_m - 2 * k) -
          log_factorial(abs_m + k) - log_factorial(k);
      //  +
      // (l - abs_m - 2 * k) * log_abs_cos_theta +
      // (abs_m + 2 * k) * log_abs_sin_theta;
      int pow_cos = (l - abs_m - 2 * k);
      int pow_sin = (abs_m + 2 * k);
      ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
      ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
      Y(p) += minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
    }
    Y(p) *= std::exp(std::complex<double>(0, m * phi));
  }
  return Y;
}

/**
 * @brief Compute real spherical harmonics \f$y_{l m}(\theta, \phi)\f$ for
 * \f$\ell=0,...,\ell_{max}\f$ at the given coordinates. Unstable for large
 * \f$l\f$ and \f$m\f$.
 *
 * @param l_max The maximum order of the spherical harmonics (non-negative
 * integer).
 * @param thetaphi_coord_P A matrix of shape (num_points, 2) where each row
 * contains the polar angle \f$\theta\f$ and azimuthal angle \f$\phi\f$ in
 * radians.
 * @return A matrix of shape (num_points, l_max * (l_max + 2) + 1)
 */
Eigen::MatrixXd
compute_all_series_real_Ylm(int l_max,
                            const Eigen::MatrixXd &thetaphi_coord_P) {
  // check l_max
  if (l_max < 0) {
    throw std::out_of_range("l_max must be non-negative");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int num_points = thetaphi_coord_P.rows();
  if (num_points <= 0) {
    throw std::invalid_argument("thetaphi_coord_P must have at least one row");
  }
  //////////////////////////////////
  int num_modes = l_max * (l_max + 2) + 1; // = n_LM(l_max, l_max)+1
  Eigen::MatrixXd Y(num_points, num_modes);
  Y.setZero();

  for (int p{0}; p < num_points; ++p) {
    double theta = thetaphi_coord_P(p, 0);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double phi = thetaphi_coord_P(p, 1);
    double cos_theta = std::cos(theta);
    double sin_theta = std::sin(theta);
    // get ReLogRe_ImLogRe_over_pi for cos(theta) and sin(theta)
    auto [log_abs_cos_theta, arg_over_pi_cos_theta] =
        ReLogRe_ImLogRe_over_pi(cos_theta);
    auto [log_abs_sin_theta, arg_over_pi_sin_theta] =
        ReLogRe_ImLogRe_over_pi(sin_theta);
    for (int l{0}; l <= l_max; l++) {
      // m = 0 case
      int n = l * (l + 1);
      for (int k{0}; k <= l / 2; k++) {
        int ImLog_over_pi_Xklm = k + l * arg_over_pi_cos_theta;
        double ReLog_Xklm = -0.5 * std::log(4 * M_PI) - (2 * k) * std::log(2) +
                            0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l) +
                            0.5 * log_factorial(l) - log_factorial(l - 2 * k) -
                            log_factorial(k) - log_factorial(k);
        //  +
        // (l - 2 * k) * log_abs_cos_theta +
        // (2 * k) * log_abs_sin_theta;
        int pow_cos = l - 2 * k;
        int pow_sin = 2 * k;
        ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
        ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
        Y(p, n) +=
            minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
      }
      for (int m{1}; m <= l; m++) {
        int n_plus = l * (l + 1) + m;
        int n_minus = l * (l + 1) - m;
        for (int k{0}; k <= (l - m) / 2; k++) {
          int ImLog_over_pi_Xklm =
              k + (l - m) * arg_over_pi_cos_theta + m * arg_over_pi_sin_theta;
          double ReLog_Xklm =
              -0.5 * std::log(4 * M_PI) - (m + 2 * k) * std::log(2) +
              0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l + m) +
              0.5 * log_factorial(l - m) - log_factorial(l - m - 2 * k) -
              log_factorial(m + k) - log_factorial(k);
          // +
          // (l - m - 2 * k) * log_abs_cos_theta +
          // (m + 2 * k) * log_abs_sin_theta;
          int pow_cos = (l - m - 2 * k);
          int pow_sin = (m + 2 * k);
          ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
          ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
          Y(p, n_plus) +=
              minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
        }
        Y(p, n_minus) = std::sqrt(2) * std::sin(m * phi) * Y(p, n_plus);
        Y(p, n_plus) *= std::sqrt(2) * std::cos(m * phi);
      }
    }
  }
  return Y;
}

/**
 * @brief Compute spherical harmonics \f$Y_{l m}(\theta, \phi)\f$ for
 * \f$\ell=0,...,\ell_{max}\f$ at the given coordinates. Unstable for large
 * \f$l\f$ and \f$m\f$.
 *
 * @param l_max The maximum order of the spherical harmonics (non-negative
 * integer).
 * @param thetaphi_coord_P A matrix of shape (num_points, 2) where each row
 * contains the polar angle \f$\theta\f$ and azimuthal angle \f$\phi\f$ in
 * radians.
 * @return A matrix of shape (num_points, l_max * (l_max + 2) + 1)
 */
Eigen::MatrixXcd
compute_all_series_Ylm(int l_max, const Eigen::MatrixXd &thetaphi_coord_P) {
  // check l_max
  if (l_max < 0) {
    throw std::out_of_range("l_max must be non-negative");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int num_points = thetaphi_coord_P.rows();
  if (num_points <= 0) {
    throw std::invalid_argument("thetaphi_coord_P must have at least one row");
  }
  //////////////////////////////////
  int num_modes = l_max * (l_max + 2) + 1; // = n_LM(l_max, l_max)+1
  Eigen::MatrixXcd Y(num_points, num_modes);
  Y.setZero();

  for (int p{0}; p < num_points; ++p) {
    double theta = thetaphi_coord_P(p, 0);
    if (theta < 0 || theta > M_PI) {
      throw std::out_of_range("theta must be in the range [0, pi]");
    }
    double phi = thetaphi_coord_P(p, 1);
    double cos_theta = std::cos(theta);
    double sin_theta = std::sin(theta);
    // get ReLogRe_ImLogRe_over_pi for cos(theta) and sin(theta)
    auto [log_abs_cos_theta, arg_over_pi_cos_theta] =
        ReLogRe_ImLogRe_over_pi(cos_theta);
    auto [log_abs_sin_theta, arg_over_pi_sin_theta] =
        ReLogRe_ImLogRe_over_pi(sin_theta);
    for (int l{0}; l <= l_max; l++) {
      // m = 0 case
      int n = l * (l + 1);
      for (int k{0}; k <= l / 2; k++) {
        int ImLog_over_pi_Xklm = k + l * arg_over_pi_cos_theta;
        double ReLog_Xklm = -0.5 * std::log(4 * M_PI) - (2 * k) * std::log(2) +
                            0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l) +
                            0.5 * log_factorial(l) - log_factorial(l - 2 * k) -
                            log_factorial(k) - log_factorial(k);
        //  +
        // (l - 2 * k) * log_abs_cos_theta +
        // (2 * k) * log_abs_sin_theta;
        int pow_cos = l - 2 * k;
        int pow_sin = 2 * k;
        ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
        ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
        Y(p, n) +=
            minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
      }
      // m=-l,...,l
      for (int m{1}; m <= l; m++) {
        int n_plus = l * (l + 1) + m;
        int n_minus = l * (l + 1) - m;
        for (int k{0}; k <= (l - m) / 2; k++) {
          int ImLog_over_pi_Xklm =
              k + (l - m) * arg_over_pi_cos_theta + m * arg_over_pi_sin_theta;
          double ReLog_Xklm =
              -0.5 * std::log(4 * M_PI) - (m + 2 * k) * std::log(2) +
              0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l + m) +
              0.5 * log_factorial(l - m) - log_factorial(l - m - 2 * k) -
              log_factorial(m + k) - log_factorial(k);
          //  +
          // (l - m - 2 * k) * log_abs_cos_theta +
          // (m + 2 * k) * log_abs_sin_theta;
          int pow_cos = (l - m - 2 * k);
          int pow_sin = (m + 2 * k);
          ReLog_Xklm += (pow_cos > 0) ? (pow_cos * log_abs_cos_theta) : 0.0;
          ReLog_Xklm += (pow_sin > 0) ? (pow_sin * log_abs_sin_theta) : 0.0;
          Y(p, n_plus) +=
              minus_one_to_int_pow(ImLog_over_pi_Xklm) * std::exp(ReLog_Xklm);
        }
        Y(p, n_minus) =
            Y(p, n_plus) * std::exp(std::complex<double>(0, -m * phi));
        Y(p, n_plus) *=
            static_cast<std::complex<double>>(minus_one_to_int_pow(m)) *
            std::exp(std::complex<double>(0, m * phi));
      }
    }
  }
  return Y;
}

/**
 * @brief Compute Ylm(theta, phi)/exp(i*theta*phi) for m>=0 and 0<=theta<=pi.
 * Unstable for large \f$l\f$
 *
 * @param l Degree of the spherical harmonic.
 * @param m Order of the spherical harmonic.
 * @param theta Polar angle in radians.
 * @return Value of Ylm(theta, phi)/exp(i*theta*phi)
 */
inline double phi_independent_Ylm(int l, int m, double theta) {
  double epsilon = 1e-8;
  double minus_log4 = std::log(0.25);

  int abs_m = std::abs(m);

  int ell_minus_m = l - abs_m;
  double cos_theta = std::cos(theta);
  double abs_cos_theta = std::abs(cos_theta);
  // double sin_theta = std::sin(theta); // always positive for theta in [0, pi]
  double abs_sin_theta = std::sin(theta); // std::abs(sin_theta);

  double rlm = 1.0 / (2.0 * std::sqrt(M_PI));
  if ((m > 0) && (abs_m % 2 == 1)) {
    rlm *= -1;
  }
  // if ((m < 0) && (abs_m % 2 == 1)) {
  //   rlm *= -1;
  // }
  // if (abs_m % 2 == 1) {
  //   rlm *= -1;
  // }
  if ((cos_theta < 0) && (ell_minus_m % 2 == 1)) {
    rlm *= -1;
  }
  int k_bound = (ell_minus_m) / 2;
  int sk = 1;
  // double log_qk;
  // double sum_Qk;
  double log_qk = 0.5 * std::log(2 * l + 1) + 0.5 * log_factorial(l + abs_m) -
                  abs_m * std::log(2) - 0.5 * log_factorial(ell_minus_m) -
                  log_factorial(abs_m);

  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  // If cos(theta) ~ +/-sin(theta) replace sin(theta) with tan(theta)
  if (std::abs(abs_cos_theta - abs_sin_theta) < epsilon) {
    double tan_theta = std::tan(theta);
    double abs_tan_theta = std::abs(tan_theta);
    double log_abs_cos_theta = std::log(abs_cos_theta);
    double log_abs_tan_theta = std::log(abs_tan_theta);
    log_qk += l * log_abs_cos_theta + abs_m * log_abs_tan_theta;
    double sum_Qk = sk * std::exp(log_qk);
    for (int k = 1; k <= k_bound; ++k) {
      sk *= -1;
      log_qk += 2 * log_abs_tan_theta;
      log_qk += minus_log4 + std::log(ell_minus_m - 2 * k + 2) +
                std::log(ell_minus_m - 2 * k + 1) - std::log(abs_m + k) -
                std::log(k);
      sum_Qk += sk * std::exp(log_qk);
    }
    return rlm * sum_Qk;
  }

  // if cos(theta) ~ 0, sin(theta) ~ 1
  if (abs_cos_theta < epsilon) {
    double log_abs_sin_theta = std::log(abs_sin_theta);
    log_qk += abs_m * log_abs_sin_theta;
    double abs_cos_theta_pow = std::pow(abs_cos_theta, ell_minus_m);
    double sum_Qk = sk * std::exp(log_qk) * abs_cos_theta_pow;
    for (int k = 1; k <= k_bound; ++k) {
      sk *= -1;
      log_qk += minus_log4 + std::log(ell_minus_m - 2 * k + 2) +
                std::log(ell_minus_m - 2 * k + 1) - std::log(abs_m + k) -
                std::log(k);
      abs_cos_theta_pow = std::pow(abs_cos_theta, ell_minus_m - 2 * k);
      sum_Qk += sk * std::exp(log_qk) * abs_cos_theta_pow;
    }

    return rlm * sum_Qk;
  }

  // if sin(theta) ~ 0, cos(theta) ~ +/-1
  if (abs_sin_theta < epsilon) {
    // double log_abs_cos_theta = std::log(abs_cos_theta);
    // log_qk += ell_minus_m * log_abs_cos_theta;
    // double abs_sin_theta_pow = std::pow(abs_sin_theta, abs_m);
    // double sum_Qk = sk * std::exp(log_qk);
    // for (int k = 1; k <= k_bound; ++k) {
    //   sk *= -1;
    //   log_qk += -2 * log_abs_cos_theta;
    //   log_qk += minus_log4 + std::log(ell_minus_m - 2 * k + 2) +
    //             std::log(ell_minus_m - 2 * k + 1) - std::log(abs_m + k) -
    //             std::log(k);
    //   abs_sin_theta_pow = std::pow(abs_sin_theta, abs_m + 2 * k);
    //   sum_Qk += sk * std::exp(log_qk) * abs_sin_theta_pow;
    // }
    // return rlm * sum_Qk;
    // double log_abs_cos_theta = std::log(abs_cos_theta);
    // log_qk += ell_minus_m * log_abs_cos_theta;
    double trig_term =
        std::pow(abs_cos_theta, ell_minus_m) * std::pow(abs_sin_theta, abs_m);
    double sum_Qk = sk * std::exp(log_qk) * trig_term;
    for (int k = 1; k <= k_bound; ++k) {
      sk *= -1;
      log_qk += minus_log4 + std::log(ell_minus_m - 2 * k + 2) +
                std::log(ell_minus_m - 2 * k + 1) - std::log(abs_m + k) -
                std::log(k);
      trig_term = std::pow(abs_cos_theta, ell_minus_m - 2 * k) *
                  std::pow(abs_sin_theta, abs_m + 2 * k);
      sum_Qk += sk * std::exp(log_qk) * trig_term;
    }
    return rlm * sum_Qk;
  }

  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////
  // if log(cos(theta)) and log(sin(theta)) are defined
  double log_abs_cos_theta = std::log(abs_cos_theta);
  double log_abs_sin_theta = std::log(abs_sin_theta);
  log_qk += ell_minus_m * log_abs_cos_theta + abs_m * log_abs_sin_theta;
  double sum_Qk = sk * std::exp(log_qk);
  for (int k = 1; k <= k_bound; ++k) {
    sk *= -1;
    log_qk += -2 * log_abs_cos_theta + 2 * log_abs_sin_theta;
    log_qk += minus_log4 + std::log(ell_minus_m - 2 * k + 2) +
              std::log(ell_minus_m - 2 * k + 1) - std::log(abs_m + k) -
              std::log(k);
    sum_Qk += sk * std::exp(log_qk);
  }

  return rlm * sum_Qk;
}

/**
 * @brief Compute spherical harmonics \f$Y_{l m}(\theta, \phi)\f$ for
 * \f$\ell=0,...,\ell_{max}\f$ at the given coordinates. Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
inline std::complex<double> old_Ylm(int l, int m, double theta, double phi) {
  if (theta > M_PI || theta < 0.0) {
    throw std::out_of_range("theta must be in the range [0, pi]");
  }
  return std::exp(std::complex<double>(0, m * phi)) *
         phi_independent_Ylm(l, m, theta);
}

/**
 * @brief Compute real spherical harmonics \f$y_{l m}(\theta, \phi)\f$ for
 * \f$\ell=0,...,\ell_{max}\f$ at the given coordinates. Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
inline double old_real_Ylm(int l, int m, double theta, double phi) {

  if (theta > M_PI || theta < 0.0) {
    throw std::out_of_range("theta must be in the range [0, pi]");
  }
  int abs_m = std::abs(m);
  double val = phi_independent_Ylm(l, abs_m, theta);
  if (abs_m % 2 == 1) {
    val *= -1;
  }
  if (m < 0) {
    return val * std::sqrt(2) * std::sin(abs_m * phi);
  }
  if (m == 0) {
    return val;
  }
  return val * std::sqrt(2) * std::cos(abs_m * phi);
}

/**
 * @brief Compute real spherical harmonics \f$y_{l m}(\theta, \phi)\f$ for
 * \f$\ell=0,...,\ell_{max}\f$ at the given coordinates. Unstable for large
 * \f$l\f$ and \f$m\f$.
 */
Eigen::MatrixXd
old_compute_all_real_Ylm(int l_max, const Eigen::MatrixXd &thetaphi_coord_P) {
  // check l_max
  if (l_max < 0) {
    throw std::out_of_range("l_max must be non-negative");
  }
  // check thetaphi_coord_P
  if (thetaphi_coord_P.cols() != 2) {
    throw std::invalid_argument("thetaphi_coord_P must have 2 columns");
  }
  int num_points = thetaphi_coord_P.rows();
  if (num_points <= 0) {
    throw std::invalid_argument("thetaphi_coord_P must have at least one row");
  }
  //////////////////////////////////
  int num_modes = l_max * (l_max + 2) + 1; // = n_LM(l_max, l_max)+1
  Eigen::MatrixXd Y(num_points, num_modes);
  Y.setZero();
  for (int l{0}; l <= l_max; l++) {
    for (int m{-l}; m <= l; m++) {
      int n = l * (l + 1) + m;
      for (int p{0}; p < num_points; ++p) {
        double theta = thetaphi_coord_P(p, 0);
        double phi = thetaphi_coord_P(p, 1);
        Y(p, n) = old_real_Ylm(l, m, theta, phi);
      }
    }
  }
  return Y;
}

} // namespace special
} // namespace mathutils

namespace mathutils {} // namespace mathutils

namespace mathutils {
namespace special {

/**
 * @brief Solve for real spherical-harmonic coefficients that best fit a
 *        3-D point cloud on a sphere, with optional Dirichlet smoothing.
 *
 * Solves the Tikhonov system
 *     (Yᵀ Y + λ Lᵀ L) A = Yᵀ X,
 * where
 *     * Y  – design matrix of real harmonics, shape (N, (l_max+1)^2)
 *     * L  – diagonal matrix with entries l(l+1) (Dirichlet energy weight)
 *     * X  – input Cartesian coordinates, shape (N,3)
 * The result A(i,:) gives the (x,y,z) coefficients for harmonic index *i*.
 *
 * @param XYZ0        (N,3) matrix of Cartesian samples.
 * @param l_max       Highest harmonic degree to include.
 * @param reg_lambda  Non-negative Tikhonov parameter (λ = 0 ⇒ plain LS).
 * @return            ((l_max+1)^2, 3) matrix of expansion coefficients.
 */
inline Eigen::MatrixXd
fit_real_sh_coefficients_to_points(const Eigen::MatrixXd &XYZ0, int l_max,
                                   double reg_lambda = 0.0) {
  // ---------------------------------------------------------------------
  // 0. Basic argument checks
  // ---------------------------------------------------------------------
  if (l_max < 0)
    throw std::invalid_argument(
        "fit_real_sh_coefficients_to_points: l_max must be non-negative.");

  if (XYZ0.cols() != 3)
    throw std::invalid_argument("fit_real_sh_coefficients_to_points: XYZ0 must "
                                "have exactly 3 columns.");

  if (XYZ0.rows() == 0)
    throw std::invalid_argument("fit_real_sh_coefficients_to_points: XYZ0 must "
                                "contain at least one point.");

  // ---------------------------------------------------------------------
  // 1. Dimensions
  // ---------------------------------------------------------------------
  const int num_modes = (l_max + 1) * (l_max + 1); // (l_max+1)^2
  const int N = static_cast<int>(XYZ0.rows());

  // ---------------------------------------------------------------------
  // 2. Build the design matrix  Y  (N × num_modes)
  //    Only directions (θ,φ) matter; radius is ignored.
  // ---------------------------------------------------------------------
  Eigen::MatrixXd thetaPhi = mathutils::thetaphi_from_xyz(XYZ0); // (N,2)
  Eigen::MatrixXd Y = compute_all_real_Ylm(l_max, thetaPhi);

  // ---------------------------------------------------------------------
  // 3. Construct Laplace–Beltrami weights  ℓ(ℓ+1)
  // ---------------------------------------------------------------------
  Eigen::VectorXd laplace(num_modes);
  for (int n = 0; n < num_modes; ++n) {
    auto [l, m] = spherical_harmonic_index_lm_N(n);
    laplace(n) = static_cast<double>(l * (l + 1));
  }

  // ---------------------------------------------------------------------
  // 4. Assemble the normal matrix  M = YᵀY  (SPD)  and add regularisation
  //    directly to its diagonal:  M_ii += λ (ℓ(ℓ+1))²
  // ---------------------------------------------------------------------
  Eigen::MatrixXd M = Y.transpose() * Y; // (num_modes, num_modes)
  if (reg_lambda > 0.0)
    M.diagonal().array() += reg_lambda * laplace.array().square();

  // ---------------------------------------------------------------------
  // 5. Right-hand side  B = Yᵀ X
  // ---------------------------------------------------------------------
  Eigen::MatrixXd B = Y.transpose() * XYZ0; // (num_modes, 3)

  // ---------------------------------------------------------------------
  // 6. Solve  M A = B   via Cholesky (faster & stabler than explicit inverse)
  // ---------------------------------------------------------------------
  Eigen::LLT<Eigen::MatrixXd> chol(M);
  if (chol.info() != Eigen::Success)
    throw std::runtime_error("fit_real_sh_coefficients_to_points: normal "
                             "matrix not SPD (ill-posed fit).");

  Eigen::MatrixXd A = chol.solve(B); // coefficients
  return A;                          // (num_modes, 3)
}

} // namespace special
} // namespace mathutils