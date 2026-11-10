#!/bin/bash
# TICKET-2 network probe loop: checks only, no large downloads.
# Probes: 172.28.4.16:18999 (unmetered), 127.0.0.1:7589 (metered mihomo), DNS.
LOG=/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-long-20261109/evidence/netprobe.log
i=0
while [ $i -lt 240 ]; do
  i=$((i+1))
  ts=$(date -u +%FT%TZ)
  line="$ts"
  t1=$(timeout 3 bash -c "echo > /dev/tcp/172.28.4.16/18999" 2>&1; echo $?)
  line="$line 18999_rc=$t1"
  t2=$(timeout 3 bash -c "echo > /dev/tcp/127.0.0.1/7589" 2>&1; echo $?)
  line="$line 7589_rc=$t2"
  dns=$(getent hosts gitlab.4pd.io >/dev/null 2>&1 && echo ok || echo fail)
  line="$line dns_gitlab=$dns"
  if [ "$t1" = "0" ]; then
    code=$(curl -sS -o /dev/null -w '%{http_code}' -x http://172.28.4.16:18999 --max-time 10 -I https://my.feishu.cn/ 2>&1)
    line="$line feishu_via_18999_HTTP=$code"
    code2=$(curl -sS -o /dev/null -w '%{http_code}' -x http://172.28.4.16:18999 --max-time 10 https://gitlab.4pd.io/api/v4/projects/gaoziming%2Fimage_authenticity_verification_leaderboard 2>&1)
    line="$line gitlab_project_api_via_18999_HTTP=$code2"
  fi
  echo "$line" >> "$LOG"
  sleep 60
done
echo "$(date -u +%FT%TZ) probe loop finished" >> "$LOG"
