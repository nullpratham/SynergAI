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

  requestAnimationFrame(animate);
}

animate();
