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




if __name__ == '__main__':
    unittest.main()
