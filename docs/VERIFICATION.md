# Mapper verification

Checked on macOS with Python 3.9.6, Inform 6.44 and Frotz 2.55, 2026-11-08.

- All 256 startup artifacts matched freshly executed native memory (64 KiB), registers, and output.
- Z5/Z8 passed 512 startup checks of all 61,440 modeled RAM bytes, nine registers plus PC, and exact output. The host intentionally omits the C64 I/O page $D000–$DFFF.
- Mapper trace regression passed 22 runs, 528 commands and 550 exact emitted-text/696-byte-state comparisons across eleven seeds. Trace mode disables presentation hooks.
- A separate normal-mode test passed in both formats: 12 commands across four encountered rooms, all native text preserved after removing generated labels, with expected labels present. All 139 generated titles are nonempty and unique. This is not exhaustive visual or Cairn mapper verification.
- Save/restore, fresh-process restore, and restart passed 32 full-state checks across seeds 0 and 255 in both formats.
- Independent source review and publication audits found no embedded game narrative, translated game routines, editorial room tables, or generated artifacts in the reviewed source/history. These checks do not confer legal rights.
- Frotz startup plus 100 LOOK commands took median 0.584 seconds (Z5) and 0.590 seconds (Z8) over three runs. This is not a Cairn UI latency measurement.

Release 5, serial 261108:

- Z5 SHA-256: 5d28c0e45453f040dc073b8d7ed189d163fda6fe984ee56407df5ae632200afd.
- Z8 SHA-256: 7bb55e808d361c115b04f34c3f86abaeaf39503570e88da2e9db6b3f322c67ed.

An empty-directory mapper rebuild using only reviewed source plus the external disk/compiler reproduced both story hashes exactly; no prior startup or label artifacts were supplied. Manual faithful-r4 restore passed; fresh manual mapper validation remains pending. See COMPATIBILITY.md. Historical broad/VICE audit claims do not apply automatically to this revision. No remote exists.
