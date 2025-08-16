"""A set of software tools for estimating LHCb PID efficiencies.

The package includes several user-callable modules:
- make_eff_hists creates histograms that can be used to estimate the PID
  efficiency of a user's sample
- ref_calib calculates the LHCb PID efficiency of a user reference sample
- merge_trees merges two ROOT files with compatible TTrees
- plot_calib_distributions allows you to plot distributions of variables in the
  calibration datasets
- pklhisto2root converts Pickled boost-histograms to ROOT histograms

More information can be found in README.md.
"""
