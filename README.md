# LayerMark

Multi-message audio watermarking with feature overlap-aware embedding and recursive detection.

[Project page](https://layermarkaudio.github.io/) | [Manuscript](assets/paper/layermark.pdf)

## Release scope

This is a partial code and demonstration release. It contains the project website,
real sequentially watermarked audio examples, and a standalone audio evaluation
utility. The training pipeline, trained LayerMark weights, Adapter and Remover
implementations, and full inference pipeline are not included in this release.
The utility below evaluates existing WAV files; it does not generate LayerMark
watermarks or reproduce the full paper experiments.

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

## Files

- `index.html`, `styles.css`, `app.js`: static website and audio players.
- `evaluate_audio.py`: standalone WAV quality evaluation.
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
code license has not yet been selected by the authors.
