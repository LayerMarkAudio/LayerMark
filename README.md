# LayerMark

Multi-message audio watermarking with feature overlap-aware embedding and recursive detection.

[Project page](https://layermarkaudio.github.io/) | [Manuscript](assets/paper/layermark.pdf)

## Release scope

This is a partial code and demonstration release. It contains the project website,
real sequentially watermarked audio examples, a standalone audio evaluation
utility, and the paper-level implementations of the Multi-Layer Adapter,
Multi-Layer Remover, NMAE objective, and one recursive removal step.

The released modules expose the architecture described in Sections 3.2-3.4 of
the manuscript. The AudioSeal Generator and Detector, trained LayerMark weights,
dataset preparation, distortion pipeline, and full training/evaluation runner are
not redistributed here. Consequently, this repository documents the method and
supports architecture inspection, but it does not reproduce the paper results
without the authors' checkpoints and the upstream AudioSeal components.

## Listen to the examples

Open the project page or run locally:

```bash
python3 -m http.server 4173
```

Visit http://localhost:4173. The page includes three source utterances and their
LayerMark outputs after one, two, and three sequential embeddings. The listening
comparison uses the same source utterance with Timbre, AudioSeal, WavMark, and
LayerMark. Payload lengths and message values vary by method.

The website examples are demo exports from one trained checkpoint. Their SNR
values are per-clip measurements, not dataset averages. Detection values in the
results table are reported separately under the manuscript evaluation protocol.
The earlier illustrative L1-L7 curve containing estimated values is not included.

## Evaluate the released audio

Python 3.10+ is sufficient; this utility uses only the standard library.

```bash
python3 evaluate_audio.py assets/audio/sample-a-original.wav \
  assets/audio/sample-a-l1.wav assets/audio/sample-a-l2.wav assets/audio/sample-a-l3.wav
```

It reads mono 16-bit PCM WAV files, checks matching sample rates and lengths,
and reports SNR and mean absolute error against the original signal. SNR is
computed from the distributed, quantized WAV files, so it may differ slightly
from values measured before the files were saved. It also reports duration,
peak magnitude, and full-scale sample fraction as diagnostics.

## Inspect the released method components

Install PyTorch and run the focused tests:

```bash
python3 -m pip install -r requirements-code.txt
python3 -m unittest discover -s tests -v
```

The public API mirrors the notation used in the manuscript:

```python
from layermark import MultiLayerAdapter, MultiLayerRemover, remove_current_layer

adapter = MultiLayerAdapter()  # A_omega: 6 blocks, 24 channels
remover = MultiLayerRemover()  # R_theta: 8 blocks, 32 channels

adjusted_feature = adapter(new_feature, previous_feature)
previous_audio, estimate = remove_current_layer(
    remover,
    current_audio,
    reconstructed_feature,
)
```

`new_feature`, `previous_feature`, `current_audio`, and
`reconstructed_feature` are mono tensors with shape `[batch, 1, frames]`.

## Files

- `index.html`, `styles.css`, `app.js`: static website and audio players.
- `evaluate_audio.py`: standalone WAV quality evaluation.
- `layermark/models.py`: Multi-Layer Adapter and Multi-Layer Remover.
- `layermark/objectives.py`: normalized mean absolute error used by the paper.
- `layermark/recursive_detection.py`: one recursive feature-removal step.
- `tests/`: focused shape, architecture, and objective tests.
- `assets/audio/`: original and watermarked listening samples.
- `assets/images/`: method overview.
- `assets/paper/`: manuscript.

## Attribution

AudioSeal, Timbre, and WavMark are third-party baseline methods; their model code
and checkpoints are not redistributed here. Their original licenses continue to
apply to those projects. Lucide icons are included under the ISC license in
`assets/lucide-LICENSE`. Visual layout was informed by the
[PhysWave project page](https://lingfengyao.github.io/PhysWave/).

The manuscript and audio assets are not covered by the Lucide license. A project
code license has not yet been selected by the authors; until one is added, the
released source is available for inspection but no reuse license is granted.
