#! /bin/sh

set -e

target_dir=$1

if [ -z "${target_dir}" ]; then
  echo "Usage: $0 <target_dir> [--clear]"
  exit 1
fi

if [[ $# -ge 2 && $2 == "--clear" ]]; then
  echo "Cleaning up current Stackpacks in ${target_dir}/"
  rm -rf "${target_dir:?}/"* || true
fi

echo "Copying Stackpacks from /stackpacks to ${target_dir}/"

# Copy .sts files
cp /stackpacks/*.sts "${target_dir}/" 2>/dev/null || true
