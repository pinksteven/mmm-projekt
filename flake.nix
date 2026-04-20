{
  inputs = {
    utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    utils,
  }:
    utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python3.withPackages (ps:
        with ps; [
          matplotlib
          numpy
        ]);
    in {
      devShells.default = with pkgs;
        mkShell {
          buildInputs = [
            zsh
            python
          ];
        };
    });
}
