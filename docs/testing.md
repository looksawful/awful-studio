# Testing AWFUL STUDIO

Use one entrypoint:

```bash
python tools/awful.py status
python tools/awful.py doctor
python -m unittest discover -s tests/static -p 'test_*.py'
python tools/awful.py test-runtime
```

The runtime command launches the pinned Blender 5.2.1 headlessly with `--factory-startup`, disables auto-execution of embedded scripts and turns Blender Python exceptions into a non-zero process exit.

GitHub Actions must call the same `tools/awful.py` path rather than maintaining a separate runtime test implementation.

Render tests are intentionally excluded from the current foundation gate.
