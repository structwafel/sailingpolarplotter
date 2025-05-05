{
  description = "A simple flake for the Sailing Polar Plotter project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python311Packages;
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            pythonPackages.fastapi
            pythonPackages.uvicorn
            pythonPackages.matplotlib
            pythonPackages.numpy
            pythonPackages.pandas
            pythonPackages.pydantic
          ];

          # Add shellHook to define the dev function
          shellHook = ''
            # Define the dev function to start the server
            function dev() {
              echo "Starting development server with live reloading..."
              uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
            }

            # Make the function available in the shell
            export -f dev

            # Show instructions
            echo "Sailing Polar Plotter development environment"
            echo "Type 'dev' to start the development server"
          '';
        };

        packages.default = pkgs.stdenv.mkDerivation {
          name = "sailing-polar-plotter";
          src = ./.;
          buildInputs = with pkgs; [
            python311
            pythonPackages.fastapi
            pythonPackages.uvicorn
            pythonPackages.matplotlib
            pythonPackages.numpy
            pythonPackages.pandas
            pythonPackages.pydantic
          ];
          installPhase = ''
            mkdir -p $out/bin
            cp -r ./app $out/
            cp -r ./static $out/
          '';
        };
      });
}
