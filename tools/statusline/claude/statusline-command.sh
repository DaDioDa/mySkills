#!/bin/bash
# Claude Code status line.
#
#   <model> - <effort>   Ctx [bar] N%   5h [bar] N% <reset countdown>   │ <folder> <branch>
#
# Uses bash builtins only - no external processes at all (no jq/awk/sed/grep/date/git).
# Process spawning is expensive on Windows and this runs on every render, so every
# field is parsed with bash regex and every number with integer arithmetic.
# Needs bash >= 5.0 for $EPOCHSECONDS.

# ---------------------------------------------------------------- appearance
BAR_WIDTH=10
BAR_FULL='#'
BAR_EMPTY='-'
GAP='   '                 # spacing between segments
SEP='│'                   # marks the start of the folder/branch group
                          # (swap for '|' if your terminal renders this wrong)

# 統一使用 Solarized 原色與固定 RGB，避免亮色 ANSI 色槽被映射成灰色。
C_MODEL=$'\033[1;38;2;238;232;213m' # 模型與思考強度：base2 淺米色、粗體
C_CTX=$'\033[38;2;42;161;152m'      # Context：cyan 青色
C_5H=$'\033[38;2;181;137;0m'       # 五小時用量：yellow 黃色
C_7D=$'\033[38;2;38;139;210m'      # 七日用量：blue 藍色
C_TPS=$'\033[38;2;133;153;0m'      # 最新 tok/s：green 綠色；已讀值使用 C_SEP
C_RESET_IN=$'\033[38;2;203;75;22m' # 重置倒數：orange 橘色
C_SEP=$'\033[38;2;101;123;131m'    # 分隔線與次要資訊：base00 灰色
C_DIR=$'\033[38;2;133;153;0m'      # 目錄：green 綠色
C_BRANCH=$'\033[38;2;211;54;130m'  # 分支：magenta 洋紅色
C_OFF=$'\033[0m'

# ---------------------------------------------------------------- read input
IFS= read -r -d '' input || :

# ---------------------------------------------------------------- parse
model='' effort='' cwd_raw='' ctx='' five='' resets='' seven='' resets7='' sid='' out='' api=''

re='"display_name":"([^"]*)"'
[[ $input =~ $re ]] && model=${BASH_REMATCH[1]}

re='"current_dir":"([^"]*)"'
[[ $input =~ $re ]] && cwd_raw=${BASH_REMATCH[1]}

re='"effort":\{"level":"([^"]*)"'
[[ $input =~ $re ]] && effort=${BASH_REMATCH[1]}

# context_window.used_percentage - drop the rate_limits tail first, otherwise the
# used_percentage keys inside five_hour/seven_day could be matched instead.
rl='"rate_limits"'
head=${input%%$rl*}
re='"used_percentage":(-?[0-9.]+)'
[[ $head =~ $re ]] && ctx=${BASH_REMATCH[1]}

re='"five_hour":\{([^}]*)\}'
if [[ $input =~ $re ]]; then
  fh=${BASH_REMATCH[1]}
  re='"used_percentage":(-?[0-9.]+)'
  [[ $fh =~ $re ]] && five=${BASH_REMATCH[1]}
  re='"resets_at":([0-9]+)'
  [[ $fh =~ $re ]] && resets=${BASH_REMATCH[1]}
fi

re='"seven_day":\{([^}]*)\}'
if [[ $input =~ $re ]]; then
  sd=${BASH_REMATCH[1]}
  re='"used_percentage":(-?[0-9.]+)'
  [[ $sd =~ $re ]] && seven=${BASH_REMATCH[1]}
  re='"resets_at":([0-9]+)'
  [[ $sd =~ $re ]] && resets7=${BASH_REMATCH[1]}
fi

# total_output_tokens is the LAST response's output (resets every response);
# total_api_duration_ms is the session-wide running total. Neither moves while a
# response is still streaming, so tok/s can only be updated when a response ends.
re='"session_id":"([^"]*)"'
[[ $input =~ $re ]] && sid=${BASH_REMATCH[1]}
re='"total_output_tokens":([0-9]+)'
[[ $input =~ $re ]] && out=${BASH_REMATCH[1]}
re='"total_api_duration_ms":([0-9]+)'
[[ $input =~ $re ]] && api=${BASH_REMATCH[1]}

