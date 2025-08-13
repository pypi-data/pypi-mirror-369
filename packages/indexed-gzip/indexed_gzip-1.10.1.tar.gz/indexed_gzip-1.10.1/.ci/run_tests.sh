#!/bin/bash
#
# Run indexed_gzip unit tests. Assumes that
# python setup.py develop has been run.

set -e

envdir="$1"
thisdir=$(cd $(dirname "$0") && pwd)

source $thisdir/activate_env.sh "$envdir"

# NITERS=<number of iterations for some tests>
# (see conftest.py)
if [[ -n "$NITERS" ]]; then
  NITERS="--niters $NITERS"
fi

# NELEMS=<number of elements/size of
#         test file, for some tests>
# (see conftest.py)
if [[ -n "$NELEMS" ]]; then
  NELEMS="--nelems $NELEMS"
fi

# Coverage reporting seems to be
# flaky and can result in test jobs
# failing, even if all tests passed.
EXTRA_ARGS="$EXTRA_ARGS --no-cov"

python -m indexed_gzip.tests      \
       -c pyproject.toml          \
       -v -s                      \
       -m "$TEST_SUITE"           \
       -k "$TEST_PATTERN"         \
       $NELEMS                    \
       $NITERS                    \
       $EXTRA_ARGS
