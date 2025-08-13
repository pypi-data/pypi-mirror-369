#!/usr/bin/env bash

# Set up a virtual environment with build and
# run-time dependencies for indexed_gzip.
#

set -e
set -x

envdir="$1"
thisdir=$(cd $(dirname "$0") && pwd)

# NUMPY=<some numpy version>
if [[ -n "$NUMPY" ]]; then
  NUMPY="numpy==$NUMPY.*"
else
  NUMPY="numpy"
fi

# NIBABEL=<some nibabel version>
if [[ -n "$NIBABEL" ]]; then
  NIBABEL="nibabel==$NIBABEL.*"
else
  NIBABEL="nibabel"
fi

if [[ "$USING_OS_PYTHON" != "1" ]]; then
  pip install virtualenv
fi

if [[ "$USING_OS_PYTHON" == "1" ]]; then
  python"$PYTHON_VERSION" -m venv "$envdir"
else
  python -m venv "$envdir"
fi

source $thisdir/activate_env.sh "$envdir"
pip install wheel setuptools build
pip install --prefer-binary cython pytest coverage pytest-cov "$NUMPY" "$NIBABEL"
