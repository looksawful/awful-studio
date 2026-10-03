from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEVICE = ROOT / "assets" / "device_mockups" / "macbook_pro_14"
sys.path.insert(0, str(DEVICE))

from geometry_contract import (
    G2_EXTERNAL_FACTS,
    G2_PROVISIONAL_FACTS,
    G2_DISPLAY_FACTS,
    G2_RELATIONS,
    GeometryFact,
    SourceClass,
    is_freezable,
    require_frozen_fact,
    validate_fact,
)


class MacBookG2ProvenanceContractTests(unittest.TestCase):
    def test_external_facts_are_individually_typed_and_traceable(self):
        self.assertNotIn("closed_lid_relation", G2_EXTERNAL_FACTS)
        for key, fact in G2_EXTERNAL_FACTS.items():
            with self.subTest(key=key):
                self.assertIsInstance(fact, GeometryFact)
                validate_fact(fact)
                self.assertTrue(is_freezable(fact))
                self.assertNotEqual(fact.source_class, SourceClass.PROVISIONAL)
                self.assertTrue(fact.source)
                self.assertTrue(fact.method)
                self.assertTrue(fact.frame)
                self.assertTrue(fact.confidence)

    def test_relations_are_not_disguised_as_metric_facts(self):
        self.assertEqual(
            G2_RELATIONS["closed_display_assembly"],
            "flush_with_top_case",
        )

    def test_unverified_hinge_dimensions_are_demoted(self):
        for key in (
            "hinge_cover_depth_mm",
            "hinge_cover_thickness_mm",
        ):
            with self.subTest(key=key):
                fact = G2_PROVISIONAL_FACTS[key]
                self.assertIsInstance(fact, GeometryFact)
                self.assertEqual(fact.source_class, SourceClass.PROVISIONAL)
                self.assertFalse(fact.frozen)
                validate_fact(fact)

    def test_release_accessor_rejects_nonfreezable_facts(self):
        width = require_frozen_fact(G2_EXTERNAL_FACTS, "front_finger_recess_width_mm")
        self.assertGreater(width, 0)
        with self.assertRaises(ValueError):
            require_frozen_fact(G2_PROVISIONAL_FACTS, "hinge_cover_depth_mm")

    def test_display_stack_does_not_consume_unverified_outer_dimensions(self):
        generator = (DEVICE / "generate_low.py").read_text(encoding="utf-8")
        for literal in ("307.2*MM", "309.3*MM", "307.6*MM", "3.4*MM"):
            with self.subTest(literal=literal):
                self.assertNotIn(literal, generator)
        self.assertNotIn("'DISPLAY_GASKET'", generator)
        self.assertNotIn("'DISPLAY_LOWER_RAIL'", generator)
        self.assertNotIn("'SCREEN_GLASS'", generator)
        self.assertIn("'DISPLAY_SURROUND_VISUAL'", generator)

    def test_release_display_facts_are_individually_source_backed(self):
        for key, fact in G2_DISPLAY_FACTS.items():
            with self.subTest(key=key):
                self.assertIsInstance(fact, GeometryFact)
                validate_fact(fact)
                self.assertTrue(is_freezable(fact))
                self.assertNotEqual(fact.source_class, SourceClass.PROVISIONAL)
                self.assertTrue(fact.source)
                self.assertTrue(fact.method)


if __name__ == "__main__":
    unittest.main()
