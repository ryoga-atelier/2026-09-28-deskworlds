// Spectral-wave idea adapted from ScottieFox CAUSTIC//LITE (MIT), pinned at
// d87351bff19831aa9d11c0679605fad6797b133f. See CAUSTIC-LICENSE.txt.
// This fixed-camera habitat has estimated depth: the projection is an optical
// approximation, not the demo's complete ray tracer or measured aquarium geometry.
export const CLEAR_WATER_GLSL = /* glsl */ `
  void tankWave(vec2 p,float t,vec2 k,float a,float rate,float phase,
    inout vec3 field,inout vec3 curvature) {
    float q=dot(p,k)-t*rate+phase;
    float s=sin(q),c=cos(q);
    field+=a*vec3(s,k*c);
    curvature-=a*s*vec3(k.x*k.x,k.y*k.y,k.x*k.y);
  }
  void tankSurface(vec2 p,float t,out vec3 field,out vec3 curvature) {
    field=vec3(0.);curvature=vec3(0.);
    tankWave(p,t,vec2(2.1,1.3),.023,.79,0.,field,curvature);
    tankWave(p,t,vec2(-1.7,2.9),.014,.93,1.3,field,curvature);
    tankWave(p,t,vec2(3.7,-1.8),.0075,1.18,2.7,field,curvature);
    tankWave(p,t,vec2(-3.3,-3.9),.005,1.43,.8,field,curvature);
    tankWave(p,t,vec2(5.4,2.7),.0028,1.67,3.7,field,curvature);
    tankWave(p,t,vec2(1.1,-5.9),.0026,1.81,5.1,field,curvature);
  }
  float tankCaustic(vec2 p,float t,float depth) {
    vec3 w,h;tankSurface(p+vec2(.20,.12)*depth,t,w,h);
    // Small-angle refracted ray convergence, using the Hessian of the same
    // surface as the visible ripples. The limit prevents singular bright flashes.
    float path=clamp(depth,1.,9.)*.23;
    float determinant=(1.+path*h.x)*(1.+path*h.y)-path*path*h.z*h.z;
    return clamp(1./max(.33,abs(determinant)),.62,2.5);
  }
`;

export const HABITAT_OPTICS_GLSL = /* glsl */ `
  ${CLEAR_WATER_GLSL}
  vec3 tankPhotograph(vec2 uv,vec3 photograph) {
    float d=texture2D(habitatDepth,uv).r;
    float rear=1.-smoothstep(.035,.20,d);
    vec2 screen=(uv-.5)/habitatCrop+.5;
    vec4 farPoint=habitatInverseViewProjection*vec4(screen*2.-1.,1.,1.);
    vec3 ray=farPoint.xyz/farPoint.w-habitatCameraPosition;
    vec3 world=habitatCameraPosition+ray*habitatDistance(uv)/dot(ray,habitatCameraForward);
    float depth=clamp(9.8-world.y,1.,9.);
    float focus=tankCaustic(world.xz,habitatTime,depth);
    float bed=1.-smoothstep(.23,.43,uv.y);
    float leaf=smoothstep(.015,.10,photograph.g-max(photograph.r*.86,photograph.b));
    float receiver=max(bed,(1.-rear)*(.35+.35*leaf));
    // Concentrated light brightens diffuse surfaces without clipping bright sand.
    vec3 lightRoom=max(vec3(0.),vec3(1.)-photograph);
    photograph+=lightRoom*max(0.,focus-1.)*.30*receiver;
    photograph*=1.+min(0.,focus-1.)*.15*receiver;
    // Bright blue distance haze belongs to the rear water, not the rendered fish.
    float water=smoothstep(.03,.17,photograph.b-photograph.r);
    photograph=mix(photograph,max(photograph,vec3(.36,.65,.79)),rear*water*.10);
    // Sparse moving illumination shafts, broad and soft at the source.
    float slant=uv.x+.27*(1.-uv.y);
    float wobble=.007*sin(habitatTime*.29+uv.y*4.);
    float beams=exp(-pow((slant-.27-wobble)/.024,2.))
      +.65*exp(-pow((slant-.49+wobble*.7)/.036,2.))
      +.45*exp(-pow((slant-.73-wobble*.5)/.019,2.));
    float beamMask=smoothstep(.15,.43,uv.y)*(1.-smoothstep(.92,1.,uv.y));
    photograph+=(1.-photograph)*vec3(.86,.95,1.)*beams*beamMask*(.065+.025*rear);
    // Looking up from underwater: a shallow, distorted reflection of the same
    // planting and lamp. Restricted to the top band, so the sand cannot wobble.
    float surface=smoothstep(.865,.967,uv.y);
    vec3 wave,curve;tankSurface(vec2(uv.x*18.,uv.y*9.),habitatTime,wave,curve);
    vec2 reflectUV=vec2(uv.x+wave.y*.15,.83-(uv.y-.87)*2.+wave.z*.10);
    vec3 reflected=texture2D(habitatColor,clamp(reflectUV,vec2(.002),vec2(.998))).rgb;
    float stripe=pow(max(0.,.5+.5*sin(uv.y*220.+wave.x*130.)),7.);
    float fresnel=.13+.23*smoothstep(.87,1.,uv.y);
    photograph=mix(photograph,reflected,surface*fresnel);
    photograph+=(1.-photograph)*surface*(.10*stripe+.12*pow(max(0.,wave.y*5.),3.));
    return photograph;
  }
`;
