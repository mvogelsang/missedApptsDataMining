with import <nixpkgs> {};
with pkgs.python27Packages;
let
  mplb = matplotlib.override {enableQt=true;};
in
  stdenv.mkDerivation {
    name = "impurePythonEnv";
    buildInputs = [
      MySQL_python
      scipy
      pandas
      cairo
      python27Full
      virtualenv
      pip
      mplb
      taglib
      openssl
      git
      libxml2
      libxslt
      libzip
      stdenv
      zlib ];
    src = null;
    shellHook = ''
    # set SOURCE_DATE_EPOCH so that we can use python wheels
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv --no-setuptools venv
    export PATH=$PWD/venv/bin:$PATH
    pip install -r requirements.txt
    '';
  }
