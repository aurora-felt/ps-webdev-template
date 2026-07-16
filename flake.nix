{
  description = "purescript web development template";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    purescript-overlay = {
      url = "github:thomashoneyman/purescript-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, purescript-overlay }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      nixpkgsFor = forAllSystems (system: import nixpkgs {
        inherit system;
        config = { };
        overlays = builtins.attrValues self.overlays;
      });
    in
    {
      overlays = {
        purescript = purescript-overlay.overlays.default;
      };
      packages = forAllSystems (system: {});

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
        in {
          default = pkgs.mkShell {
              venvDir = ".venv";
              inputsFrom = builtins.attrValues self.packages.${system};
              buildInputs = with pkgs; [
                purs
                spago-unstable
                purescript-language-server
                purs-tidy-bin.purs-tidy-0_10_0
                purs-backend-es
                nodejs
                git
                geckodriver
                esbuild
                python314
              ]
              ++ (with pkgs.python314Packages; [
                # python dev tools
                pip
                venvShellHook
                pyright

                # python packages
                aiohttp
                watchfiles
              ]);
            };
        }
      );
    };
}