# ---------------------------------------------------------------- helpers
# Round "37.4" to 37 and clamp to 0..100. Result in $R.
round_pct() {
  local v=$1 i d
  i=${v%%.*}
  [[ -z $i || $i == -* ]] && i=0
  if [[ $v == *.* ]]; then
    d=${v#*.}
    (( ${d:0:1} >= 5 )) && (( i++ ))
  fi
  (( i < 0 )) && i=0
  (( i > 100 )) && i=100
  R=$i
}

# Bar for an already-rounded percent. Result in $R.
make_bar() {
  local n=$(( ($1 * BAR_WIDTH + 50) / 100 )) f e
  (( n > BAR_WIDTH )) && n=$BAR_WIDTH
  (( n < 0 )) && n=0
  printf -v f '%*s' "$n" ''
  printf -v e '%*s' "$(( BAR_WIDTH - n ))" ''
  R="${f// /$BAR_FULL}${e// /$BAR_EMPTY}"
}

# epoch seconds -> "2h13m" / "47m" / "now". Result in $R.
# Tolerates a millisecond timestamp in case the field ever changes unit.
make_countdown() {
  local t=$1 d h m
  (( t > 100000000000 )) && t=$(( t / 1000 ))
  d=$(( t - EPOCHSECONDS ))
  if (( d <= 0 )); then R='now'; return; fi
  h=$(( d / 3600 )); m=$(( (d % 3600) / 60 ))
  if (( h >= 24 )); then R="$(( h / 24 ))d$(( h % 24 ))h"
  elif (( h > 0 )); then R="${h}h${m}m"
  elif (( m > 0 )); then R="${m}m"
  else R='1m'
  fi
}

# Branch name by walking up for .git and reading HEAD. Result in $R ('' if none).
find_branch() {
  local d=$1 head_file='' gd line i=0
  R=''
  while [[ -n $d && $d == */* && $i -lt 40 ]]; do
    if [[ -d $d/.git ]]; then head_file=$d/.git/HEAD; break; fi
    if [[ -f $d/.git ]]; then
      read -r line < "$d/.git" || :
      line=${line%$'\r'}
      gd=${line#gitdir: }
      gd=${gd//\\//}
      [[ $gd != /* && $gd != ?:/* ]] && gd=$d/$gd
      [[ -f $gd/HEAD ]] && head_file=$gd/HEAD
      break
    fi
    d=${d%/*}
    (( i++ ))
  done
  [[ -z $head_file ]] && return
  read -r line < "$head_file" || :
  line=${line%$'\r'}
  case $line in
    'ref: refs/heads/'*) R=${line#ref: refs/heads/} ;;
    '')                  R='' ;;
    *)                   R=${line:0:7} ;;   # detached HEAD -> short sha
  esac
}

# ---------------------------------------------------------------- tok/s
# Window of the last TPS_WINDOW responses, speed = sum(tokens) / sum(api ms).
# Responses under TPS_MIN_TOK tokens (tool-call-only turns) are skipped: their time
# is mostly time-to-first-token. State is kept per session in ~/.claude/.tokps-<id>:
#   line 1 = api ms at last sample, line 2 = "tok:ms tok:ms ..."
TPS_WINDOW=10
TPS_MIN_TOK=30
tps='' tps_new=0
if [[ -n $sid && -n $out && -n $api ]]; then
  tps_state=$HOME/.claude/.tokps-$sid
  last_api='' samples=''
  if [[ -f $tps_state ]]; then
    { read -r last_api; read -r samples; } < "$tps_state" || :
  fi
  arr=($samples)
  if [[ -z $last_api ]]; then
    printf '%s\n\n' "$api" > "$tps_state"
  elif (( api != last_api )); then
    if (( api > last_api && out >= TPS_MIN_TOK )); then
      arr+=("$out:$(( api - last_api ))")
      (( ${#arr[@]} > TPS_WINDOW )) && arr=("${arr[@]: -TPS_WINDOW}")
      tps_new=1
    fi
    printf '%s\n%s\n' "$api" "${arr[*]}" > "$tps_state"
  fi
  st=0 sm=0
  for s in "${arr[@]}"; do
    st=$(( st + ${s%%:*} )); sm=$(( sm + ${s##*:} ))
  done
  (( sm > 0 )) && tps=$(( (st * 1000 + sm / 2) / sm ))
fi

# ---------------------------------------------------------------- build line
line=''
add() { line="${line:+$line$GAP}$1"; }

if [[ -n $model ]]; then
  if [[ -n $effort ]]; then
    add "${C_MODEL}${model} - ${effort}${C_OFF}"
  else
    add "${C_MODEL}${model}${C_OFF}"
  fi
fi

if [[ -n $ctx ]]; then
  round_pct "$ctx"; p=$R
  make_bar "$p"
  add "${C_CTX}Ctx [$R] ${p}%${C_OFF}"
fi

if [[ -n $five ]]; then
  round_pct "$five"; p=$R
  make_bar "$p"
  seg="${C_5H}5h [$R] ${p}%${C_OFF}"
  if [[ -n $resets ]]; then
    make_countdown "$resets"
    seg="$seg ${C_RESET_IN}${R}${C_OFF}"
  fi
  add "$seg"
fi

if [[ -n $seven ]]; then
  round_pct "$seven"; p=$R
  make_bar "$p"
  seg="${C_7D}7d [$R] ${p}%${C_OFF}"
  if [[ -n $resets7 ]]; then
    make_countdown "$resets7"
    seg="$seg ${C_RESET_IN}${R}${C_OFF}"
  fi
  add "$seg"
fi

if [[ -n $tps ]]; then
  if (( tps_new )); then add "${C_TPS}${tps} tok/s${C_OFF}"
  else add "${C_SEP}${tps} tok/s${C_OFF}"
  fi
fi

if [[ -n $cwd_raw ]]; then
  cwd=${cwd_raw//\\//}
  while [[ $cwd == */ ]]; do cwd=${cwd%/}; done
  dir=${cwd##*/}
  [[ -z $dir ]] && dir=$cwd
  right="${C_DIR}${dir}${C_OFF}"
  find_branch "$cwd"
  [[ -n $R ]] && right="$right ${C_BRANCH}${R}${C_OFF}"
  add "${C_SEP}${SEP}${C_OFF} $right"
fi

[[ -z $line ]] && line="${C_SEP}no status data yet${C_OFF}"

printf '%s\n' "$line"
