from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEVICE = ROOT / "assets" / "device_mockups" / "macbook_pro_14"
sys.path.insert(0, str(DEVICE))

from geometry_contract import G2_EXTERNAL_FACTS, G2_RELATIONS, require_frozen_fact


class MacBookG2ExternalContractTests(unittest.TestCase):
    def test_closed_display_is_a_relation_not_a_lid_part_dimension(self):
        self.assertNotIn("lid_plan_width_mm", G2_EXTERNAL_FACTS)
        self.assertNotIn("lid_plan_depth_mm", G2_EXTERNAL_FACTS)
        self.assertEqual(
            G2_RELATIONS["closed_display_assembly"],
            "flush_with_top_case",
        )

    def test_hinge_cover_is_corner_part_not_sixty_mm_sleeve(self):
        width = require_frozen_fact(G2_EXTERNAL_FACTS, "hinge_cover_width_mm")
        center_x = require_frozen_fact(G2_EXTERNAL_FACTS, "hinge_cover_center_abs_x_mm")
        self.assertAlmostEqual(width, 19.9, delta=2.0)
        self.assertAlmostEqual(center_x, 130.1, delta=2.0)

    def test_front_recess_and_bottom_hardware_follow_apple_calibration(self):
        recess = require_frozen_fact(G2_EXTERNAL_FACTS, "front_finger_recess_width_mm")
        foot_diameter = require_frozen_fact(G2_EXTERNAL_FACTS, "foot_diameter_mm")
        foot_side = require_frozen_fact(G2_EXTERNAL_FACTS, "foot_side_inset_mm")
        foot_edge = require_frozen_fact(G2_EXTERNAL_FACTS, "foot_edge_inset_mm")
        self.assertAlmostEqual(recess, 54.2, delta=1.5)
        self.assertGreaterEqual(foot_diameter, 16.5)
        self.assertLessEqual(foot_diameter, 18.1)
        self.assertGreaterEqual(foot_side, 19.5)
        self.assertLessEqual(foot_side, 22.5)
        self.assertGreaterEqual(foot_edge, 22.0)
        self.assertLessEqual(foot_edge, 23.5)

    def test_logo_uses_calibrated_closed_top_scale(self):
        logo_width = require_frozen_fact(G2_EXTERNAL_FACTS, "logo_width_mm")
        self.assertAlmostEqual(logo_width, 37.2, delta=2.0)

    def test_generator_no_longer_contains_rejected_g1_external_magic(self):
        generate = (DEVICE / "generate_low.py").read_text(encoding="utf-8")
        construction = (DEVICE / "construction_details.py").read_text(encoding="utf-8")
        self.assertNotIn("LID_W,LID_H=312.0*MM,212.0*MM", generate)
        self.assertNotIn("for end in (-30*mm,30*mm)", construction)
        self.assertNotIn("(36*mm, 6*mm, 3.1*mm)", construction)
        self.assertNotIn("5.2*mm,.75*mm", generate)


if __name__ == "__main__":
    unittest.main()
