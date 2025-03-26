#!/bin/sh

# setup python project (npm-like stub)
# (c) 2023, Mat.




# ...
CD="$(cd "$(dirname "$0")" && pwd)"

# ...
usage () {
    echo "Usage: $(basename "$0") [bootstrap] [clean] [run ...]"
}

# ...
create_venv () {
    $(which virtualenv) "$CD"/.venv/
}

# ...
enter_venv () {
    source "$CD"/.venv/bin/activate
}

# ...
install_deps () {
    pip install --upgrade pip
    pip install -r "$CD"/requirements.txt
}

# ...
cleanup () {
    rm -r "$CD"/.venv/
}

# ...
run_command () {
    local command="$1".py
    shift
    enter_venv
    python "$CD"/"$command" "$@"
}

# ...
if {
    [ "$#" -ne 1 ] && [ "${1}" != "run" ];
} || {
    [ "$#" -lt 2 ] && [ "${1}" == "run" ];
}; then
    usage
    exit 1
fi

# ...
opt="${1}"

# ...
case "$opt" in
    "bootstrap")
        create_venv
        enter_venv
        install_deps
        ;;
    "clean")
        cleanup
        ;;
    "run")
        enter_venv
        shift
        run_command "$@"
        ;;
    *)
        usage
        exit 1
        ;;
esac
