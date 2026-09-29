// Shared coordinates for the wood, its attached fern and its moss colonies.
// Generate geometry and collision volumes from these coordinates, not mesh scale.
import { vec } from './math.js';

export const WOOD_SCALE = 0.58;
export function woodPoint(x, y, z) {
  return vec(3.48 + (x - 3.48) * 0.62,
    0.37 + (y - 0.37) * 0.44,
    -0.15 + (z + 0.15) * 0.75);
}
