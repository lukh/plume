#!/bin/bash
set -o pipefail

LRED='\033[1;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
LMAGENTA='\033[1;35m'
NC='\033[0m' # No Color

pip install build

pip install requests==2.28.1
pip uninstall pip-system-certs &> /dev/null

echo -e "${CYAN}start webserver with self-signed cert${NC}"
python3 test/simple-https-server.py &

echo -e "${CYAN}Should fail to verify self-signed cert${NC}"
curl -s https://localhost:4443 || (echo -e "\n${LMAGENTA}curl failed as expected${NC}"; true)
python3 test/request.py 2> /dev/null || (echo -e "${LMAGENTA}python failed as expected${NC}\n"; true)

echo -e "${CYAN}Install self-signed cert in system, curl should pass${NC}"
cp test/pki/ca.crt  /usr/local/share/ca-certificates/
update-ca-certificates

curl -s https://localhost:4443 > /dev/null && echo -e "\n${GREEN}curl passed as expected${NC}"
python3 test/request.py 2> /dev/null || (echo -e "${LMAGENTA}python failed as expected${NC}\n"; true)

echo -e "${CYAN}Install pip-system-certs, curl & python should pass${NC}"
pip install -e .

curl -s https://localhost:4443 > /dev/null && echo -e "\n${GREEN}curl passed as expected${NC}"
python3 test/request.py > /dev/null && echo -e "${GREEN}python passed as expected${NC}\n"

echo -e "${CYAN}Uninstall pip-system-certs, python should fail again${NC}"
pip uninstall pip-system-certs &> /dev/null

curl -s https://localhost:4443 > /dev/null && echo -e "\n${GREEN}curl passed as expected${NC}"
python3 test/request.py 2> /dev/null || (echo -e "${LMAGENTA}python failed as expected${NC}\n"; true)

echo -e "${CYAN}Install pip-system-certs from wheel, curl & python should pass${NC}"
rm -rf dist/*.whl
python -m build --wheel
pip install dist/*.whl

curl -s https://localhost:4443 > /dev/null && echo -e "\n${GREEN}curl passed as expected${NC}"
python3 test/request.py > /dev/null && echo -e "${GREEN}python passed as expected${NC}\n"

echo -e "${CYAN}Test pip install still works after pip-system-certs installation${NC}"
pip install --no-cache-dir certifi > /dev/null && echo -e "${GREEN}pip install certifi passed as expected${NC}"
pip install --no-cache-dir --index-url https://pypi.org/simple/ urllib3 > /dev/null && echo -e "${GREEN}pip install urllib3 from PyPI passed as expected${NC}\n"

echo -e "${CYAN}Test pip install with trusted-host configuration (issue #39)${NC}"
# Create temporary pip config with trusted-host
mkdir -p /tmp/pip-test-config
cat > /tmp/pip-test-config/pip.conf <<'EOF'
[global]
trusted-host = pypi.org
EOF

# Test with trusted-host config - verifies our patch for pip's InsecureCacheControlAdapter bug
export PIP_CONFIG_FILE=/tmp/pip-test-config/pip.conf
echo -e "${MAGENTA}Testing pip with trusted-host configuration...${NC}"
if pip install --no-cache-dir anyio 2>&1 | tee /tmp/pip-trusted-host-test.log; then
    echo -e "${GREEN}pip install with trusted-host passed${NC}\n"
    unset PIP_CONFIG_FILE
    rm -rf /tmp/pip-test-config /tmp/pip-trusted-host-test.log
else
    echo -e "\n${LRED}pip install with trusted-host FAILED${NC}"
    echo -e "${LRED}This exposes issue #39 - a latent bug in pip's InsecureCacheControlAdapter${NC}"
    echo -e "${LRED}See: https://gitlab.com/alelec/pip-system-certs/-/issues/39${NC}\n"
    echo -e "${LRED}Full error output:${NC}"
    cat /tmp/pip-trusted-host-test.log
    unset PIP_CONFIG_FILE
    rm -rf /tmp/pip-test-config /tmp/pip-trusted-host-test.log
    exit 1
fi

