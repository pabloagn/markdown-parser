# flake.nix
{
  description = "A Python script to reformat Markdown files";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {inherit system;};
      in {
        devShells.default = pkgs.mkShell {
          name = "markdown-formatter-dev";

          # The only dependency we need is Python
          buildInputs = [
            pkgs.python311
          ];
        };
      }
    );
}
