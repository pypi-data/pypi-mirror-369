import os
import numpy as np
import pandas as pd
import h5py
import torch
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from pnpl.datasets.armeni2022.constants import SUBJECTS, SESSIONS, TASKS, TRAIN_SUBJECTS, VALIDATION_SUBJECTS, TEST_SUBJECTS
from pnpl.datasets.utils import check_include_and_exclude_ids, include_exclude_ids
from torch.utils.data import Dataset
import requests
from urllib.parse import urljoin
import zipfile
import mne
import mne_bids
from pathlib import Path


class Armeni2022Base(Dataset):
    # Adjust max_workers as needed.
    _executor = ThreadPoolExecutor(max_workers=4)
    _download_futures = {}
    _lock = threading.Lock()

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
        Base class for Armeni2022 (MEG-MASC) datasets.

        See the dataset on OSF: https://osf.io/ag3kj/files/osfstorage

        Args:
            data_path: Path where you wish to store the dataset. The local dataset structure 
                      will follow the BIDS structure from the MEG-MASC dataset.
            partition: Convenient shortcut to specify train/validation/test split. Use "train", 
                      "validation", or "test". When specified, include/exclude parameters 
                      must be empty. If None, you can manually specify subjects/sessions/tasks.
            preprocessing_str: Preprocessing identifier for different preprocessing pipelines.
                             Default is "default" which corresponds to minimal preprocessing.
            tmin: Start time of the sample in seconds relative to event onset.
            tmax: End time of the sample in seconds relative to event onset.
            include_subjects: List of specific subjects to include (e.g., ['01', '02']).
            exclude_subjects: List of subjects to exclude.
            include_sessions: List of specific sessions to include (e.g., ['0', '1']).
            exclude_sessions: List of sessions to exclude.
            include_tasks: List of task names to include (e.g., ['0', '1', '2', '3']).
            exclude_tasks: List of task names to exclude.
            standardize: Whether to z-score normalize each channel's MEG data using mean and std 
                        computed across all included sessions.
            clipping_boundary: If specified, clips all values to [-clipping_boundary, clipping_boundary]. 
                             Set to None for no clipping.
            channel_means: Pre-computed channel means for standardization. If None and standardize=True, 
                          will be computed from the dataset.
            channel_stds: Pre-computed channel standard deviations for standardization.
            include_info: Whether to include additional info dict in each sample containing dataset name, 
                         subject, session, task, and onset time.
            preload_files: Whether to "eagerly" download all dataset files when the 
                          dataset object is created (True) or "lazily" download files on demand (False).
            download: Whether to download files from OSF if not found locally (True) or 
                     throw an error if files are missing locally (False).

        Returns:
            Data samples with shape (channels, time) where channels=208 MEG channels and time 
            depends on (tmax-tmin)*sfreq.
        """
        os.makedirs(data_path, exist_ok=True)
        self.data_path = data_path
        self.partition = partition
        self.preprocessing_str = preprocessing_str
        self.tmin = tmin
        self.tmax = tmax
        self.include_subjects = include_subjects
        self.exclude_subjects = exclude_subjects
        self.standardize = standardize
        self.clipping_boundary = clipping_boundary
        self.channel_means = channel_means
        self.channel_stds = channel_stds
        self.include_info = include_info
        self.preload_files = preload_files
        self.download = download

        # Define partitions based on MEG-MASC dataset
        if partition is not None:
            if include_subjects or exclude_subjects or include_sessions or exclude_sessions or include_tasks or exclude_tasks:
                raise ValueError(
                    "partition is a shortcut to indicate what data to include. include/exclude parameters must be empty when partition is not None")
            if partition == "train":
                include_subjects = TRAIN_SUBJECTS
            elif partition == "validation":
                include_subjects = VALIDATION_SUBJECTS
            elif partition == "test":
                include_subjects = TEST_SUBJECTS
            else:
                raise ValueError(
                    f"Invalid partition: {partition}. Must be one of: train, validation, test")

        # Convert channel_means and channel_stds to np.ndarray if they are provided as lists.
        if isinstance(channel_means, list):
            self.channel_means = np.array(channel_means)
        if isinstance(channel_stds, list):
            self.channel_stds = np.array(channel_stds)

        check_include_and_exclude_ids(
            include_subjects, exclude_subjects, SUBJECTS)
        check_include_and_exclude_ids(
            include_sessions, exclude_sessions, SESSIONS)
        check_include_and_exclude_ids(
            include_tasks, exclude_tasks, TASKS)

        intended_subjects = include_exclude_ids(
            include_subjects, exclude_subjects, SUBJECTS)
        intended_sessions = include_exclude_ids(
            include_sessions, exclude_sessions, SESSIONS)
        intended_tasks = include_exclude_ids(
            include_tasks, exclude_tasks, TASKS)

        # Create session keys (subject, session, task combinations)
        self.intended_session_keys = []
        for subject in intended_subjects:
            for session in intended_sessions:
                for task in intended_tasks:
                    self.intended_session_keys.append((subject, session, task))

        if len(self.intended_session_keys) == 0:
            raise ValueError(
                f"Your configuration does not allow any session keys to be included. Please check configuration."
            )

        # Preload files if requested
        if self.preload_files and self.download:
            self.prefetch_files()

        # Get sfreq from first available file
        self.sfreq = self._get_sfreq(
            self.intended_session_keys[0][0],
            self.intended_session_keys[0][1],
            self.intended_session_keys[0][2]
        )
        self.points_per_sample = int((tmax - tmin) * self.sfreq)
        self.open_h5_datasets = {}

    def __len__(self):
        return len(self.samples)

    def prefetch_files(self):
        """Preload all required files in parallel."""
        futures = []
        needed_files = set()

        # Collect all file paths that we'll need
        for subject, session, task in self.intended_session_keys:
            # MEG files
            meg_path = self._get_meg_path(subject, session, task)
            if not os.path.exists(meg_path):
                needed_files.add(meg_path)

            # Event files
            events_path = self._get_events_path(subject, session, task)
            if not os.path.exists(events_path):
                needed_files.add(events_path)

        # Schedule downloads for all files that don't exist locally
        for fpath in needed_files:
            futures.append(self._schedule_download(fpath))

        # Wait for all downloads to complete
        if futures:
            print(f"Downloading {len(futures)} files...")
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error downloading a file: {e}")
            print("Done!")

    def _schedule_download(self, fpath):
        """Schedule a file download with retry logic."""
        rel_path = os.path.relpath(fpath, self.data_path)
        os.makedirs(os.path.dirname(fpath), exist_ok=True)

        with Armeni2022Base._lock:
            if fpath not in Armeni2022Base._download_futures:
                Armeni2022Base._download_futures[fpath] = Armeni2022Base._executor.submit(
                    self._download_with_retry,
                    fpath=fpath,
                    rel_path=rel_path
                )
            return Armeni2022Base._download_futures[fpath]

    def _download_with_retry(self, fpath, rel_path, max_retries=5):
        """
        Download a file from OSF with retry logic for handling timeouts.
        Downloads from the MEG-MASC dataset: https://osf.io/ag3kj/files/osfstorage
        """
        last_exception = None
        retries = 0
        
        while retries < max_retries:
            try:
                # Get the file ID from the OSF API based on the file path
                file_id = self._get_osf_file_id(rel_path)
                
                if file_id:
                    # Download using OSF direct download URL
                    download_url = f"https://osf.io/download/{file_id}"
                    print(f"Downloading {os.path.basename(fpath)} from OSF...")
                    
                    response = requests.get(download_url, timeout=60, stream=True)
                    response.raise_for_status()
                    
                    # Write file in chunks to handle large files
                    with open(fpath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"Successfully downloaded {os.path.basename(fpath)}")
                    return fpath
                else:
                    raise FileNotFoundError(f"File {rel_path} not found in OSF project ag3kj")
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
                last_exception = e
                retries += 1
                wait_time = 2 ** retries + random.uniform(0, 1)
                if retries < max_retries:
                    print(f"Network error for {os.path.basename(fpath)}, retrying in {wait_time:.1f}s ({retries}/{max_retries}): {type(e).__name__}")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to download {os.path.basename(fpath)} after {max_retries} network retries")
                    
            except Exception as e:
                last_exception = e
                retries += 1
                wait_time = 2 ** retries + random.uniform(0, 1)
                if retries < max_retries:
                    print(f"Unknown error for {os.path.basename(fpath)}, retrying in {wait_time:.1f}s ({retries}/{max_retries}): {type(e).__name__}")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to download {os.path.basename(fpath)} after {max_retries} attempts: {type(e).__name__}")
        
        # If we've exhausted all retries, raise the last exception
        raise last_exception

    def _get_osf_file_id(self, rel_path):
        """
        Get OSF file ID for a given relative path using the OSF API.
        """
        # MEG-MASC project ID
        project_id = "ag3kj"
        
        try:
            # Get the file structure from OSF API
            if not hasattr(self, '_osf_file_mapping'):
                self._osf_file_mapping = self._build_osf_file_mapping(project_id)
            
            # Try exact match first
            if rel_path in self._osf_file_mapping:
                return self._osf_file_mapping[rel_path]
            
            # Try alternative path formats if exact match fails
            filename = os.path.basename(rel_path)
            
            # Look for the filename anywhere in the project
            for osf_path, file_id in self._osf_file_mapping.items():
                if os.path.basename(osf_path) == filename:
                    print(f"Found {filename} at {osf_path} (expected at {rel_path})")
                    return file_id
            
            # Debug: show available files for this subject if not found
            subject_match = rel_path.split('/')[0] if '/' in rel_path else None
            if subject_match:
                matching_files = [path for path in self._osf_file_mapping.keys() if subject_match in path]
                if matching_files:
                    print(f"Available files for {subject_match}: {matching_files[:5]}...")  # Show first 5
            
            return None
            
        except Exception as e:
            print(f"Error getting file ID for {rel_path}: {e}")
            return None

    def _build_osf_file_mapping(self, project_id):
        """
        Build a mapping from file paths to OSF file IDs by traversing the OSF file structure.
        Uses rate limiting to avoid 429 errors. Caches results to avoid re-downloading.
        """
        cache_file = os.path.join(self.data_path, f".osf_file_mapping_{project_id}.json")
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            try:
                import json
                with open(cache_file, 'r') as f:
                    file_mapping = json.load(f)
                print(f"Loaded cached OSF file mapping with {len(file_mapping)} files")
                return file_mapping
            except Exception as e:
                print(f"Failed to load cache, rebuilding: {e}")
        
        print("Building OSF file mapping from MEG-MASC dataset...")
        
        file_mapping = {}
        
        # Get storage providers for the project
        storage_url = f"https://api.osf.io/v2/nodes/{project_id}/files/"
        
        response = self._make_rate_limited_request(storage_url)
        storage_data = response.json()
        
        # Find OSF Storage provider
        osf_storage = None
        for provider in storage_data['data']:
            if provider['attributes']['name'] == 'osfstorage':
                osf_storage = provider
                break
        
        if not osf_storage:
            raise ValueError("OSF Storage not found for project")
        
        # Recursively traverse the file structure with rate limiting
        storage_files_url = osf_storage['relationships']['files']['links']['related']['href']
        self._traverse_osf_directory_rate_limited(storage_files_url, "", file_mapping)
        
        print(f"Found {len(file_mapping)} files in OSF project")
        
        # Cache the results
        try:
            import json
            with open(cache_file, 'w') as f:
                json.dump(file_mapping, f, indent=2)
            print(f"Cached file mapping to {cache_file}")
        except Exception as e:
            print(f"Failed to cache file mapping: {e}")
        
        return file_mapping

    def _make_rate_limited_request(self, url, max_retries=5):
        """
        Make an HTTP request with rate limiting and retry logic.
        """
        retries = 0
        while retries < max_retries:
            try:
                # Add a small delay between requests to avoid rate limiting
                time.sleep(0.5)  # 500ms delay
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 429:
                    # Rate limited, wait longer
                    wait_time = 2 ** (retries + 1) + random.uniform(0, 1)
                    print(f"Rate limited, waiting {wait_time:.1f}s before retry...")
                    time.sleep(wait_time)
                    retries += 1
                    continue
                    
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries < max_retries:
                    wait_time = 2 ** retries + random.uniform(0, 1)
                    print(f"Request failed, retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise Exception(f"Failed to make request after {max_retries} attempts")

    def _traverse_osf_directory_rate_limited(self, url, current_path, file_mapping):
        """
        Recursively traverse OSF directory structure to build file mapping with rate limiting.
        """
        try:
            response = self._make_rate_limited_request(url)
            data = response.json()
            
            for item in data['data']:
                name = item['attributes']['name']
                item_path = os.path.join(current_path, name).replace('\\', '/') if current_path else name
                
                if item['attributes']['kind'] == 'file':
                    # Extract file ID from download link
                    download_link = item['links']['download']
                    # Download link format: https://files.osf.io/v1/resources/{project_id}/providers/osfstorage/{file_id}
                    file_id = download_link.split('/')[-1]
                    file_mapping[item_path] = file_id
                    
                elif item['attributes']['kind'] == 'folder':
                    # Recursively traverse subdirectory with rate limiting
                    folder_url = item['relationships']['files']['links']['related']['href']
                    self._traverse_osf_directory_rate_limited(folder_url, item_path, file_mapping)
            
            # Handle pagination if present
            if 'next' in data['links'] and data['links']['next']:
                self._traverse_osf_directory_rate_limited(data['links']['next'], current_path, file_mapping)
                
        except Exception as e:
            print(f"Error traversing directory {url}: {e}")
            return

    def _ensure_file(self, fpath: str) -> str:
        """
        Ensures the file exists locally, downloading if needed.
        This is a blocking call that waits for download to complete.
        """
        if os.path.exists(fpath):
            return fpath

        if not self.download:
            raise FileNotFoundError(f"File not found: {fpath}. Download is disabled.")

        future = self._schedule_download(fpath)
        # Wait for the download to complete
        return future.result()

    def _get_meg_path(self, subject: str, session: str, task: str) -> str:
        """
        Gets the path to the MEG file following BIDS structure.
        """
        subject_id = f"sub-{subject.zfill(2)}"
        session_id = f"ses-{session}"
        task_id = f"task-{task}"
        
        fname = f"{subject_id}_{session_id}_{task_id}_meg.fif"
        return os.path.join(self.data_path, subject_id, session_id, "meg", fname)

    def _get_events_path(self, subject: str, session: str, task: str) -> str:
        """
        Gets the path to the events file following BIDS structure.
        """
        subject_id = f"sub-{subject.zfill(2)}"
        session_id = f"ses-{session}"
        task_id = f"task-{task}"
        
        fname = f"{subject_id}_{session_id}_{task_id}_events.tsv"
        return os.path.join(self.data_path, subject_id, session_id, "meg", fname)

    def _ids_to_meg_path(self, subject: str, session: str, task: str) -> str:
        """
        Gets the path to the MEG file and ensures it exists.
        """
        path = self._get_meg_path(subject, session, task)
        return self._ensure_file(path)

    def _get_sfreq(self, subject, session, task):
        """
        Get sampling frequency from MEG file.
        """
        meg_path = self._ids_to_meg_path(subject, session, task)
        
        # Read using MNE-Python
        raw = mne.io.read_raw_fif(meg_path, preload=False, verbose=False)
        sfreq = raw.info['sfreq']
        return sfreq

    def _load_events(self, subject: str, session: str, task: str):
        """
        Load events file for a given subject, session, and task.
        """
        fpath = self._get_events_path(subject, session, task)
        fpath = self._ensure_file(fpath)
        events_df = pd.read_csv(fpath, sep="\t")
        return events_df

    def _calculate_standardization_params(self):
        """
        Calculate channel-wise means and standard deviations across all intended sessions.
        """
        n_samples = []
        means = []
        stds = []
        
        for subject, session, task in self.intended_session_keys:
            try:
                meg_path = self._ids_to_meg_path(subject, session, task)
                
                # Read MEG data
                raw = mne.io.read_raw_fif(meg_path, preload=True, verbose=False)
                data = raw.get_data()  # channels x time
                
                channel_means = np.mean(data, axis=1)
                channel_stds = np.std(data, axis=1)
                
                n_samples.append(data.shape[1])
                means.append(channel_means)
                stds.append(channel_stds)
                
                print(f"Calculated stats for: {subject}, {session}, {task}")
                
            except Exception as e:
                print(f"Error processing {subject}, {session}, {task}: {e}")
                continue
        
        if not means:
            raise ValueError("No valid data found for standardization")
            
        means = np.array(means)
        stds = np.array(stds)
        n_samples = np.array(n_samples)
        
        self.channel_stds, self.channel_means = self._accumulate_stds(
            means, stds, n_samples)
        self.broadcasted_stds = np.tile(
            self.channel_stds, (self.points_per_sample, 1)).T
        self.broadcasted_means = np.tile(
            self.channel_means, (self.points_per_sample, 1)).T

    @staticmethod
    def _accumulate_stds(ch_means, ch_stds, n_samples):
        """
        Accumulate standard deviations across multiple sessions.
        
        ch_means: np.ndarray (n_groups, n_channels)
        ch_stds: np.ndarray (n_groups, n_channels)
        n_samples: np.ndarray (n_groups)
        """
        vars = np.array(ch_stds) ** 2
        means_total = np.average(ch_means, axis=0, weights=n_samples)
        sum_of_squares_within = np.sum(
            vars * np.tile(n_samples, (vars.shape[1], 1)).T, axis=0)
        sum_of_squares_between = np.sum(
            (ch_means - np.tile(means_total, (ch_means.shape[0], 1))) ** 2 *
            np.tile(n_samples, (ch_means.shape[1], 1)).T,
            axis=0
        )
        sum_of_squares_total = sum_of_squares_within + sum_of_squares_between
        return np.sqrt(sum_of_squares_total / np.sum(n_samples)), means_total

    def _clip_sample(self, sample, boundary):
        """Clip sample values to [-boundary, boundary]."""
        sample = np.clip(sample, -boundary, boundary)
        return sample

    def __getitem__(self, idx):
        """
        Returns a sample: [data, label, info] where data has shape (channels, time)
        """
        if idx >= len(self.samples):
            raise IndexError(
                f"Index {idx} is out of bounds for dataset of size {len(self.samples)}"
            )
        
        sample = self.samples[idx]
        subject, session, task, onset, label = sample
        
        if self.include_info:
            info = {
                "dataset": "armeni2022",
                "subject": subject,
                "session": session,
                "task": task,
                "onset": torch.tensor(onset, dtype=torch.float32),
            }

        # Get MEG data
        if (subject, session, task) not in self.open_h5_datasets:
            meg_path = self._ids_to_meg_path(subject, session, task)
            raw = mne.io.read_raw_fif(meg_path, preload=True, verbose=False)
            data_full = raw.get_data()  # channels x time
            self.open_h5_datasets[(subject, session, task)] = data_full
        else:
            data_full = self.open_h5_datasets[(subject, session, task)]

        # Extract time window
        start = max(0, int((onset + self.tmin) * self.sfreq))
        end = start + self.points_per_sample
        data = data_full[:, start:end]

        # Handle case where data is shorter than expected
        if data.shape[1] < self.points_per_sample:
            # Pad with zeros
            padding = self.points_per_sample - data.shape[1]
            data = np.pad(data, ((0, 0), (0, padding)), mode='constant')

        if self.standardize:
            # for the edge case in which the last samples are smaller than points_per_sample,
            if data.shape[1] < self.broadcasted_means.shape[1]:
                self.broadcasted_means = self.broadcasted_means[:, 0:data.shape[1]]
                self.broadcasted_stds = self.broadcasted_stds[:, 0:data.shape[1]]

            data = (data - self.broadcasted_means) / self.broadcasted_stds

        if self.clipping_boundary is not None:
            data = self._clip_sample(data, self.clipping_boundary)

        if self.include_info:
            return [torch.tensor(data, dtype=torch.float32), label, info]
        return [torch.tensor(data, dtype=torch.float32), label, {}] 