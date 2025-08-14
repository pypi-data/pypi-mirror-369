# 🍍PNPL Brain Data Deep Learning Library

> The current primary use of the PNPL library is for the LibriBrain competition. [Click here](https://neural-processing-lab.github.io/2025-libribrain-competition/) to learn more and get started!

## Installation
```
pip install pnpl
```

This will also take care of all requirements.

## Usage
The core functionality of the library is contained in the two Dataset classes `LibriBrainSpeech` and `LibriBrainPhoneme`.
Check out the basic usage:

### LibriBrainSpeech
This wraps the LibriBrain dataset for use in speech detection problems.
```python
from pnpl.datasets import LibriBrainSpeech

speech_example_data = LibriBrainSpeech(
    data_path="./data/",
    include_run_keys = [("0","1","Sherlock1","1")]
)

sample_data, label = speech_example_data[0]

# Print out some basic info about the sample
print("Sample data shape:", sample_data.shape)
print("Label shape:", label.shape)
```

### LibriBrainSpeech
This wraps the LibriBrain dataset for use in phoneme classification problems.
```python
from pnpl.datasets import LibriBrainPhoneme

phoneme_example_data = LibriBrainPhoneme(
    data_path="./data/",
    include_run_keys = [("0","1","Sherlock1","1")]
)

sample_data, label = phoneme_example_data[0]

# Print out some basic info about the sample
print("Sample data shape:", sample_data.shape)
print("Label shape:", label.shape)
```

## Support
In case of any questions or problems, please get in touch through [our Discord server](https://discord.gg/Fqr8gJnvSh).