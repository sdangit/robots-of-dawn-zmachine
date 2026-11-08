# Current verification

Checked on macOS with Python 3.9.6, Inform 6.44 and Frotz 2.55, 2026-11-08.

- Empty-directory rebuild using only reviewed source plus the external disk/compiler reproduced both candidate stories exactly. No historical artifacts or prior generated files were supplied.
- Private startup artifacts checked against 256 freshly executed native starts: full 64 KiB memory, nine CPU registers, and exact output.
- Generated startup setters checked in both Z5 and Z8 for every seed: 512 checks of all 61,440 modeled RAM bytes, nine registers plus PC, and exact output. The host intentionally omits the C64 I/O page $D000–$DFFF; this is not a claim of complete C64 hardware emulation.
- Gameplay regression passed 22 runs, 528 commands and 550 exact emitted-text/696-byte-state comparisons, across seeds 0, 1, 2, 3, 31, 63, 127, 128, 192, 254 and 255.
- Save/restore, fresh-process restore, and restart passed 32 full-state checks across seeds 0 and 255 in both formats.
- Nine disk-free packaging tests cover input identity, staged/history blobs, forbidden artifacts, and direct source-stage execution guards.
- Independent source review found no embedded game narrative, translated routines, editorial room tables, or generated game artifacts in the reviewed source set. Automated audits complement manual review; they are not legal clearance.

Frotz batch timing (three-run median, startup plus 100 LOOK commands): clean Z5/Z8 0.543 seconds versus preserved translated-text builds 0.171/0.174 seconds. This is a local throughput check, not a Cairn UI responsiveness measurement.

Release 4, serial 261108:

- Z5: 103,424 bytes; SHA-256 cc6ddb5d4ee1511c31955b073870bdff0ba2aa865adbf4bcd1887c36259a4263.
- Z8: 103,936 bytes; SHA-256 79b4d3002e1cb1409de963621d4dd70cbeb5c79e1bc16bcdc7863b2aa43d01ec.

Cairn automated observations were inconclusive: an earlier full-native-startup experiment displayed a budget-stop message through accessibility, but normal manual behavior was not established. These newer startup-artifact builds were not automatically tested in Cairn. Manual faithful-r4 testing subsequently confirmed correct saved location and inventory after restore, despite an incorrect inferred Cairn display label; see COMPATIBILITY.md. Historical broad/VICE audit claims do not apply automatically to this revision.
