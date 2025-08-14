import os
import warnings
import numpy as np
import pandas as pd
import torch
from pnpl.datasets.armeni2022.base import Armeni2022Base
from pnpl.datasets.constants import ARPABET


class Armeni2022Phoneme(Armeni2022Base):

    def __init__(
        self,
        data_path: str,
        partition: str | None = None,
        preprocessing_str: str | None = "default",
        tmin: float = -0.2,
        tmax: float = 0.6,
        include_subjects: list[str] = [],
        exclude_subjects: list[str] = [],
        include_sessions: list[str] = [],
        exclude_sessions: list[str] = [],
        include_tasks: list[str] = [],
        exclude_tasks: list[str] = [],
        standardize: bool = True,
        clipping_boundary: float | None = 10,
        channel_means: np.ndarray | None = None,
        channel_stds: np.ndarray | None = None,
        include_info: bool = False,
        preload_files: bool = True,
        download: bool = True
    ):
        """
        Armeni2022 phoneme classification dataset (MEG-MASC).

        This dataset provides MEG data segmented around phoneme onsets for phoneme classification.
        The dataset is based on the MEG-MASC dataset where participants listened to stories.

        Args:
            data_path: Path where you wish to store the dataset. The local dataset structure 
                      will follow the BIDS structure from the MEG-MASC dataset:
                      ```
                      data_path/
                      ├── sub-{subject}/
                      │   └── ses-{session}/
                      │       └── meg/
                      │           ├── sub-{subject}_ses-{session}_task-{task}_meg.fif
                      │           └── sub-{subject}_ses-{session}_task-{task}_events.tsv
                      ```
            partition: Convenient shortcut to specify train/validation/test split. Use "train", 
                      "validation", or "test". Instead of specifying subjects manually, you can use:
                      - partition="train": Subjects 01-23
                      - partition="validation": Subjects 24-25  
                      - partition="test": Subjects 26-27
            preprocessing_str: Preprocessing identifier for different preprocessing pipelines.
                             Default is "default" which corresponds to minimal preprocessing.
            tmin: Start time of the sample in seconds relative to phoneme onset.
            tmax: End time of the sample in seconds relative to phoneme onset.
            include_subjects: List of specific subjects to include (e.g., ['01', '02']).
            exclude_subjects: List of subjects to exclude.
            include_sessions: List of specific sessions to include (e.g., ['0', '1']).
            exclude_sessions: List of sessions to exclude.
            include_tasks: List of task names to include (e.g., ['0', '1', '2', '3']).
            exclude_tasks: List of task names to exclude.
            standardize: Whether to z-score normalize each channel's MEG data using mean and std 
                        computed across all included sessions.
            clipping_boundary: If specified, clips all values to [-clipping_boundary, clipping_boundary]. 
                             This can help with outliers. Set to None for no clipping.
            channel_means: Pre-computed channel means for standardization. If provided along with 
                          channel_stds, these will be used instead of computing from the dataset.
            channel_stds: Pre-computed channel standard deviations for standardization.
            include_info: Whether to include additional info dict in each sample containing dataset name, 
                         subject, session, task, and onset time of the sample.
            preload_files: Whether to "eagerly" download all dataset files when 
                          the dataset object is created (True) or "lazily" download files on demand (False).
            download: Whether to download files from OSF if not found locally (True) or 
                     throw an error if files are missing locally (False).

        Returns:
            Data samples with shape (channels, time) where channels=208 MEG channels.
            Labels are integers corresponding to phoneme classes.
        """
        super().__init__(
            data_path=data_path,
            partition=partition,
            preprocessing_str=preprocessing_str,
            tmin=tmin,
            tmax=tmax,
            include_subjects=include_subjects,
            exclude_subjects=exclude_subjects,
            include_sessions=include_sessions,
            exclude_sessions=exclude_sessions,
            include_tasks=include_tasks,
            exclude_tasks=exclude_tasks,
            standardize=standardize,
            clipping_boundary=clipping_boundary,
            channel_means=channel_means,
            channel_stds=channel_stds,
            include_info=include_info,
            preload_files=preload_files,
            download=download
        )

        if not os.path.exists(data_path):
            raise ValueError(f"Path {data_path} does not exist.")

        self.samples = []
        session_keys_missing = []
        self.session_keys = []
        
        for session_key in self.intended_session_keys:
            try:
                subject, session, task = session_key
                phonemes, onsets = self.get_phonemes_for_session(subject, session, task)
                self._collect_phoneme_samples(subject, session, task, phonemes, onsets)
                self.session_keys.append(session_key)
            except FileNotFoundError:
                session_keys_missing.append(session_key)
                warnings.warn(f"File not found for session key {session_key}. Skipping")
                continue

        if len(session_keys_missing) > 0:
            warnings.warn(
                f"Session keys {session_keys_missing} not found in dataset. Present session keys: {self.session_keys}")

        if len(self.samples) == 0:
            raise ValueError("No samples found.")

        # Set up phoneme labels
        self.phoneme_labels = self._get_unique_phonemes()
        self.phoneme_to_id = {label: i for i, label in enumerate(self.phoneme_labels)}
        self.id_to_phoneme = self.phoneme_labels

        if (self.standardize and channel_means is None and channel_stds is None):
            self._calculate_standardization_params()
        elif (self.standardize and (channel_means is not None and channel_stds is not None)):
            self.channel_means = channel_means
            self.channel_stds = channel_stds
            self.broadcasted_stds = np.tile(
                self.channel_stds, (self.points_per_sample, 1)).T
            self.broadcasted_means = np.tile(
                self.channel_means, (self.points_per_sample, 1)).T

    def get_phonemes_for_session(self, subject, session, task):
        """
        Extract phonemes and their onset times from the events file.
        """
        df = self._load_events(subject, session, task)
        
        # Filter for phoneme events (this depends on the actual structure of the MEG-MASC events)
        # The MEG-MASC dataset has detailed phoneme annotations
        phoneme_events = df[df['description'].str.contains('phoneme', na=False)]
        
        phonemes = []
        onsets = []
        
        for _, event in phoneme_events.iterrows():
            # Extract phoneme from description (format may vary)
            # This is a simplified extraction - you may need to adjust based on actual format
            description = event['description']
            if 'phoneme' in description:
                # Parse phoneme from description
                phoneme = self._parse_phoneme_from_description(description)
                if phoneme and phoneme in ARPABET:
                    onset = float(event['onset'])
                    phonemes.append(phoneme)
                    onsets.append(onset)

        return phonemes, onsets

    def _parse_phoneme_from_description(self, description):
        """
        Parse phoneme from event description.
        This is a placeholder - you'll need to implement based on actual MEG-MASC format.
        """
        # This is a simplified parser
        # The actual implementation would depend on the MEG-MASC event format
        try:
            # Try to extract phoneme symbol from description
            # Format might be something like: "{'phoneme': 'AH', 'word': 'the', ...}"
            import ast
            desc_dict = ast.literal_eval(description)
            if 'phoneme' in desc_dict:
                return desc_dict['phoneme']
        except:
            # Fallback for simple formats
            if 'phoneme:' in description:
                parts = description.split('phoneme:')
                if len(parts) > 1:
                    return parts[1].strip().split()[0]
        
        return None

    def _collect_phoneme_samples(self, subject, session, task, phonemes, onsets):
        """
        Collect samples for each phoneme onset.
        """
        for phoneme, onset in zip(phonemes, onsets):
            self.samples.append((subject, session, task, onset, phoneme))

    def _get_unique_phonemes(self):
        """
        Get unique phonemes from all samples.
        """
        phonemes = set()
        for sample in self.samples:
            phonemes.add(sample[4])  # phoneme is the 5th element
        
        phoneme_list = list(phonemes)
        phoneme_list.sort()
        return phoneme_list

    def __getitem__(self, idx):
        """
        Returns a sample: [data, phoneme_id, info] where data has shape (channels, time)
        """
        data, phoneme, info = super().__getitem__(idx)
        
        # Convert phoneme to ID
        phoneme_id = self.phoneme_to_id[phoneme]
        
        if self.include_info:
            return [data, torch.tensor(phoneme_id, dtype=torch.long), info]
        return [data, torch.tensor(phoneme_id, dtype=torch.long)]


if __name__ == "__main__":
    import time

    start_time = time.time()
    dataset = Armeni2022Phoneme(
        data_path="./armeni2022_data",
        partition="train",
        standardize=True,
        tmin=-0.2,
        tmax=0.6,
        download=False  # Set to True to download from OSF
    )
    
    print(f"Dataset loaded with {len(dataset)} samples")
    print(f"Available phonemes: {dataset.phoneme_labels}")
    print(f"Number of phoneme classes: {len(dataset.phoneme_labels)}")
    
    if len(dataset) > 0:
        data, label = dataset[0]
        print(f"Sample shape: {data.shape}")
        print(f"Sample label: {label}")
    
    loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Test loading a batch
    if len(dataset) > 0:
        batch = next(iter(loader))
        print(f"Batch data shape: {batch[0].shape}")
        print(f"Batch labels shape: {batch[1].shape}") 