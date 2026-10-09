"""
Verify .gitignore patterns are correct.
Simulates Git's pattern matching behavior.
"""
import re
from pathlib import Path

def should_ignore(filepath, patterns):
    """
    Simulate Git's pattern matching for .gitignore.
    Patterns starting with ! are negation rules (whitelist).
    """
    ignored = False
    
    for pattern in patterns:
        if not pattern.strip() or pattern.strip().startswith('#'):
            continue
        
        pattern = pattern.strip()
        is_negation = pattern.startswith('!')
        if is_negation:
            pattern = pattern[1:]
        
        # Simple pattern matching (not full Git semantics, but sufficient for verification)
        if pattern == filepath or filepath.endswith('/' + pattern):
            if is_negation:
                ignored = False
            else:
                ignored = True
        elif '*' in pattern:
            regex = pattern.replace('.', r'\.').replace('*', '.*')
            if re.match(f'^{regex}$', filepath) or re.search(regex, filepath):
                if is_negation:
                    ignored = False
                else:
                    ignored = True
    
    return ignored

# Read patterns from .gitignore
with open('.gitignore', 'r') as f:
    patterns = f.readlines()

# Test cases
test_cases = [
    ('backend/.env', True, 'backend/.env should be IGNORED'),
    ('frontend/.env', True, 'frontend/.env should be IGNORED'),
    ('backend/.env.example', False, 'backend/.env.example should NOT be ignored'),
    ('frontend/.env.example', False, 'frontend/.env.example should NOT be ignored'),
    ('backend/.env.local', True, 'backend/.env.local should be IGNORED'),
    ('frontend/.env.test', True, 'frontend/.env.test should be IGNORED'),
    ('frontend/.env.test.example', False, 'frontend/.env.test.example should NOT be ignored'),
    ('backend/public/uploads/file.txt', True, 'backend/public/uploads/* should be IGNORED'),
    ('backend/public/uploads/.gitkeep', False, 'backend/public/uploads/.gitkeep should NOT be ignored'),
]

print("GITIGNORE PATTERN VERIFICATION")
print("=" * 70)
print()

all_pass = True
for filepath, should_be_ignored, description in test_cases:
    ignored = should_ignore(filepath, patterns)
    status = "✓ PASS" if ignored == should_be_ignored else "✗ FAIL"
    expected = "ignored" if should_be_ignored else "NOT ignored"
    actual = "ignored" if ignored else "NOT ignored"
    
    if ignored != should_be_ignored:
        all_pass = False
    
    print(f"{status}: {description}")
    print(f"       Expected: {expected}, Got: {actual}")
    print()

print("=" * 70)
if all_pass:
    print("✅ ALL VERIFICATION TESTS PASSED")
else:
    print("❌ SOME TESTS FAILED")
print()
