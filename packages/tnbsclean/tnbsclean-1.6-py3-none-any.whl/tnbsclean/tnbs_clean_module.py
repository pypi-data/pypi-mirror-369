import numpy as np
import matplotlib.pyplot as plt
import mne
import os, glob
import neo.rawio
import datetime                   
import pandas as pd

def remove_stim(y, sfreq, half_win, threshold):
    """
    @author: Kinkini. M
    Read raw mne object and clean all stim artifacts for selected channel


    Parameters
    ----------
    raw : mne.io.Raw
        The MNE Raw object containing the EEG/MEG data.
    half_win : int
        Half-window length in samples to remove around each artifact.
    threshold : int
        Threshold factor for artifact detection.


    Returns
    -------
    mne raw object
    """
    try:
        #spike_idxs, properties = find_peaks(y, height=0.00005,  width=0.00001)  # height=0 means above 0
        #spike_idxs, properties = find_peaks(abs(y), height=0.00007, width=(None, 7))
        #spike_idxs, properties = find_peaks(abs(y), height=0.000025, width=(None, 7))  # min=None, max=3)  # height=0 means above 0
        print(threshold*(np.median(abs(y))/0.6745))
        spike_idxs = np.where(abs(y) > (threshold*(np.median(abs(y))/0.6745)))[0]

        #distance = max(1, int(round(0.040 * sfreq)))
        #wlen = max(1, int(round(0.050 * sfreq)))
        #spike_idxs, props = find_peaks( -y, prominence=3e-4, distance=distance, wlen=wlen) #invert y

        #spike_idxs = np.where(abs(y) > threshold)[0]
        #print(spike_idxs)
        # 2) convert to times (in seconds)
        spike_times = spike_idxs / sfreq
        # 1) Make a copy of your signal
        y_clean = y.copy().astype(float)

        # 3) Blank out (set to NaN) around each spike
        for idx in spike_idxs:
            start = max(0, idx - half_win)
            end   = min(len(y_clean), idx + half_win)
            y_clean[start:end] = np.nan

        # 4) Interpolate linearly over NaNs
        nans     = np.isnan(y_clean)
        not_nans = ~nans
        y_clean[nans] = np.interp(
            np.flatnonzero(nans),
            np.flatnonzero(not_nans),
            y_clean[not_nans]
        )
    except:
        print('it is likely that this channel is noisy')

    return y_clean, spike_idxs



def stim_clean(raw, half_win, threshold, channel_name):
    """
    @author: Kinkini. M
    Read an MNE Raw object and remova all stim artifacts across all channels


    Parameters
    ----------
    raw : mne.io.Raw
        The MNE Raw object containing the EEG/MEG data.
    half_win : int
        Half-window length in samples to remove around each artifact.
    threshold : int
        Threshold factor for artifact detection.
    channel_name : str
        Name of the electrode/channel to process.

    Returns
    -------
    mne raw object
    """
    data_stim = raw.get_data()
    times = raw.times                      
    sfreq = raw.info['sfreq']
    cleaned_data = []

    #channel_name = "ECG"  # change to your channel
    index = raw.ch_names.index(channel_name)
    print(index)

    y = data_stim[index, :]  
    y_clean, spike_idxs = remove_stim(y, sfreq, half_win, threshold)

    for i in range(np.size(data_stim,0)):
        print(f'processing {raw.ch_names[i]}')
        y = data_stim[i, :]  

        #print(threshold*(np.median(abs(y))/0.6745))
        #spike_idxs = np.where(abs(y) > (threshold*(np.median(abs(y))/0.6745)))[0]

        #distance = max(1, int(round(0.040 * sfreq)))
        #wlen = max(1, int(round(0.050 * sfreq)))
        #spike_idxs, props = find_peaks( -y, prominence=3e-4, distance=distance, wlen=wlen) #invert y

        #spike_idxs = np.where(abs(y) > threshold)[0]
        #print(spike_idxs)
        # 2) convert to times (in seconds)
        spike_times = spike_idxs / sfreq
        # 1) Make a copy of your signal
        y_clean = y.copy().astype(float)

        
        # 3) Blank out (set to NaN) around each spike
        for idx in spike_idxs:
            start = max(0, idx - half_win)
            end   = min(len(y_clean), idx + half_win)
            y_clean[start:end] = np.nan

        # 4) Interpolate linearly over NaNs
        nans     = np.isnan(y_clean)
        not_nans = ~nans
        y_clean[nans] = np.interp(
            np.flatnonzero(nans),
            np.flatnonzero(not_nans),
            y_clean[not_nans]
        )

        cleaned_data.append(y_clean)

    cleaned_data = np.array(cleaned_data)


    if  raw.get_data().shape == cleaned_data.shape:
        raw._data[: :] = cleaned_data
    else:
        raise ValueError("There is a channel present in your data that is consistently pinning all points. "
                       "Please either remove this channel or consider adjusting your threshold to allow for successful interpolation.")

    return raw, spike_idxs



def read_blackrock(folder, aux_chann, chan_type_map):
    """
    @author: Antonio Franco
    read blackrock ns3 files for eeg

    Parameters
    ----------
    folder : fodler with .ns3
    aux_chann : list
    chan_type_map : dict

    Returns
    -------
    mne raw object
    """
    files     = sorted(glob.glob(os.path.join(folder, '*.ns3')))

    # split into two lists
    hub_files = [f for f in files if os.path.basename(f).lower().startswith('hub')]
    nsp_files = [f for f in files if os.path.basename(f).lower().startswith('nsp')]

    print("Hub files:", hub_files)
    print("NSP files:", nsp_files)

    ######################################################### read & parse Hub
    hub_reader = neo.rawio.BlackrockRawIO(filename=hub_files[0], nsx_to_load=[3])
    hub_reader.parse_header()
    print(hub_reader)

    sig_chs    = hub_reader.header['signal_channels']
    ch_names   = [name.decode() if isinstance(name, bytes) else name for name in sig_chs['name']]
    sfreq      = hub_reader.sig_sampling_rates[3]
    signal_size = hub_reader._get_signal_size(block_index=0, seg_index=0, stream_index=0)

    signals = hub_reader._get_analogsignal_chunk(
        block_index=0,
        seg_index=0,
        i_start=0,
        i_stop=signal_size,
        stream_index=0,
        channel_indexes=None
    )
    data_raw = hub_reader.rescale_signal_raw_to_float(signals, dtype="float64")
    data_raw *= 1e-6     # µV → V so your plot scales sensibly
    basename = os.path.basename(hub_files[0])
    parts    = basename.split('-')
    date_str = parts[1]                           
    time_str = parts[2]                  
    meas_dt  = datetime.datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
    meas_dt  = meas_dt.replace(tzinfo=datetime.timezone.utc)   # ← make UTC-aware


    ch_types = [chan_type_map.get(name, 'eeg') for name in ch_names]
    info = mne.create_info(ch_names=ch_names,
                        sfreq=sfreq,
                        ch_types=ch_types)
    info.set_meas_date(meas_dt)
    raw  = mne.io.RawArray(data_raw.T, info)
    return raw