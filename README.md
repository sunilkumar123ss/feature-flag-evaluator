# Deterministic feature flags

Evaluate explicit targeting rules and reproducible percentage rollouts.

Educational implementation with synthetic examples.

## Run

Python 3.9 or newer; standard library only. From this directory:

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

The default example uses synthetic data and needs no credentials, installation, or network connection. The script also works by absolute path from another working directory.

## Behavior

Flags have a boolean default, enabled switch, ordered equality rules, and an optional rollout in basis points. Rules are checked first. The rollout hashes the flag key, salt, and user ID to a stable bucket from 0 to 9999; changing the salt intentionally reassigns buckets.

## Use in Python

```python
from main import evaluate

flag = {'key': 'example-feature', 'enabled': True,
        'default': False, 'rollout_bps': 2500}
result = evaluate(flag, user_id='synthetic-user', attributes={})
assert 0 <= result['bucket'] < 10000
```

## Design limits

This evaluates a supplied local configuration. It has no control plane, authentication, analytics, exposure logging, or stale-config recovery. Attributes must come from a trusted caller; feature flags are not authorization checks. Rollout percentages approximate population shares and do not guarantee exact cohort sizes.

## Verification

The unit tests cover successful operations, failure paths, and invariants. These are local correctness checks, not production performance or security certification.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
