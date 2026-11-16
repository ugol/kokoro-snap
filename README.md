# Kokoro inference snap

Early engineering prototype for packaging [Kokoro 82M](https://huggingface.co/hexgrad/Kokoro-82M) as a Canonical Inference Snap.

The initial implementation targets CPU inference with [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), WAV output, and English and Italian voices.

**Status:** experimental. Snapcraft packaging, model components, `modelctl` speech capabilities, and offline tests remain to be completed. This is not yet an installable snap.

See [Canonical Inference Snaps](https://github.com/canonical/inference-snaps) for architectural conventions.
