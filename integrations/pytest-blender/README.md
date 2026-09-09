# pytest-blender

Status: candidate.

Upstream: https://github.com/mondeja/pytest-blender

Purpose: candidate harness for running pytest inside Blender's own Python runtime.

Before adoption:
- pin an exact release or commit;
- verify Blender 5.2.1 compatibility in the AWFUL runtime environment;
- verify install/uninstall behavior;
- compare it against the existing thin `tools/blender_runtime_probe.py` approach;
- record license and setup/rollback instructions;
- only then change status to `pilot` or `supported`.

No third-party code is vendored here yet.
