import importlib.util
from pathlib import Path
import sys
import unittest
_spec = importlib.util.spec_from_file_location('lab_' + Path(__file__).parent.name.replace('-', '_'), Path(__file__).with_name('main.py'))
m = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = m
_spec.loader.exec_module(m)

class FlagTests(unittest.TestCase):

    def flag(self, **changes):
        return {'key': 'test', 'enabled': True, 'default': False, **changes}

    def test_disabled_uses_default(self):
        self.assertFalse(m.evaluate(self.flag(enabled=False, rollout_bps=10000), 'a', {})['value'])

    def test_first_matching_rule_wins(self):
        rules = [{'attribute': 'team', 'equals': 'qa', 'value': False}, {'attribute': 'team', 'equals': 'qa', 'value': True}]
        r = m.evaluate(self.flag(rules=rules, rollout_bps=10000), 'a', {'team': 'qa'})
        self.assertFalse(r['value'])
        self.assertEqual(r['rule_index'], 0)

    def test_rollout_endpoints(self):
        for user in map(str, range(50)):
            self.assertFalse(m.evaluate(self.flag(rollout_bps=0), user, {})['value'])
            self.assertTrue(m.evaluate(self.flag(rollout_bps=10000), user, {})['value'])

    def test_stable_bucket_and_monotonic_rollout(self):
        first = m.evaluate(self.flag(rollout_bps=5000), 'a', {})
        again = m.evaluate(self.flag(rollout_bps=5000), 'a', {})
        self.assertEqual(first, again)
        bucket = first['bucket']
        self.assertTrue(m.evaluate(self.flag(rollout_bps=bucket + 1), 'a', {})['value'])

    def test_missing_attribute_does_not_match_null(self):
        flag = self.flag(rules=[{'attribute': 'region', 'equals': None, 'value': True}])
        self.assertFalse(m.evaluate(flag, 'a', {})['value'])
        self.assertTrue(m.evaluate(flag, 'a', {'region': None})['value'])

    def test_invalid_rollout_and_rule(self):
        with self.assertRaises(ValueError):
            m.evaluate(self.flag(rollout_bps=True), 'a', {})
        with self.assertRaises(ValueError):
            m.evaluate(self.flag(rules=[None]), 'a', {})
if __name__ == '__main__':
    unittest.main()
