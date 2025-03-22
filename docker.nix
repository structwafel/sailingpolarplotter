{ pkgs ? import <nixpkgs> { } }:

pkgs.dockerTools.buildImage {
  name = "sailing-polar-plotter";
  tag = "latest";

  contents = [
    (pkgs.python311.withPackages
      (ps: with ps; [ fastapi uvicorn matplotlib numpy pandas pydantic ]))

    # Add your app code
    (pkgs.runCommand "app-code" { } ''
      mkdir -p $out/code
      cp -r ${./app} $out/code/app
      cp -r ${./static} $out/code/static
    '')
  ];

  config = {
    Cmd = [ "uvicorn" "app.main:app" "--host" "0.0.0.0" "--port" "8888" ];
    WorkingDir = "/code";
    ExposedPorts = { "8888/tcp" = { }; };
  };
}
