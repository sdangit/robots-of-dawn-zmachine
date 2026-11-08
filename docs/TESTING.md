# Verification

Run disk-free packaging tests with make test. Run the publication audit with make audit.

After building, run:

```sh
python3 scripts/test_runtime.py --c64 '/path/to/ROBODAWN.D64' --inform6 '/path/to/inform6' --dfrotz '/path/to/dfrotz'
```

Expected text and state are computed privately by executing the supplied disk with the Python CPU harness. They are not checked-in game fixtures. The runtime test compares emitted bytes and 696 bytes of persistent state at each input boundary.

The CPU harness and Inform runtime share an instruction-set design; their agreement alone is not independent hardware-emulator verification. Historical VICE comparisons and older broad tests are not fresh results for this source set. See VERIFICATION.md for checks actually completed.
