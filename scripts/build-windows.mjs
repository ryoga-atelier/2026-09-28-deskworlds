import { build } from "esbuild";
import { readFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.argv[2]);
if (!process.argv[2]) throw new Error("Usage: node scripts/build-windows.mjs <scene folder>");
await build({
  entryPoints: [path.join(root, "scenes/riverscape/src/main.js")],
  outfile: path.join(root, "guppy-bundle.js"),
  bundle: true, format: "iife", platform: "browser", target: "chrome120",
  minify: false, legalComments: "eof",
  alias: { three: path.join(root, "vendor/three.module.js") },
  plugins: [{
    name: "preserve-module-asset-locations",
    setup(builder) {
      builder.onLoad({ filter: /\.js$/ }, async ({ path: filename }) => {
        const relative = path.relative(root, filename).split(path.sep).join("/");
        if (relative.startsWith("../")) throw new Error("Module escaped the scene folder");
        // Every original module keeps its own asset base, including bundled
        // modules. Lively's localfolder scheme does not need ES module support.
        let contents = (await readFile(filename, "utf8")).replaceAll(
          "import.meta.url",
          "new URL(" + JSON.stringify(relative) + ", document.baseURI).href",
        );
        if (relative === "scenes/riverscape/src/main.js") {
          // Other local wallpapers may share the localfolder origin. Keep this
          // package Balanced without writing shared localStorage preferences.
          const anchor = "const query = new URLSearchParams(location.search);";
          if (!contents.includes(anchor)) throw new Error("Quality anchor changed");
          contents = contents.replace(anchor, anchor + '\nquery.set("quality", "balanced");');
        }
        return { contents, loader: "js", resolveDir: path.dirname(filename) };
      });
    },
  }],
  footer: { js: 'window.dispatchEvent(new Event("guppy-scene-ready"));' },
});
