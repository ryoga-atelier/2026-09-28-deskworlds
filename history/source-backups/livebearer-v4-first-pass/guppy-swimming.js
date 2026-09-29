// Shared colour/depth deformation. Tail tissue continues from the peduncle;
// unlike the trunk it bends freely instead of extending the articulated spine.
export const GUPPY_SWIM_GLSL = /* glsl */ `
  attribute vec4 aSwim;
  attribute float aFinPhase;
  attribute float aPart;
  attribute float aFinProgress;
  attribute float aGuppyVariant;
  attribute float aGuppySeed;
  varying vec3 vSkinPoint;
  varying vec2 vFishUV;
  varying float vFishPart;
  const float PIVOT = 0.12;
  vec3 gSwimPosition;
  float spineAngle(float s) {
    float along = clamp(s / 0.43, 0.0, 1.0);
    return aSwim.z * s * (s < 0.0 ? 0.12 : 1.0)
      - 0.018 * aSwim.y * sin(aSwim.x)
      + 0.67 * aSwim.y * pow(along, 2.0) * sin(aSwim.x - s * 8.6);
  }
  vec3 finMotion(vec3 p) {
    float r = aFinProgress;
    float effort = clamp(aSwim.y / 0.78, 0.0, 1.0);
    if (aPart > 0.5 && aPart < 1.5) {
      float across = 1.0 - 2.0 * uv.x;
      float lag = aSwim.x - 3.6 - r * 2.1;
      // The outer membrane carries a slower residual water wave during a glide.
      float flow = sin(aFinPhase * 0.26 - r * 3.2 + aGuppySeed * 5.0);
      float open = 0.88 + 0.07 * sin(aFinPhase * 0.19 + aGuppySeed * 7.0)
        - 0.18 * effort * (0.5 + 0.5 * sin(lag + 1.1))
        - 0.09 * min(abs(aSwim.z), 1.3);
      float rootY = across * 0.022;
      p.y = mix(p.y, rootY + (p.y-rootY) * open * (0.89+0.23*aGuppySeed), r);
      p.x = -0.288 + (p.x+0.288) * (0.91+0.17*aGuppySeed);
      // Travelling bending and cupping, rooted exactly at the hypural plate.
      p.z += r*r * ((0.023+0.105*effort)*sin(lag)
        + 0.023*flow + 0.032*across*across*sin(lag-0.9)
        + 0.015*sin(across*8.0-r*4.0-aFinPhase*0.32));
      p.x += r*r * (0.013+0.035*effort) * pow(sin(lag),2.0);
    } else if (aPart > 1.5 && aPart < 2.5) {
      p.z += r*r*(0.015+0.023*effort)*sin(aSwim.x-r*2.5-1.4)
        + r*r*0.012*sin(aFinPhase*0.4-uv.x*5.0);
      p.y -= r*r*0.014*effort;
    } else if (aPart > 3.5 && aPart < 5.5) {
      float side = aPart < 4.5 ? 1.0 : -1.0;
      float beat = sin(aFinPhase + side * 0.9);
      p.z += side*r*((0.014+0.020*aSwim.w)*beat+0.020*aSwim.w);
      p.x += r*(0.015*beat-0.027*aSwim.w);
      p.y += r*0.011*cos(aFinPhase+side*0.9);
    } else if (aPart > 2.5 && aPart < 6.5) {
      p.z += sin(aFinPhase-p.x*10.0)*r*0.004;
    }
    return p;
  }
  vec3 bendSpine(vec3 p, inout vec3 n) {
    float extension = aPart > 0.5 && aPart < 1.5 ? min(p.x+0.288,0.0) : 0.0;
    float s = PIVOT-p.x+extension;
    float theta=spineAngle(s);
    vec2 spine=vec2(PIVOT,0.0);
    float kappa=(spineAngle(s+0.001)-spineAngle(s-0.001))/0.002;
    if(s<0.0) {
      float mid=spineAngle(s*0.5);
      spine+=vec2(-cos(mid),sin(mid))*s;
    } else {
      float ds=s/8.0;
      for(int i=0;i<8;i++) {
        float mid=spineAngle((float(i)+0.5)*ds);
        spine+=vec2(-cos(mid),sin(mid))*ds;
      }
    }
    float c=cos(theta),sn=sin(theta);
    vec3 local=vec3(n.x/max(0.3,1.0-p.z*kappa),n.y,n.z);
    n=normalize(vec3(local.x*c+local.z*sn,local.y,-local.x*sn+local.z*c));
    return vec3(spine.x+p.z*sn+extension*c,p.y,spine.y+p.z*c-extension*sn);
  }
`;
