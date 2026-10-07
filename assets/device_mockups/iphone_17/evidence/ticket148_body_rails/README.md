# Ticket #148 BODY_ALUMINUM rail topology

Exact exported BODY_ALUMINUM side-surface topology repair.

Before:
- min angle 0.0158 deg
- max aspect 2798.84
- side p95 aspect 159.48

After:
- min angle 5.9272 deg
- max aspect 9.6839
- 794 target side triangles
- confirmed quality seam: min angle >= 5 deg, aspect <= 10

Implementation:
- side annulus correspondence changed from clustered authored/corner rays to 44 uniform rays;
- cap diagonals are explicitly pinned by triangle quality;
- one main-shell depth loop removes corner-rail needle triangles;
- bottom cells are intentionally untouched and remain #149 scope.

Gates:
- fast 216/216 GREEN
- Blender runtime 17/17 GREEN
- Khronos compat + Meshopt 0 errors / 0 warnings
- source revision bbcbb93ce541dcaeccc93470770df69f6fa77514cd7182c5fdb8c2dcc861c507
- compat e8678121f510844abda164d714ac45a7abbf129aad408ee355c7a4a137eb920d
- Meshopt 054b341fb92b587b105952b318681450de268186c6812b44ad247337a24185bf

Whole-device #146 remains rejected/pending until #149 and a new exact Human Gate.
