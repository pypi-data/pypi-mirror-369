# B10 Video Benchmark

Simple video quality analysis using VBench.

## Installation

```bash
pip install b10-vidbench[vbench]
```

## Usage

```python
from b10_vidbench import VideoAnalyzer

analyzer = VideoAnalyzer(device="cuda")  # or "cpu"
analyzer.set_backends("vbench")

results = analyzer.analyze(
    videos_path="./videos",
    output_path="./results.json"
)
```

## API

### VideoAnalyzer(device="cuda")
- `set_backends(backends)` - Set backend ("vbench")
- `analyze(videos_path, output_path, dimensions=None)` - Analyze videos

### Available Dimensions
- aesthetic_quality, motion_smoothness, subject_consistency
- temporal_flickering, dynamic_degree, imaging_quality
- object_class, multiple_objects, human_action, color
- spatial_relationship, scene, temporal_style, appearance_style
- background_consistency, overall_consistency

## Output Format

```json
{
  "video1": {"aesthetic_quality": 0.85, "motion_smoothness": 0.72},
  "video2": {"aesthetic_quality": 0.78, "motion_smoothness": 0.68}
}
```
