// Structural regression checks for the no-shrimp, coherent-material guppy scene.
// These checks do not claim that the scene looks photorealistic; review the WebGL render.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { register } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const tree = resolve(process.argv[2]);
const sceneRoot = pathToFileURL(`${tree}/scenes/riverscape/`);
const sourceRoot = new URL('src/', sceneRoot);
const main = readFileSync(new URL('main.js', sourceRoot), 'utf8');
const water = readFileSync(new URL('water.js', sourceRoot), 'utf8');
const aquarium = readFileSync(new URL('aquarium-details.js', sourceRoot), 'utf8');
const metadata = JSON.parse(readFileSync(`${tree}/guppy-customization.json`, 'utf8'));

assert.doesNotMatch(main, /shrimp|crab/i, 'The shipped scene must contain guppies only');
assert.equal(existsSync(new URL('shrimp.js', sourceRoot)), false,
  'The no-shrimp build must not include the retired shrimp module');
assert.equal(metadata.revision, 'clearwater-guppy-v6');
assert.doesNotMatch(JSON.stringify(metadata), /shrimp|crab/i,
  'Build metadata must describe the current no-shrimp scene');
assert.match(main, /new THREE\.FogExp2\("#91a9a7", 0\.002\)/,
  'Clear-water rendering must use only a very light, neutral depth haze');
assert.match(main, /import \{ waterTime, waterLitShader \} from "\.\/water\.js";/,
  'The clear-water background should receive restrained animated water lighting');
assert.match(main, /backboard\.material\.onBeforeCompile = \(shader\) => waterLitShader\(shader\);/,
  'The background depth plane must carry subtle moving refracted light');
assert.match(main, /new THREE\.Color\('#2b3c3a'\), high = new THREE\.Color\('#94b1ac'\)/,
  'The back plane must read as neutral clear water, not a green or blue wash');
assert.match(main, /renderer\.toneMapping = THREE\.ACESFilmicToneMapping;/);
assert.match(main, /renderer\.toneMappingExposure = 1\.00;/);
assert.match(main, /renderer\.outputColorSpace = THREE\.SRGBColorSpace;/,
  'Keep the calibrated tone mapping and sRGB output path intact');
assert.match(water, /exp\(-vec3\(0\.006, 0\.006, 0\.006\) \* depth\)/,
  'Water absorption should stay neutral and nearly transparent');
assert.match(aquarium, /roughness: 0\.28, metalness: 0\.012,[\s\S]*?opacity: 0\.07/,
  'Surface reflections should remain soft and restrained while becoming visible');
execFileSync(process.execPath, ['--check', new URL('main.js', sourceRoot).pathname]);

register(new URL('tests/three-loader.mjs', sceneRoot));
const { createFishMaterials } = await import(new URL('fish-anatomy.js', sourceRoot));
const materials = createFishMaterials();
assert.ok(Math.abs(materials.skin.roughness - materials.fins.roughness) <= 0.025,
  'The body and tail must use closely matched roughness');
assert.ok(materials.skin.clearcoat <= 0.05,
  'The body must not read as polished plastic');
assert.ok(materials.skin.envMapIntensity <= 0.3,
  'Body reflections should remain restrained');
assert.ok(materials.fins.metalness <= 0.03,
  'Translucent fins must not read as metallic');

console.log(JSON.stringify({ pass: true, revision: metadata.revision,
  guppyOnly: true, bodyRoughness: materials.skin.roughness,
  finRoughness: materials.fins.roughness }, null, 2));
