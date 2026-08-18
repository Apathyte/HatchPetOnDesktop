const canvas = document.getElementById("dex");
const ctx = canvas.getContext("2d");
const workbench = document.querySelector(".workbench");
const appSelect = document.getElementById("appSelect");
const cpuRange = document.getElementById("cpuRange");
const idleRange = document.getElementById("idleRange");
const moodText = document.getElementById("moodText");
const behaviorText = document.getElementById("behaviorText");
const itemText = document.getElementById("itemText");
const notification = document.querySelector(".notification");

const apps = {
  terminal: { mood: "Attentive", item: "clipboard", gear: "vest" },
  vscode: { mood: "Supervising", item: "wrench", gear: "hardhat" },
  docker: { mood: "Alert", item: "wrench", gear: "vest" },
  "node-red": { mood: "Focused", item: "clipboard", gear: "hardhat" },
  ignition: { mood: "On watch", item: "clipboard", gear: "vest" },
  powerpoint: { mood: "Bored", item: "leash", pose: "dramatic" },
  excel: { mood: "Disappointed", item: "none", pose: "sit" },
  meeting: { mood: "Patiently done", item: "leash", pose: "flat" }
};

const dex = {
  x: 80,
  y: 300,
  vx: 0.32,
  direction: 1,
  frame: 0,
  pose: "trot",
  mood: "Calm",
  item: "none",
  gear: "none",
  attentionUntil: 0,
  zoomiesUntil: 0,
  notificationUntil: 0,
  midnightUntil: 0,
  dragging: false,
  cursorX: 0,
  cursorY: 0,
  lastWalk: performance.now()
};

function bounds() {
  const rect = workbench.getBoundingClientRect();
  return {
    width: rect.width,
    height: rect.height,
    floor: rect.height - 132
  };
}

function chooseBehavior(now) {
  const app = apps[appSelect.value];
  const idleMinutes = Number(idleRange.value);
  const cpu = Number(cpuRange.value);
  dex.mood = app.mood;
  dex.item = app.item;
  dex.gear = app.gear || "none";
  dex.pose = app.pose || "trot";

  if (cpu > 76) {
    dex.pose = "alert";
    dex.mood = "Awake";
  }

  if (idleMinutes > 60) {
    dex.pose = "leash";
    dex.item = "leash";
    dex.mood = "Needs a walk";
  } else if (idleMinutes > 38 && !app.pose) {
    dex.pose = "sleep";
    dex.mood = "Napping";
  }

  if (now < dex.attentionUntil) {
    dex.pose = "happy";
    dex.mood = "Content";
  }

  if (now < dex.zoomiesUntil) {
    dex.pose = "zoom";
    dex.mood = "Zoomies";
  }

  if (now < dex.notificationUntil) {
    dex.pose = "growl";
    dex.mood = "Protective";
  }

  if (now < dex.midnightUntil) {
    dex.pose = "patrol";
    dex.mood = "Night watch";
  }
}

function moveDex(now) {
  const b = bounds();
  if (dex.dragging) return;

  const speed = dex.pose === "zoom" ? 7.8 : dex.pose === "patrol" ? 1.1 : dex.pose === "leash" ? 0.8 : 0.32;
  const targetY = dex.pose === "sleep" || dex.pose === "flat" || dex.pose === "dramatic" ? b.floor + 24 : b.floor;
  dex.y += (targetY - dex.y) * 0.05;

  if (["sleep", "flat", "dramatic"].includes(dex.pose)) {
    dex.vx *= 0.88;
  } else {
    dex.vx = speed * dex.direction;
  }

  if (dex.pose === "leash") {
    const edge = dex.x < b.width / 2 ? 28 : b.width - 220;
    dex.x += (edge - dex.x) * 0.012;
  } else {
    dex.x += dex.vx;
  }

  if (dex.x < 20 || dex.x > b.width - 230) {
    dex.direction *= -1;
    dex.x = Math.max(20, Math.min(b.width - 230, dex.x));
  }

  if (Math.random() < 0.0012 && now > dex.attentionUntil && dex.pose === "trot") {
    dex.zoomiesUntil = now + 3200;
  }
}

function px(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
}

