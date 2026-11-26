// TaskManager: interfaz web que consume la API REST /api/tareas.
"use strict";

const API = "/api/tareas";
const ESTADOS = ["Pendiente", "En proceso", "Terminada"];
const estadoApp = { tareas: [], editandoId: null };

const $ = (selector) => document.querySelector(selector);
const slug = (texto) =>
  texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, "-");

// ----------------------------------------------------------------------------
// Utilidades
// ----------------------------------------------------------------------------
let temporizadorMensaje;
function mostrarMensaje(texto, tipo = "exito") {
  const caja = $("#mensaje");
  if (!caja) return;
  caja.textContent = texto;
  caja.className = `mensaje ${tipo}`;
  caja.hidden = false;
  clearTimeout(temporizadorMensaje);
  temporizadorMensaje = setTimeout(() => { caja.hidden = true; }, 3500);
}

async function peticion(url, opciones = {}) {
  const respuesta = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  let datos = null;
  try { datos = await respuesta.json(); } catch (_) { /* respuesta sin JSON */ }
  if (!respuesta.ok) {
    const detalle = datos && datos.detalles && datos.detalles.length
      ? datos.detalles.join(" ")
      : (datos && datos.error) || `Error ${respuesta.status}`;
    throw new Error(detalle);
  }
  return datos;
}

// ----------------------------------------------------------------------------
// Inicio
// ----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
});
