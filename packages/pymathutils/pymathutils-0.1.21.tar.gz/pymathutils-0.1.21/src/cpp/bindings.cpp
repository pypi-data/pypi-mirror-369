#include "mathutils/funs.hpp"
#include "mathutils/log_factorial_lookup_table.hpp"
#include "mathutils/spherical_harmonics_index_lookup_table.hpp"
#include <pybind11/complex.h>
#include <pybind11/eigen.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(mathutils_backend, m) {
  m.doc() = "Fast mathematical utilities backend";
  m.attr("__version__") = "0.1.21";

  // Basic utility functions (in main module)
  m.def("sign", &mathutils::sign<double>, "sign function (double)",
        py::arg("x"));
  m.def("sign", &mathutils::sign<int>, "sign function (int)", py::arg("x"));
  m.def("thetaphi_from_xyz", &mathutils::thetaphi_from_xyz,
        "Convert Cartesian coordinates (x, y, z) to unit sphere coordinates "
        "(theta, phi)",
        py::arg("xyz"));
  m.def("xyz_from_rthetaphi", &mathutils::xyz_from_rthetaphi,
        "Convert spherical coordinates (r, theta, phi) to Cartesian "
        "coordinates (x, y, z)",
        py::arg("rthetaphi"));
  m.def("thetaphi_from_xyz", &mathutils::thetaphi_from_xyz,
        "Convert Cartesian coordinates (x, y, z) to spherical coordinates (r, "
        "theta, phi)",
        py::arg("xyz"));

  // Create a submodule for special functions
  py::module_ special =
      m.def_submodule("special", "Special mathematical functions");
  //   special.def("reduced_spherical_Pmm",
  //               &mathutils::special::reduced_spherical_Pmm,
  //               "Compute reduced spherical Pmm", py::arg("m"),
  //               py::arg("theta"));
  //   special.def("reduced_spherical_Plm",
  //               &mathutils::special::reduced_spherical_Plm,
  //               "Compute reduced spherical Plm", py::arg("l"), py::arg("m"),
  //               py::arg("theta"));
  //   special.def("spherical_Plm", &mathutils::special::spherical_Plm,
  //               "Compute spherical Plm", py::arg("l"), py::arg("m"),
  //               py::arg("theta"));
  special.def("Ylm",
              static_cast<std::complex<double> (*)(int, int, double, double)>(
                  &mathutils::special::Ylm),
              "Compute spherical harmonic Ylm for single point", py::arg("l"),
              py::arg("m"), py::arg("theta"), py::arg("phi"));
  special.def(
      "Ylm",
      static_cast<Eigen::VectorXcd (*)(int, int, const Eigen::MatrixXd &)>(
          &mathutils::special::Ylm),
      "Compute spherical harmonic Ylm for multiple points", py::arg("l"),
      py::arg("m"), py::arg("thetaphi_coord_P"));
  special.def("real_Ylm",
              static_cast<double (*)(int, int, double, double)>(
                  &mathutils::special::real_Ylm),
              "Compute real spherical harmonic Ylm for single point",
              py::arg("l"), py::arg("m"), py::arg("theta"), py::arg("phi"));
  special.def(
      "real_Ylm",
      static_cast<Eigen::VectorXd (*)(int, int, const Eigen::MatrixXd &)>(
          &mathutils::special::real_Ylm),
      "Compute real spherical harmonic Ylm for multiple points", py::arg("l"),
      py::arg("m"), py::arg("thetaphi_coord_P"));
  special.def("spherical_harmonic_index_n_LM",
              &mathutils::special::spherical_harmonic_index_n_LM,
              "Convert (l,m) to linear index", py::arg("l"), py::arg("m"));
  special.def("spherical_harmonic_index_lm_N",
              &mathutils::special::spherical_harmonic_index_lm_N,
              "Convert linear index to (l,m)", py::arg("n"));
  // Batch computation functions
  special.def("compute_all_real_Ylm", &mathutils::special::compute_all_real_Ylm,
              "Compute all real Ylm up to l_max", py::arg("l_max"),
              py::arg("thetaphi_coord_P"));
  special.def("compute_all_Ylm", &mathutils::special::compute_all_Ylm,
              "Compute all complex Ylm up to l_max", py::arg("l_max"),
              py::arg("thetaphi_coord_P"));
  special.def("fit_real_sh_coefficients_to_points",
              &mathutils::special::fit_real_sh_coefficients_to_points,
              "Fit real spherical harmonic coefficients to points",
              py::arg("XYZ0"), py::arg("l_max"), py::arg("reg_lambda"));

  //////////////////////////////////
  //////////////////////////////////
  //////////////////////////////////
  special.def("minus_one_to_int_pow", &mathutils::special::minus_one_to_int_pow,
              "Compute (-1)^n for integer n", py::arg("n"));

  special.def("ReLogRe_ImLogRe_over_pi",
              &mathutils::special::ReLogRe_ImLogRe_over_pi<double>,
              "Compute ReLogRe and ImLogRe over pi for a given value (double)",
              py::arg("x"));
  special.def("ReLogRe_ImLogRe_over_pi",
              &mathutils::special::ReLogRe_ImLogRe_over_pi<int>,
              "Compute ReLogRe and ImLogRe over pi for a given value (int)",
              py::arg("x"));

  special.def("log_factorial", &mathutils::special::log_factorial,
              "Compute log factorial of n", py::arg("n"));

  special.def("series_Ylm",
              static_cast<std::complex<double> (*)(int, int, double, double)>(
                  &mathutils::special::series_Ylm),
              "Compute spherical harmonic Ylm for single point", py::arg("l"),
              py::arg("m"), py::arg("theta"), py::arg("phi"));
  special.def(
      "series_Ylm",
      static_cast<Eigen::VectorXcd (*)(int, int, const Eigen::MatrixXd &)>(
          &mathutils::special::series_Ylm),
      "Compute spherical harmonic Ylm for multiple points", py::arg("l"),
      py::arg("m"), py::arg("thetaphi_coord_P"));

  special.def("series_real_Ylm",
              static_cast<double (*)(int, int, double, double)>(
                  &mathutils::special::series_real_Ylm),
              "Compute real spherical harmonic Ylm for single point",
              py::arg("l"), py::arg("m"), py::arg("theta"), py::arg("phi"));
  special.def(
      "series_real_Ylm",
      static_cast<Eigen::VectorXd (*)(int, int, const Eigen::MatrixXd &)>(
          &mathutils::special::series_real_Ylm),
      "Compute real spherical harmonic Ylm for multiple points", py::arg("l"),
      py::arg("m"), py::arg("thetaphi_coord_P"));

  special.def("compute_all_series_real_Ylm",
              &mathutils::special::compute_all_series_real_Ylm,
              "Compute all real Ylm up to l_max", py::arg("l_max"),
              py::arg("thetaphi_coord_P"));

  special.def("old_compute_all_real_Ylm",
              &mathutils::special::old_compute_all_real_Ylm,
              "Old implementation of compute_all_real_Ylm", py::arg("l_max"),
              py::arg("thetaphi_coord_P"));

  special.def("compute_all_series_Ylm",
              &mathutils::special::compute_all_series_Ylm,
              "Compute all complex Ylm up to l_max", py::arg("l_max"),
              py::arg("thetaphi_coord_P"));
}