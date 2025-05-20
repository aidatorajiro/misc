## Process separated wave files properly in whisper

When we use Whisper, we often separate a long audio wave data into multiple parts. However, if we run Whisper separately, all the outputs will have timestamps starts from zero. This script will adjust them into consistent timestamps.

1. Split a long wave file into separate wav files (manually via Audacity, or automatically). In Audacity, you can export multiple wave files after assigning "labels" to each separated clips. Make sure that files should have numbers, like "audio-001.wav", "audio-002.wav", "audio-003.wav". Place these wave files to the directory `./orig`.
2. Build BLIS and Whisper, and download Whisper model with `./01_build.bash`.
3. Run Whisper with `./02_whisper.bash`.
4. Create JSON transcription data with `./03_process.py`.
5. Output human-readable transcription data with `./04_format.py`.
