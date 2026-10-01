# MacBook screen review — 2026-10-01

The display image was connected to both the reflective base color and emission of a Principled material. Strong studio area lights produced a large white reflection on the content surface itself, in addition to the separate cover glass.

Controlled Blender 5.2.1 renders with the glass hidden showed the glare remained. Removing the image's diffuse response alone retained the specular glare. Removing content specular response as well restored image contrast. The durable generator now uses a dark content base, the image only for emission, and zero content specular response; the separate glass retains reflections.

The runtime regression validator failed against the previous delivery, then passed against the regenerated one. The GLB contract verifies a dark untextured base, an emissive texture, and zero exported content specular factor. Regenerated source/package/delivery blends, both GLBs, catalog, and six tracked acceptance renders. Fresh verification: 170 fast tests and 11 preview tests passed; Storybook build passed.

Review Standards found no hard violations in a7237f2/dda41de, with two nonblocking test-maintainability observations. Review Spec found stale iPad acceptance previews (addressed separately). MacBook's five sampled hinge positions remain insufficient to establish clearance at every intermediate angle. Detailed keyboard/ports, physical screen UI calibration, and visual LOW approval remain outstanding. No site-controls redesign or production deployment was performed.
