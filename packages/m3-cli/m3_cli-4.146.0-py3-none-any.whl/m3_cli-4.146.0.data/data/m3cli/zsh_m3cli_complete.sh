#!/bin/zsh

PYTHON_SYMLINK='python3'
SCRIPT_PATH=$2
HELP_FILE=$3

_m3cli_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[m3] )) && return 1

    m3 complete "zsh" ${words}
    response=""
    if [ -f "${HELP_FILE}" ] ; then
      response=("${(@f)$(<${HELP_FILE})}")
    fi

    for key descr in ${(kv)response}; do
      if [[ "$descr" == "_" ]]; then
          completions+=("$key")
      else
          completions_with_descriptions+=("$key":"$descr")
      fi
    done
    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi
    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
    compstate[insert]="automenu"
    rm -f "${HELP_FILE}"
}
compdef _m3cli_completion m3;