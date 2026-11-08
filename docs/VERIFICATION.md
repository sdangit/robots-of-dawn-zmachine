# Current verification

Checked on macOS with Python 3.9.6, Inform 6.44 and Frotz 2.55, 2026-11-08.

The clean source pipeline builds Z5 and Z8 from the external C64 disk. Startup artifacts are generated privately by executing all 256 native seeds. Runtime regression passed 22 runs, 528 commands and 550 exact emitted-text/696-byte-state comparisons, across seeds 0, 1, 2, 3, 31, 63, 127, 128, 192, 254 and 255.

Cairn automated observations were inconclusive: the earlier full-native-startup experiment displayed a budget-stop message through accessibility, but normal manual behavior was not established. The newer startup-artifact builds were not automatically tested in Cairn. Manual validation is pending.

All-seed startup reconstruction, save/restore/restart, clean checkout, mapper branch, and final publication checks remain pending. No remote has been created. Historical test claims do not apply automatically to this revision.
