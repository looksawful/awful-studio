# Flue

Status: candidate.

Upstream: https://github.com/SFKislev/Flue

Purpose: optional developer bridge for live Blender inspection and bounded debugging workflows.

Before adoption:
- pin an exact release or commit;
- verify Blender 5.2.1 behavior on Windows and in the test environment where practical;
- document security boundaries for scripts executed in Blender;
- compare against the headless CLI runtime harness;
- keep it optional rather than making it a canonical test dependency.

No third-party code is vendored here yet.
