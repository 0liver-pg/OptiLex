#!/bin/zsh
# Calibration grid: data-scaling ruler (1M/2M/4M tokens, 1 epoch) + positive control (1M x 4 epochs).
# Seed-major order so a full first replicate lands early.
cd "$(dirname $0)/.."
for s in 0 1 2; do
  for cfg in "1 1" "2 1" "4 1" "1 4"; do
    set -- ${=cfg}
    tag="D${1}M_E${2}_s${s}"
    [[ -f results/$tag.json ]] || .venv/bin/python pilot/train.py --tokens ${1}e6 --epochs $2 --seed $s --tag $tag
  done
done
echo GRID_DONE
