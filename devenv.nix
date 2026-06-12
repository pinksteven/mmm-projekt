{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  # https://devenv.sh/packages/
  packages = [pkgs.git];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages (ps: [
      ps.matplotlib
      ps.numpy
    ]);
    venv.enable = true;
  };
  languages.texlive = {
    enable = true;
    packages = [
      "preprint"
    ];
  };
}
