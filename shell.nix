{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.fastapi
    python311Packages.uvicorn
    python311Packages.matplotlib
    python311Packages.numpy
    python311Packages.pandas
    python311Packages.pydantic
  ];

  shellHook = ''
    echo "Sailing Polar Plotter development environment"
    echo "Run 'uvicorn app.main:app --reload' to start the development server"

    echo "starting automatically"

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8888

    echo "quitting nix-shell"
    exit
  '';
}
