# tnbsclean

## Description
`tnbsclean` provides functionality to clean EEG, MEG, and other time-series data from mne-python by removing unwanted stimuli using the tnbsclean function. This is especially useful in preprocessing to remove noise or artifacts from signals caused by stimuli events.

## Installation

You can install the package via pip from PyPI:

```bash
pip install tnbsclean
```
## Example use

```bash
import tnbsclean as tnbs

# Example parameters
raw  # Raw time series data in MNE's raw object format
half_win = 3  # Half window size around each stimulus (in samples) that will be chopped away from the artifact peak point
threshold = 2  # Threshold constant above which stimulus is considered significant

# Apply stimulus cleaning 
raw_cleaned, spike_idxs = tnbs.get_stim_markers(raw, half_win, threshold) #cleans based on ECG, returns spike indices
```