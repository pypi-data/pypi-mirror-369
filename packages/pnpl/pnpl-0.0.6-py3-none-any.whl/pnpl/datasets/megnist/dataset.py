import os
import warnings

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset


class MegNISTDataset(Dataset):
    """PyTorch `Dataset` for MegNIST HDF5 files (train/val/test splits).

    The MegNIST files are expected to have the following structure::

        train.h5 / val.h5 / test.h5
            ├── "X": float32 dataset of shape (n_trials, n_channels, n_times)
            └── "y": int64   dataset of shape (n_trials,)
            └── "times"  (optional): float64 dataset of time points (n_times,)

    Parameters
    ----------
    data_path : str
        Directory that contains the ``*.h5`` files.  By default we look for
        ``MegNIST1/derivatives`` inside the current working directory.
    split : {"train", "val", "test"}
        Which split file to load.  ``val``/``test`` files are optional and will
        only be accessed if present.
    standardize : bool, default True
        If ``True`` each channel will be z-scored using the *per-channel* mean
        and standard deviation computed across the entire split.
    clipping_boundary : float | None, default 10.0
        Clip the signal to the range ``[-clipping_boundary, clipping_boundary]``
        *after* standardization.  Pass ``None`` to disable clipping.
    include_info : bool, default False
        If ``True`` the ``__getitem__`` call will also return an ``info`` dict
        with the keys ``{"dataset", "index"}``.
    batch_size_stats : int, default 100
        Batch size used when iterating through the file to compute channel
        statistics.  Increase if you have plenty of RAM to speed things up.
    """

    def __init__(
        self,
        data_path: str = "MegNIST1/derivatives",
        split: str = "train",
        standardize: bool = True,
        clipping_boundary: float | None = 10.0,
        include_info: bool = False,
        batch_size_stats: int = 100,
    ) -> None:
        super().__init__()

        if split not in {"train", "val", "test"}:
            raise ValueError(f"Invalid split '{split}'. Must be 'train', 'val', or 'test'.")

        self.data_path = data_path
        self.split = split
        self.standardize = standardize
        self.clipping_boundary = clipping_boundary
        self.include_info = include_info
        self.batch_size_stats = batch_size_stats

        # ------------------------------------------------------------------
        # Open the HDF5 file and keep the handle around for efficient access.
        # ------------------------------------------------------------------
        self.filepath = os.path.join(self.data_path, f"{split}.h5")
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"MegNIST file for split '{split}' not found at: {self.filepath}"
            )

        # We keep the file handle open in read-only mode for the lifetime of the Dataset.
        self._h5file = h5py.File(self.filepath, "r")
        self._X_ds = self._h5file["X"]  # shape (n_trials, n_channels, n_times)
        self._y = self._h5file["y"][:]   # load labels fully into memory (usually small)

        # Cache useful shapes
        self.n_trials, self.n_channels, self.n_times = self._X_ds.shape

        # ------------------------------------------------------------------
        # Compute (or retrieve) per-channel mean/std for optional z-scoring.
        # ------------------------------------------------------------------
        if standardize:
            if "channel_means" in self._X_ds.attrs and "channel_stds" in self._X_ds.attrs:
                self.channel_means = self._X_ds.attrs["channel_means"].astype(np.float64)
                self.channel_stds = self._X_ds.attrs["channel_stds"].astype(np.float64)
            else:
                self.channel_means, self.channel_stds = self._compute_channel_stats()
                # Try to save them back for next time (requires reopening in r+)
                try:
                    self._h5file.close()
                    with h5py.File(self.filepath, "r+") as f:
                        f["X"].attrs["channel_means"] = self.channel_means
                        f["X"].attrs["channel_stds"] = self.channel_stds
                    # Re-open read-only file handle for continued use
                    self._h5file = h5py.File(self.filepath, "r")
                    self._X_ds = self._h5file["X"]
                except Exception as e:
                    warnings.warn(
                        f"Could not cache channel statistics inside the HDF5 file: {e}."
                    )
            # Broadcast so that we can vectorise standardisation per sample
            self._broadcast_means = np.tile(self.channel_means[:, None], (1, self.n_times))
            self._broadcast_stds = np.tile(self.channel_stds[:, None], (1, self.n_times))
        else:
            self.channel_means = None
            self.channel_stds = None
            self._broadcast_means = None
            self._broadcast_stds = None

    # ------------------------------------------------------------------
    # Mandatory PyTorch Dataset protocol methods
    # ------------------------------------------------------------------
    def __len__(self):
        return self.n_trials

    def __getitem__(self, idx: int):
        if idx >= self.n_trials or idx < 0:
            raise IndexError(f"Index {idx} is out of bounds for dataset of size {self.n_trials}.")

        sample = self._X_ds[idx]  # (channels, time)
        label = int(self._y[idx])

        if self.standardize:
            sample = (sample - self._broadcast_means) / self._broadcast_stds

        if self.clipping_boundary is not None:
            sample = np.clip(sample, -self.clipping_boundary, self.clipping_boundary)

        data_tensor = torch.tensor(sample, dtype=torch.float32)
        label_tensor = torch.tensor(label, dtype=torch.long)

        if self.include_info:
            info = {"dataset": "MegNIST", "index": idx}
            return [data_tensor, label_tensor, info]
        return [data_tensor, label_tensor]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _compute_channel_stats(self):
        """Compute per-channel mean and std without loading the full dataset."""
        total_sum = np.zeros(self.n_channels, dtype=np.float64)
        total_sum_sq = np.zeros(self.n_channels, dtype=np.float64)
        total_count = 0

        for start in range(0, self.n_trials, self.batch_size_stats):
            end = min(start + self.batch_size_stats, self.n_trials)
            batch = self._X_ds[start:end].astype(np.float64)  # (batch, ch, time)
            # Aggregate across batch and time dimensions -> per channel
            total_sum += batch.sum(axis=(0, 2))
            total_sum_sq += np.square(batch).sum(axis=(0, 2))
            total_count += batch.shape[0] * self.n_times

        means = total_sum / total_count
        variances = total_sum_sq / total_count - means ** 2
        stds = np.sqrt(variances)

        return means.astype(np.float32), stds.astype(np.float32)

    # ------------------------------------------------------------------
    # Clean-up
    # ------------------------------------------------------------------
    def __del__(self):
        try:
            self._h5file.close()
        except Exception:
            pass 