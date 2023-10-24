"""Boolean feature flags with ordered rules and stable rollout buckets."""
import argparse
import hashlib
import json
import math

def scalar(value):
    return value is None or type(value) in (str, bool, int) or (type(value) is float and math.isfinite(value))

def evaluate(flag, user_id, attributes):
    if not isinstance(flag, dict) or not isinstance(flag.get('key'), str) or (not flag['key']):
        raise ValueError('Flag key required')
    if type(flag.get('enabled')) is not bool or type(flag.get('default')) is not bool:
        raise ValueError('enabled and default must be boolean')
    if not isinstance(user_id, str) or not user_id or (not isinstance(attributes, dict)) or any((not isinstance(k, str) or not scalar(v) for (k, v) in attributes.items())):
        raise ValueError('User ID and scalar attribute mapping required')
    rules = flag.get('rules', [])
    rollout = flag.get('rollout_bps', 0)
    salt = flag.get('salt', 'v1')
    if not isinstance(rules, list) or type(rollout) is not int or (not 0 <= rollout <= 10000) or (not isinstance(salt, str)):
        raise ValueError('Invalid rules or rollout')
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != {'attribute', 'equals', 'value'} or (not isinstance(rule['attribute'], str)) or (not rule['attribute']) or (not scalar(rule['equals'])) or (type(rule['value']) is not bool):
            raise ValueError('Invalid equality rule')
    if not flag['enabled']:
        return {'value': flag['default'], 'reason': 'disabled'}
    for (index, rule) in enumerate(rules):
        key = rule['attribute']
        if key in attributes and type(attributes[key]) is type(rule['equals']) and (attributes[key] == rule['equals']):
            return {'value': rule['value'], 'reason': 'rule', 'rule_index': index}
    encoded = json.dumps([flag['key'], salt, user_id], ensure_ascii=False, separators=(',', ':')).encode()
    bucket = int.from_bytes(hashlib.sha256(encoded).digest()[:8], 'big') % 10000
    included = bucket < rollout
    return {'value': True if included else flag['default'], 'reason': 'rollout' if included else 'default', 'bucket': bucket}

def demo():
    flag = {'key': 'synthetic-search-ui', 'enabled': True, 'default': False, 'rollout_bps': 2500, 'rules': [{'attribute': 'team', 'equals': 'testers', 'value': True}]}
    return {user: evaluate(flag, user, {'team': team}) for (user, team) in [('synthetic-a', 'testers'), ('synthetic-b', 'general'), ('synthetic-c', 'general')]}
if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(demo(), indent=2))
