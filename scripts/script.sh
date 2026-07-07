#! /usr/bin/env bash
# check for gzip installation
if ! command -v gzip >/dev/null 2>&1; then
  echo "GZip is not installed."
  exit 1
fi

# check for parts of gz and merge them
shopt -s nullglob

for dir in ../data/raw/*/; do
  name=$(basename "$dir")
  output="${dir}${name}.csv.gz"

  if [[ -f "$output" ]]; then
    echo "Skipping $dir: $output already exists"
    continue
  fi

  files=("${dir}"*.gz.*)

  ((${#files[@]} == 0)) && continue

  echo "Processing $dir"

  cat "${files[@]}" >"$output"
done

for dir in ../data/raw/*/; do
  files=("${dir}"*.csv.gz)
  ((${#files[@]} == 0)) && continue

  csv="${files[0]%.gz}"

  if [[ -f "$csv" ]]; then
    echo "Skipping $csv: already extracted"
    continue
  fi

  gunzip "${files[@]}"
done

shopt -u nullglob

echo "All done!"
