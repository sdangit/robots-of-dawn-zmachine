# Robots of Dawn disk-to-Z-machine builder

Build Z5 and Z8 stories locally from your own matching C64 disk image. This repository contains extraction/build scripts and a 6502 compatibility host, not the game or a reconstructed implementation of its rules.

The build extracts memory from the supplied disk, generates private Inform source, and compiles it. Startup is precomputed by executing original disk bytes locally; parser, world rules, and text expansion execute disk bytes at runtime. There are no checked-in startup tables, game-text translations, room labels, game transcripts, or generated story files.

## Build

Requirements: Python 3.9+, Inform 6.44. Frotz is optional for testing.

```sh
python3 scripts/build.py --c64 '/path/to/ROBODAWN.D64' --inform6 '/path/to/inform6'
```

The exact supported disk is identified in disk-hashes.json. Obtain it independently and use only content you are entitled to use. All generated material stays under ignored build/. Do not publish that directory or attach its contents to releases.

Outputs: build/mapper/z5/robots.z5 and build/mapper/z8/robots.z8. This release-6 disk-native runtime differs from historical experimental builds. Previous save files and exact story hashes are not promised compatible.

See docs/BUILD.md, docs/TESTING.md, and docs/PUBLISHING.md. The separate cairn-mapper branch adds labels generated from the supplied disk for mapper presentation.

Project contributions are MIT licensed; original game rights are not granted. See NOTICE.md.

This mapper branch derives short labels from disk descriptions using the original text routines during the build. Labels are generic shortened descriptions plus numeric IDs, not the previous hand-authored landmarks. Startup and subsequent room descriptions place headings at the native room-description boundary; the status line provides an additional mapper cue. Manual Cairn release-6 testing confirmed startup and sampled movement headings; compatibility limits are documented in docs/COMPATIBILITY.md.
