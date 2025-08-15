#!/usr/bin/env python3
"""Simplified video quality analyzer using VBench."""

import json
import torch
import typing
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from vbench import VBench
except ImportError:
    VBench = None

# Fix PyTorch security issues for model loading
torch.serialization.add_safe_globals([typing.OrderedDict])


class VideoAnalyzer:
    """Simple video quality analyzer using VBench."""

    # All dimensions that support custom_input mode
    VBENCH_DIMENSIONS = [
        "subject_consistency",
        "background_consistency",
        "motion_smoothness",
        "dynamic_degree",
        "aesthetic_quality",
        "imaging_quality",
    ]

    def __init__(self, device: str = "cuda"):
        self.device = device
        self.backends: List[str] = []

    def set_backends(self, backends: Union[str, List[str]]) -> None:
        """Set backends for video analysis. Currently only 'vbench' is supported."""
        if isinstance(backends, str):
            backends = [backends]

        if any(b != "vbench" for b in backends):
            raise ValueError("Only 'vbench' backend is supported")

        if "vbench" in backends and VBench is None:
            raise ImportError("VBench not installed. Run: pip install vbench")

        self.backends = backends

    def analyze(
        self,
        videos_path: Union[str, Path],
        output_path: Union[str, Path],
        dimensions: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """Analyze videos and save results."""
        if not self.backends:
            raise ValueError("No backends set. Call set_backends() first.")

        videos_path = Path(videos_path)
        output_path = Path(output_path)

        if not videos_path.exists():
            raise FileNotFoundError(f"Videos path does not exist: {videos_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if dimensions is None:
            dimensions = self.VBENCH_DIMENSIONS

        # Use simplified VBench approach from working script
        print("Evaluating all supported dimensions...")

        # Initialize VBench
        my_VBench = VBench(
            self.device,
            "VBench_full_info.json",
            str(output_path.parent / "evaluation_results"),
        )

        # Evaluate all dimensions using custom_input mode
        my_VBench.evaluate(
            videos_path=str(videos_path),
            name="complete_evaluation",
            dimension_list=dimensions,
            mode="custom_input",
        )

        print("Complete evaluation finished! Results saved in evaluation_results/")

        # Return empty dict for now - VBench handles the results
        # In the future, we could parse the results from evaluation_results/
        return {}


if __name__ == "__main__":
    """Simple test of the analyzer."""
    analyzer = VideoAnalyzer(device="cuda")
    analyzer.set_backends("vbench")

    analyzer.analyze(
        videos_path="/mirager/example_videos", output_path="./results.json"
    )
