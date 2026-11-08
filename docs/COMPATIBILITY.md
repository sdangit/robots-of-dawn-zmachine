# Interpreter compatibility

## Frotz

Fresh Z5/Z8 checks cover generated startup, representative gameplay, save/restore, fresh-process restores, and restart. See VERIFICATION.md for exact coverage and limits.

## Cairn 3.5.1 (63)

Manual testing of the faithful release-4 candidate on 2026-11-08 confirmed that restore returned to the saved west hallway with the expected inventory. Restore therefore worked in this tested case.

Cairn nevertheless displayed an introductory-text fragment as its inferred location/save label and showed part of the introduction around restoration. The faithful build deliberately supplies no mapper room headings. This suggests an interpreter presentation/context issue, but the internal cause has not been established. The display alone is not evidence of lost game state; LOOK and INVENTORY confirmed the saved state.

The earlier mapper release 3 included editorial room headings, so it is not a like-for-like presentation comparison with faithful release 4. The clean cairn-mapper branch uses headings generated from the supplied disk. Manual Cairn release-5 Z5 testing confirmed correct save naming/context and restored location/inventory. It also exposed a startup heading placed after the description, while LOOK placed it before. Release 6 corrects this ordering using a boundary observed during native startup execution. Manual release-6 Cairn testing subsequently confirmed the initial heading before the room description, plus appropriate headings for LOOK and west/west/south movement. Release-5 restore validation and release-6 presentation validation are distinct checks, not a claim of exhaustive mapper compatibility.

Earlier automated Cairn startup-budget observations were inconclusive and concerned an experimental full-runtime-startup build, not these final startup-artifact candidates. No exhaustive Cairn compatibility claim is made.

## Saves across builds

Use saves with their matching story. Release 4, release 5, release 6, and earlier releases have different story contents and are not guaranteed save-compatible. Keep previous story files alongside any saves you need.
