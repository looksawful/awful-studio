PASS

No documented violation or correctness defect found in the provided diff against ff22bb2.

The changes in `generate_low_v30.py` introduce a new parameter `preserve_depth_axis` to `place_on_apple_bottom()` and use it for USB components. The runtime contracts confirm:
- USB physical dimensions match specifications (iphone_v30_usb_frame_contract.py)
- USB topology is preserved with no modifiers and correct geometry (iphone_v30_usb_topology_contract.py)
- Exported GLB matches authored geometry (iphone_v30_usb_exported_triangles_contract.py)

All 16 verified tests pass, including the new USB contracts. The `preserve_depth_axis` logic maintains device X-spanning width as required by the contract, with no regression in physical dimensions or topology.

The changes are minimal, targeted, and fully validated by existing test suite. No breach of product invariants, safety rules, or runtime correctness is demonstrated.