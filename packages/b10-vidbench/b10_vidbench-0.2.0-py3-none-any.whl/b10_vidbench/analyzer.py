"""Video quality analyzer using VBench."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from vbench import VBench
except ImportError:
    VBench = None


class VideoAnalyzer:
    """Simple video quality analyzer using VBench."""

    VBENCH_DIMENSIONS = [
        "subject_consistency",
        "background_consistency",
        "temporal_flickering",
        "motion_smoothness",
        "dynamic_degree",
        "aesthetic_quality",
        "imaging_quality",
        "object_class",
        "multiple_objects",
        "human_action",
        "color",
        "spatial_relationship",
        "scene",
        "temporal_style",
        "appearance_style",
        "overall_consistency",
    ]

    def __init__(self, device: str = "cuda"):
        self.device = device
        self.backends: List[str] = []
        self._vbench_instance: Optional[VBench] = None

    def set_backends(
        self, backends: Union[str, List[str]], skip_import_check: bool = False
    ) -> None:
        """Set backends for video analysis. Currently only 'vbench' is supported."""
        if isinstance(backends, str):
            backends = [backends]

        if any(b != "vbench" for b in backends):
            raise ValueError("Only 'vbench' backend is supported")

        if "vbench" in backends and VBench is None and not skip_import_check:
            raise ImportError("VBench not installed. Run: pip install vbench")

        self.backends = backends

    def _initialize_vbench(self, save_dir: str) -> VBench:
        """Initialize VBench instance."""
        if VBench is None:
            raise ImportError("VBench not installed. Run: pip install vbench")

        if self._vbench_instance is None:
            # Create minimal config
            config_path = os.path.join(save_dir, "VBench_full_info.json")
            os.makedirs(save_dir, exist_ok=True)

            config = {"dimension_map": {dim: dim for dim in self.VBENCH_DIMENSIONS}}
            with open(config_path, "w") as f:
                json.dump(config, f)

            self._vbench_instance = VBench(self.device, config_path, save_dir)

        return self._vbench_instance

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

        video_files = list(videos_path.glob("*.mp4"))
        if not video_files:
            raise ValueError(f"No MP4 files found in {videos_path}")

        results = self._analyze_with_vbench(videos_path, output_path, dimensions)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        return results

    def _analyze_with_vbench(
        self,
        videos_path: Path,
        output_path: Path,
        dimensions: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """Analyze videos using VBench."""
        if dimensions is None:
            dimensions = self.VBENCH_DIMENSIONS

        invalid_dims = set(dimensions) - set(self.VBENCH_DIMENSIONS)
        if invalid_dims:
            raise ValueError(f"Invalid dimensions: {invalid_dims}")

        temp_dir = output_path.parent / "vbench_temp"
        temp_dir.mkdir(exist_ok=True)

        try:
            vbench = self._initialize_vbench(str(temp_dir))
            vbench.evaluate(
                videos_path=str(videos_path), name="analysis", dimension_list=dimensions
            )

            # Parse results
            results = {}
            for video_file in videos_path.glob("*.mp4"):
                video_name = video_file.stem
                results[video_name] = {}

                for dimension in dimensions:
                    result_file = temp_dir / "analysis" / f"{dimension}.json"
                    if result_file.exists():
                        try:
                            with open(result_file, "r") as f:
                                data = json.load(f)

                            # Extract score (handle various formats)
                            score = None
                            if isinstance(data, dict):
                                score = data.get(video_name) or data.get(
                                    f"{video_name}.mp4"
                                )
                                if score is None:
                                    # Find first numeric value
                                    for v in data.values():
                                        if isinstance(v, (int, float)):
                                            score = v
                                            break
                            elif isinstance(data, (int, float)):
                                score = data

                            results[video_name][dimension] = score
                        except Exception as e:
                            print(
                                f"Warning: Could not parse {dimension} for {video_name}: {e}"
                            )
                            results[video_name][dimension] = None

            return results

        finally:
            import shutil

            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
