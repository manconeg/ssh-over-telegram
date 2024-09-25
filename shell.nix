{ pkgs ? import <nixpkgs> {} }:

# https://github.com/cachix/devenv/blob/main/examples/python-venv/devenv.nix
# https://gist.github.com/cdepillabout/f7dbe65b73e1b5e70b7baa473dafddb3
# https://www.reddit.com/r/NixOS/comments/17kzzdr/need_python_dev_env/
# https://www.zknotes.com/page/python%20development%20flake

pkgs.mkShell {
  buildInputs = [ pkgs.home-manager pkgs.helix ];
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      # select Python packages here
      python-pkgs.pandas
      python-pkgs.requests
      python-pkgs.pip
      python-pkgs.virtualenvwrapper
      python-pkgs.wheel
    ]))
  ];
  shellHook = ''
    mkdir ~/.venv
    VENV=~/.venv/ssh-over-telegram
    if test ! -d $VENV; then
      virtualenv $VENV

      escaped_pwd=$(printf '%s\n' "$(pwd)" | sed 's/[\/&]/\\&/g')      
      find $VENV -type f -exec sed -i "s/$escaped_pwd/\./g" {} +
#      rm -r $VENV/bin/*
#      ln -s $VENV/${pkgs.python3.sitePackages}/bin $VENV/bin
    fi
    source $VENV/bin/activate
#    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH=$VENV/${pkgs.python3.sitePackages}/:$PYTHONPATH
#    export PYTHONPATH="$PIP_PREFIX/${pkgs.python3.sitePackages}:$PYTHONPATH"
#    export PATH="$PIP_PREFIX/bin:$PATH"
#    export PATH=$(pwd)/$VENV/bin:$PATH
    unset SOURCE_DATE_EPOCH
'';
}

