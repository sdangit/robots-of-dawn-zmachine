# Mapper verification

Checked on macOS with Python 3.9.6, Inform 6.44 and Frotz 2.55, 2026-11-08.

- All 256 startup artifacts matched freshly executed native memory (64 KiB), registers, output, and room-description boundary offsets.
- Z5/Z8 passed 512 startup checks of all 61,440 modeled RAM bytes, nine registers plus PC, and exact output. The host intentionally omits the C64 I/O page $D000–$DFFF.
- Mapper trace regression passed 22 runs, 528 commands and 550 exact emitted-text/696-byte-state comparisons across eleven seeds. Trace mode disables presentation hooks.
- A separate normal-mode test passed in both formats: 12 commands across four encountered rooms, all native text preserved after removing generated labels, with expected labels present. Dedicated startup-only tests also verified that the initial heading appears at the native room-description boundary in both formats. All 139 generated titles are nonempty and unique. This is not exhaustive visual or Cairn mapper verification.
- Save/restore, fresh-process restore, and restart passed 32 full-state checks across seeds 0 and 255 in both formats.
- Independent source review and publication audits found no embedded game narrative, translated game routines, editorial room tables, or generated artifacts in the reviewed source/history. These checks do not confer legal rights.
- The preceding release-5 Frotz startup plus 100 LOOK commands took median 0.584 seconds (Z5) and 0.590 seconds (Z8) over three runs. This is not a Cairn UI latency measurement.

Release 6, serial 261108:

- Z5 SHA-256: 640fa92eaef365e962fef75f66621cb02906c2f10ca25534d2b233ccf57babcb.
- Z8 SHA-256: b290e681da5d2be2af1cd2db21edf5c12587532776c1486be307e7f92cc7e799.

An empty-directory mapper rebuild using only reviewed source plus the external disk/compiler reproduced both story hashes exactly; no prior startup or label artifacts were supplied. Manual faithful-r4 and mapper-r5 restore passed; release-6 startup-order confirmation remains pending. See COMPATIBILITY.md. Historical broad/VICE audit claims do not apply automatically to this revision. No remote exists.
