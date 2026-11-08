# Interpreter compatibility

## Frotz

Fresh Z5/Z8 checks cover generated startup, representative gameplay, save/restore, fresh-process restores, and restart. See VERIFICATION.md for exact coverage and limits.

## Cairn 3.5.1 (63)

Manual testing of the faithful release-4 candidate on 2026-11-08 confirmed that restore returned to the saved west hallway with the expected inventory. Restore therefore worked in this tested case.

Cairn nevertheless displayed an introductory-text fragment as its inferred location/save label and showed part of the introduction around restoration. The faithful build deliberately supplies no mapper room headings. This suggests an interpreter presentation/context issue, but the internal cause has not been established. The display alone is not evidence of lost game state; LOOK and INVENTORY confirmed the saved state.

The earlier mapper release 3 included editorial room headings, so it is not a like-for-like presentation comparison with faithful release 4. The clean cairn-mapper branch produces release 5, with headings generated from the supplied disk. Its automated Frotz tests pass, but fresh manual Cairn mapper validation remains outstanding. Do not treat this as a claim that the mapper display issue is resolved.

Earlier automated Cairn startup-budget observations were inconclusive and concerned an experimental full-runtime-startup build, not these final startup-artifact candidates. No exhaustive Cairn compatibility claim is made.

## Saves across builds

Use saves with their matching story. Release 4, release 5, and earlier releases have different story contents and are not guaranteed save-compatible. Keep previous story files alongside any saves you need.
