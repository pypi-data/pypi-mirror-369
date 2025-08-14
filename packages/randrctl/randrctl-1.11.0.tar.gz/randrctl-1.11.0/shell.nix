{ pkgs ? import <nixpkgs> {} }:
let
  my-python = pkgs.python310;
  python-with-my-packages = my-python.withPackages (p: with p; [
    argcomplete
    pyyaml
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-with-my-packages
    pkgs.xorg.xrandr
  ];
  shellHook = ''
    PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
    # maybe set more env-vars
  '';
}
