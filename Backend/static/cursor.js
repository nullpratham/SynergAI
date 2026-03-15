const canvas = document.getElementById("cursor");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let dots = [];

window.addEventListener("mousemove",(e)=>{
  dots.push({x:e.x,y:e.y,life:100});
});

function animate(){
  ctx.clearRect(0,0,canvas.width,canvas.height);

  for(let i=0;i<dots.length;i++){
    ctx.beginPath();
    ctx.arc(dots[i].x,dots[i].y,3,0,Math.PI*2);
    ctx.fillStyle="white";
    ctx.fill();
    dots[i].life--;

    if(dots[i].life<=0){
      dots.splice(i,1);
      i--;
    }
  }
  requestAnimationFrame(animate);
}

animate();
