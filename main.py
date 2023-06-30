"""Boolean feature flags with ordered rules and stable rollout buckets."""
import argparse
import hashlib
import json
import math

def scalar(value):
    return value is None or type(value) in (str, bool, int) or (type(value) is float and math.isfinite(value))
