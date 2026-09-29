// Bounded history of actual render submissions. Querying stats never starts animation.
// These are CPU-side frame intervals, not GPU presentation timings or requested FPS.
export function createFrameMetrics(capacity=4096) {
  const intervals=new Float32Array(capacity);
  let head=0,count=0,last=null,segments=0,lastGapMs=0;
  return {
    record(now) {
      if(last!==null){
        const elapsed=now-last;lastGapMs=elapsed;
        if(elapsed>1000){head=0;count=0;segments++;}
        else if(elapsed>0){intervals[head]=elapsed;head=(head+1)%capacity;count=Math.min(count+1,capacity);}
      }
      last=now;
    },
    stats(){
      const values=Array.from(intervals.subarray(0,count)).sort((a,b)=>a-b);
      const total=values.reduce((a,b)=>a+b,0);
      return {kind:'actual CPU render-submission intervals',samples:count,segments,
        lastFrameAtMs:last,lastGapMs,windowMs:total,
        fpsMeasured:total?1000*count/total:null,
        p50Ms:count?values[Math.floor((count-1)*.5)]:null,
        p95Ms:count?values[Math.floor((count-1)*.95)]:null,
        maxMs:count?values[count-1]:null};
    }
  };
}
