// One transform is shared by geometry, attached growth, contacts and collision volumes.
import { vec, groundHeight } from './math.js';

export const WOOD_SCALE = 0.45;
export function woodPoint(x, y, z) {
  return vec(4.45 + (x - 3.48) * 0.42,
    groundHeight(4.45, -0.65) + 0.10 + (y - 0.37) * 0.32,
    -0.65 + (z + 0.15) * 0.70);
}
const original = [
  { x: 4.7, z: 0.35, rx: 1.7, ry: 1.5, rz: 1.15, lean: 0.15 },
  { x: -4.7, z: -0.35, rx: 1.35, ry: 1.45, rz: 1, lean: -0.12 },
  { x: 6.7, z: -0.85, rx: 1.05, ry: 0.82, rz: 1, lean: 0.10 },
  { x: -6.05, z: 0.55, rx: 1.05, ry: 0.68, rz: 0.85, lean: -0.08 },
];
const shifts = [[0.45,-0.28,0.90],[-0.48,-0.60,0.64],[0.0,-0.20,0.92],[-0.38,0.02,0.84]];
const centreY = r => groundHeight(r.x,r.z)+r.ry*0.57-Math.abs(r.lean)*r.rx*0.55;
export function tuneRock(rock,index) {
  if(index>=shifts.length)return rock;
  const [dx,dz,s]=shifts[index];
  return {...rock,x:rock.x+dx,z:rock.z+dz,rx:rock.rx*s,ry:rock.ry*s,rz:rock.rz*s};
}
export function rockPoint(index,x,y,z) {
  const before=original[index], after=tuneRock(before,index), s=shifts[index][2];
  return vec(after.x+(x-before.x)*s,centreY(after)+(y-centreY(before))*s,after.z+(z-before.z)*s);
}
export function stoneFernPoint(x,y,z) {
  // Only the tuft seated on the secondary stone moves with its reduced shoulder.
  return y>1 && x<0 ? rockPoint(1,x,y,z) : vec(x,groundHeight(x,z)+0.12,z);
}
