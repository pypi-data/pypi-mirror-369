"""FeatureExtractor for music21 features."""
import logging

import numpy as np
from music21.features.base import allFeaturesAsList, extractorsById

from .feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

categorical_features = {
    "R31_1": (0, 1, 2, 4, 8, 16, 32, 64, 128), # InitialTimeSignatureFeature (denom)
    "P6_0": tuple(range(12)), # IntervalBetweenStrongestPitchClassesFeature
    "P9_0": tuple(range(13)), # PitchClassVarietyFeature
    "P16_0": tuple(range(12)) # MostCommonPitchClassFeature
}

feats2del = ["TX1_0"]

class Music21Extractor(FeatureExtractor):
    """FeatureExtractor Subclass for extracting music21 features from MIDI files."""
    def __init__(
        self,
        extractor_name: str = "music21",
        fast: bool = True,
        preprocess_features: bool = True,
    ) -> None:
        """Initialize the Music21Extractor class.

        Args:
            extractor_name (str): Name of the feature extractor.
                Must be unique to identify this extractor in benchmark results.
            fast (bool, optional): If True, enables multiprocessing to extract features
                from multiple files in parallel for improved performance.
                Defaults to False.
            preprocess_features (bool, optional): If True, features will be preprocessed
                according to the AutoML configuration before being used in tasks.
                If False, raw extracted features are used without modification.
                Defaults to True.
        """
        super().__init__(extractor_name, fast, preprocess_features)

    def extract_features_from_file(
        self,
        file: str
    ) -> np.ndarray:
        """Extract music21-based features from a MIDI file.

        Args:
            file (str): Relative or absolute path to the MIDI file.

        Returns:
            np.ndarray: 1D numpy array of shape (n_features,)
                containing the extracted music21 features.

        Raises:
            ValueError: If the file cannot be parsed or feature extraction fails.
        """
        try:
            features = allFeaturesAsList(file)
        except Exception as e:  # noqa: BLE001
            log_msg = f"Cannot extract features from file {file}. {e}"
            msg = f"Exception during feature extraction: {e}"
            logger.error(log_msg)
            raise ValueError(msg) from None
        columns = [x.id for x in extractorsById("all")]
        unique_feats = {
            (columns[outer] + f"_{i}"): f
            for outer in range(len(columns))
            for i, f in enumerate(features[outer])
        }

        # OHE for categorical features
        for feat in categorical_features:
            value = unique_feats[feat]
            del unique_feats[feat]
            for cat in categorical_features[feat]:
                unique_feats[f"{feat}_{cat}"] = 0 if cat != value else 1

        # delete text features
        for feat in feats2del:
            del unique_feats[feat]

        return np.array(list(unique_feats.values()))
