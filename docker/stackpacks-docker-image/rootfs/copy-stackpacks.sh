#! /bin/sh

set -e

target_dir=$1

if [ -z "${target_dir}" ]; then
  echo "Usage: $0 <target_dir>"
  exit 1
fi

echo "Cleaning up current Stackpacks in ${target_dir}/"
rm -rf "${target_dir:?}/"* || true

echo "Copying Stackpacks from /stackpacks to ${target_dir}/"

# Copy .sts files
cp /stackpacks/*.sts "${target_dir}/" 2>/dev/null || true
