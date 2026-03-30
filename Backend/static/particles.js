const canvas = document.getElementById("particles");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let mouse = {x:null, y:null};

window.addEventListener("mousemove",(e)=>{
  mouse.x = e.x;
  mouse.y = e.y;
});

let particles = [];
let burstParticles = []; // For the 'whoosh' effect

for(let i=0;i<100;i++){
  particles.push({
    x:Math.random()*canvas.width,
    y:Math.random()*canvas.height,
    vx:(Math.random()-0.5)*0.3,
    vy:(Math.random()-0.5)*0.3
  });
}

function animate(){

  ctx.clearRect(0,0,canvas.width,canvas.height);

  particles.forEach(p=>{

    let dx = p.x - mouse.x;
    let dy = p.y - mouse.y;
    let dist = Math.sqrt(dx*dx + dy*dy);

    // Impulse repel (cursor PUSH)
    if(dist < 120 && dist > 0){
      let force = (120 - dist) / 120;
      p.vx += (dx/dist) * force * 1.2;
      p.vy += (dy/dist) * force * 1.2;
    }

    // gentle natural float force
    p.vx += (Math.random()-0.5)*0.01;
    p.vy += (Math.random()-0.5)*0.01;

    // move
    p.x += p.vx;
    p.y += p.vy;

    // friction (slowly lose cursor boost)
    p.vx *= 0.97;
    p.vy *= 0.97;

    // terminal velocity
    let speed = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
    let max = 1.2;
    let min = 0.3;

    // terminal velocity
    if(speed > max){
      p.vx = (p.vx/speed)*max;
      p.vy = (p.vy/speed)*max;
    }

    // maintain floating speed (space cruise)
    if(speed < min){
      let angle = Math.random()*Math.PI*2;
      p.vx += Math.cos(angle)*0.05;
      p.vy += Math.sin(angle)*0.05;
    }


    // wrap around
    if(p.x > canvas.width) p.x = 0;
    if(p.x < 0) p.x = canvas.width;
    if(p.y > canvas.height) p.y = 0;
    if(p.y < 0) p.y = canvas.height;

    ctx.beginPath();
    ctx.arc(p.x,p.y,2,0,Math.PI*2);
    ctx.fillStyle="white";
    ctx.fill();
  });

  // connect lines
  for(let i=0;i<particles.length;i++){
    for(let j=i+1;j<particles.length;j++){
      let dx=particles[i].x-particles[j].x;
      let dy=particles[i].y-particles[j].y;
      let dist=Math.sqrt(dx*dx+dy*dy);

      if(dist<120){
        ctx.strokeStyle="rgba(255,255,255,0.1)";
        ctx.beginPath();
        ctx.moveTo(particles[i].x,particles[i].y);
        ctx.lineTo(particles[j].x,particles[j].y);
        ctx.stroke();
      }
    }
  }

  // Burst particles (whoosh)
  for (let i = burstParticles.length - 1; i >= 0; i--) {
    let p = burstParticles[i];
    p.x += p.vx;
    p.y += p.vy;
    p.alpha -= 0.02;
    
    if (p.alpha <= 0) {
      burstParticles.splice(i, 1);
      continue;
    }

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = p.color || "#34d399";
    ctx.globalAlpha = p.alpha;
    ctx.shadowBlur = 15;
    ctx.shadowColor = p.color || "#34d399";
    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.shadowBlur = 0;
  }

  requestAnimationFrame(animate);
}

function triggerWhoosh(x, y, color = "#34d399") {
  for (let i = 0; i < 50; i++) {
    let angle = Math.random() * Math.PI * 2;
    let speed = Math.random() * 8 + 2;
    burstParticles.push({
      x: x,
      y: y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 2, // Slight upward bias
      size: Math.random() * 4 + 1,
      alpha: 1,
      decay: Math.random() * 0.02 + 0.01,
      color: color
    });
  }
}

// Make globally accessible
window.triggerWhoosh = triggerWhoosh;

animate();