function drawDog(now) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(dex.direction === 1 ? 24 : 236, 0);
  ctx.scale(dex.direction, 1);

  const t = Math.floor(now / 160) % 4;
  const bob = ["sleep", "flat", "dramatic"].includes(dex.pose) ? 0 : Math.sin(now / 180) * 2;
  const pant = Math.floor(now / 280) % 2;
  const wag = dex.pose === "happy" ? Math.sin(now / 80) * 8 : Math.sin(now / 220) * 3;
  const charcoal = "#242424";
  const black = "#141516";
  const brindle = "#46372d";
  const grey = "#b8b2aa";
  const eye = "#130f0d";
  const tongue = "#c67973";

  const laying = ["sleep", "flat", "dramatic"].includes(dex.pose);
  const sit = dex.pose === "sit" || dex.pose === "alert" || dex.pose === "growl";
  const bodyY = laying ? 96 : sit ? 78 : 72 + bob;
  const bodyH = laying ? 34 : sit ? 52 : 46;

  px(68, bodyY + 6, 92, bodyH, charcoal);
  px(84, bodyY, 66, 18, "#303030");
  px(102, bodyY + 10, 44, 10, brindle);
  px(60, bodyY + 18, 22, 28, black);
  px(148, bodyY + 18, 24, 28, black);

  const headX = laying ? 142 : 148;
  const headY = laying ? 84 : sit ? 50 + bob : 56 + bob;
  px(headX, headY, 44, 42, charcoal);
  px(headX + 8, headY - 10, 30, 16, "#303030");
  px(headX + 20, headY + 18, 24, 18, grey);
  px(headX + 28, headY + 26, 16, 10, grey);
  px(headX + 32, headY + 28, 8, 4, "#0d0d0d");
  px(headX + 29, headY + 13, 5, 5, eye);
  px(headX + 4, headY + 9, 12, 24, black);
  px(headX + 34, headY + 8, 10, 22, black);

  if (dex.pose !== "growl" && dex.pose !== "sleep") {
    px(headX + 35, headY + 35, 8, pant ? 13 : 8, tongue);
  }

  if (dex.pose === "sleep") {
    px(headX + 28, headY + 14, 8, 2, eye);
    px(194, 66 + (pant * -4), 8, 4, "#d8d4cc");
    px(207, 56 + (pant * -3), 5, 3, "#d8d4cc");
  }

  if (dex.pose === "growl") {
    px(headX + 34, headY + 35, 12, 3, "#e4dccd");
  }

  const legOffset = t % 2 === 0 ? 0 : 5;
  if (laying) {
    px(78, 129, 42, 10, black);
    px(124, 129, 42, 10, black);
  } else if (sit) {
    px(84, 124, 20, 28, black);
    px(136, 124, 20, 28, black);
  } else {
    px(82, 116 + legOffset, 16, 34 - legOffset, black);
    px(118, 116 - legOffset, 16, 34 + legOffset, black);
    px(150, 116 + legOffset, 16, 34 - legOffset, black);
  }

  px(47, bodyY + 18 + wag, 28, 10, black);

  if (dex.gear === "hardhat") {
    px(headX + 8, headY - 18, 30, 8, "#d9a928");
    px(headX + 5, headY - 12, 36, 6, "#b9871e");
  }

  if (dex.gear === "vest") {
    px(90, bodyY + 10, 18, 34, "#d78639");
    px(112, bodyY + 11, 8, 32, "#f0c65a");
  }

  if (dex.item === "leash" || dex.pose === "leash") {
    px(176, 120, 34, 4, "#8b5a3d");
    px(204, 112, 14, 14, "#8b5a3d");
  } else if (dex.item === "clipboard") {
    px(50, 104, 18, 26, "#a57d4e");
    px(54, 108, 10, 3, "#e8dfc7");
  } else if (dex.item === "wrench") {
    px(48, 118, 24, 5, "#9aa3a6");
    px(44, 114, 8, 8, "#9aa3a6");
  }

  ctx.restore();
}

function render(now) {
  chooseBehavior(now);
  moveDex(now);
  canvas.style.transform = `translate(${dex.x}px, ${dex.y}px)`;
  drawDog(now);

  moodText.textContent = dex.mood;
  behaviorText.textContent = dex.pose;
  itemText.textContent = dex.item === "none" ? "None" : dex.item;

  requestAnimationFrame(render);
}

function giveAttention() {
  dex.attentionUntil = performance.now() + 9000;
  idleRange.value = 0;
}

function walkDex() {
  dex.attentionUntil = performance.now() + 14000;
  dex.lastWalk = performance.now();
  idleRange.value = 0;
}

canvas.addEventListener("pointerdown", (event) => {
  dex.dragging = true;
  canvas.classList.add("dragging");
  canvas.setPointerCapture(event.pointerId);
});

canvas.addEventListener("pointermove", (event) => {
  const rect = workbench.getBoundingClientRect();
  dex.cursorX = event.clientX - rect.left;
  dex.cursorY = event.clientY - rect.top;
  if (!dex.dragging) return;
  dex.x = dex.cursorX - canvas.width / 2;
  dex.y = dex.cursorY - canvas.height / 2;
  walkDex();
});

canvas.addEventListener("pointerup", (event) => {
  dex.dragging = false;
  canvas.classList.remove("dragging");
  canvas.releasePointerCapture(event.pointerId);
});

document.addEventListener("pointermove", (event) => {
  const rect = workbench.getBoundingClientRect();
  dex.cursorX = event.clientX - rect.left;
  dex.cursorY = event.clientY - rect.top;
});

document.getElementById("attentionBtn").addEventListener("click", giveAttention);
document.getElementById("walkBtn").addEventListener("click", walkDex);
document.getElementById("notifyBtn").addEventListener("click", () => {
  dex.notificationUntil = performance.now() + 4200;
  notification.hidden = false;
  setTimeout(() => {
    notification.hidden = true;
  }, 3000);
});
document.getElementById("midnightBtn").addEventListener("click", () => {
  dex.midnightUntil = performance.now() + 12000;
});

setInterval(() => {
  idleRange.value = Math.min(90, Number(idleRange.value) + 1);
}, 60000);

requestAnimationFrame(render);
