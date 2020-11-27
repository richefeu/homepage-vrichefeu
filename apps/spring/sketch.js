// global parameters
let m = 1.0;
let k = 5.0;

// kinematics
let x = 150.0;
let y = 100.0;
let vx = -20.0;
let vy = 250.0;
let ax = 0.0;
let ay = 0.0;

// time increment for explicit integration
let dt = 0.02;

// origine of the frame
let x0 = 0.0;
let y0 = 0.0;

// called one time at the beginning
function setup() {
  createCanvas(400, 400);
  background(240); // light gray
   
  x0 = 0.5 * width;
  y0 = 0.5 * height;
}

// called periodically
function draw() {
  background(240); // light gray

  // Euler scheme
  x += vx * dt;
  y += vy * dt;
  
  let d = sqrt(x * x + y * y);
  ux = x / d;
  uy = y / d;
  let a = (k * d) / m;
  ax = -a * ux;
  ay = -a * uy;
  
  vx += ax * dt;
  vy += ay * dt;

  fill(21, 163, 180);
  circle(x0 + x, y0 + y, 20);

  // attached point
  stroke(100);
  line(x0, 0, x0, height);
  line(0, y0, width, y0);

  // spring
  stroke(0);
  line(x0, y0, x0 + x, y0 + y);
}
