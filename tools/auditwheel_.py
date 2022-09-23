import sys
from auditwheel.main import main
from auditwheel.policy import _POLICIES as POLICIES

for policy in POLICIES:
    policy['lib_whitelist'].append('libsteam_api.so')

if __name__ == "__main__":
    sys.exit(main())
