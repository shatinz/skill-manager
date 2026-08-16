import './style.css';
import { OrbitScene } from './scene.js';
import { UIManager } from './ui.js';
import { ORBITAL_PLANS } from './plans.js';

document.addEventListener('DOMContentLoaded', () => {
  const canvasContainer = document.getElementById('webgl-canvas-container');
  if (!canvasContainer) return;

  let ui = null;

  // Initialize the 3D Orbit Scene with reactive callbacks
  const scene = new OrbitScene(canvasContainer, {
    onOrbitSelect: (plan) => {
      if (ui) {
        ui.openPlanModal(plan);
      }
    },
    onHoverChange: (data) => {
      if (ui) {
        ui.showHoverTooltip(data);
      }
    }
  });

  // Initialize UI Manager
  ui = new UIManager(scene);

  console.log("🚀 Shipien Orbital Matrix initialized successfully.");
});
