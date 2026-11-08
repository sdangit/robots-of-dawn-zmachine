# Build pipeline

1. Verify every supplied disk's exact byte length and SHA-256 before extraction.
2. Copy the small source set into the private build work directory.
3. Read the D64 directory and linked sectors. Assemble the required PRG segments using header load addresses and the final segment's execution relocation; verify the resulting memory hash.
4. Execute original startup for all 256 seeds in the Python CPU harness, generating private startup memory/state/output artifacts.
5. Generate Inform source containing extracted memory, generated seed-specific startup setters, and the compatibility host.
6. Compile Z-machine 5 and/or 8 stories with external Inform 6.44.
7. Record input/output hashes in the private build manifest.

Startup is executed from disk bytes during the build, while command processing and text routines execute from disk bytes at runtime. No translated game-rule implementation is stored in the repository. The source tree needs no output from prior research or previous builds. Generated files are artifacts, not public source.

Use --version 5, --version 8, or --version both. --inform6 accepts an executable path or PATH name. INFORM6 provides its default. Optional --apple2 verifies identity only; it does not contribute to stories or reproduce the historical comparison. Any inherited Apple II path is cleared unless supplied explicitly.

Official compiler source: https://github.com/DavidKinder/Inform6/archive/refs/tags/v6.44.tar.gz
Expected archive SHA-256: 4096da66193e35834e9b6d99bf58681e833ae20e747c3aa7352dba7975d172d0
Build the compiler outside publishable source and retain its upstream license.

All generated outputs must remain under ignored build/. Start from a fresh checkout or use an empty build directory to verify there are no stale dependencies. A different compiler can produce different bytes. This revision changes story contents and is not guaranteed to load historical save files.

## Mapper-only label stage

This branch writes build/mapper outputs. After native startup preparation, prepare_labels.py reads room-description pointers from the extracted memory and executes the original disk's text routines. Generic shortening plus numeric room identifiers produce private room_titles.json. No hand-authored game-world name table is used. The compiler includes those local labels in the generated story and adds presentation hooks. This is release 6, serial 261108.

Startup extraction also observes the native room-description entry point and records output offsets and room IDs privately. The generator inserts headings at those recorded boundaries rather than matching embedded prose or appending a heading after the description.
