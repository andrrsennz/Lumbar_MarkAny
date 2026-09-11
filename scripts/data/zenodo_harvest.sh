#!/usr/bin/env bash
# zenodo_harvest.sh -- Zenodo dataset discovery via curl (urllib is rate-limited
# more aggressively by Zenodo than curl in this environment). Paced at 1 req/4s.
set -u
OUT="data/registry/discovery_raw/zenodo_pages"
mkdir -p "$OUT"
i=0
while IFS= read -r q; do
  [ -z "$q" ] && continue
  i=$((i+1))
  slug=$(echo "$q" | tr ' ' '_' | tr -cd '[:alnum:]_')
  enc=$(python -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$q")
  code=$(curl -sS --max-time 60 -w "%{http_code}" \
      -o "$OUT/${slug}.json" \
      "https://zenodo.org/api/records?q=${enc}&size=25&type=dataset")
  n=$(python -c "
import json,sys
try:
    d=json.load(open(sys.argv[1],encoding='utf-8')); print(len(d.get('hits',{}).get('hits',[])))
except Exception: print('ERR')
" "$OUT/${slug}.json" 2>/dev/null)
  printf '%-46s http=%s hits=%s\n' "$q" "$code" "$n"
  sleep 4
done < scripts/data/zenodo_queries.txt
