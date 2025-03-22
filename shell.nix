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
}
