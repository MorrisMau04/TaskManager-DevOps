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
// RF02: Consultar tareas
// ----------------------------------------------------------------------------
async function cargarTareas() {
  try {
    estadoApp.tareas = await peticion(API);
    renderizar();
  } catch (e) {
    mostrarMensaje(`No se pudieron cargar las tareas: ${e.message}`, "error");
  }
}

function tareasVisibles() {
  return estadoApp.tareas;
}

function actualizarContadores() {
  const contar = (estado) => estadoApp.tareas.filter((t) => t.estado === estado).length;
  $("#total-todas").textContent = estadoApp.tareas.length;
  $("#total-pendiente").textContent = contar("Pendiente");
  $("#total-en-proceso").textContent = contar("En proceso");
  $("#total-terminada").textContent = contar("Terminada");
}

function boton(texto, accion, clase = "") {
  const b = document.createElement("button");
  b.type = "button";
  b.className = `boton pequeno ${clase}`.trim();
  b.dataset.accion = accion;
  b.textContent = texto;
  return b;
}

function crearTarjeta(tarea) {
  const li = document.createElement("li");
  li.className = `tarea prioridad-${slug(tarea.prioridad)} estado-${slug(tarea.estado)}`;
  li.dataset.id = tarea.id;
  li.innerHTML = `
    <div class="tarea-cabecera">
      <h3 class="tarea-nombre"></h3>
      <span class="badge badge-prioridad"></span>
    </div>
    <p class="tarea-descripcion"></p>
    <div class="tarea-pie">
      <span class="tarea-meta"></span>
      <div class="tarea-acciones"></div>
    </div>`;
  li.querySelector(".tarea-nombre").textContent = tarea.nombre;
  const badge = li.querySelector(".badge-prioridad");
  badge.textContent = `Prioridad ${tarea.prioridad.toLowerCase()}`;
  badge.classList.add(`p-${slug(tarea.prioridad)}`);
  const descripcion = li.querySelector(".tarea-descripcion");
  descripcion.textContent = tarea.descripcion || "Sin descripción";
  if (!tarea.descripcion) descripcion.classList.add("tenue");
  li.querySelector(".tarea-meta").textContent = `#${tarea.id} · ${tarea.actualizada_en}`;

  const acciones = li.querySelector(".tarea-acciones");
  const etiquetaEstado = document.createElement("span");
  etiquetaEstado.className = `badge badge-estado e-${slug(tarea.estado)}`;
  etiquetaEstado.textContent = tarea.estado;
  acciones.append(etiquetaEstado);
  return li;
}

function renderizar() {
  const lista = $("#lista-tareas");
  const visibles = tareasVisibles();
  lista.replaceChildren(...visibles.map(crearTarjeta));
  $("#sin-tareas").hidden = visibles.length > 0;
  actualizarContadores();
}

// ----------------------------------------------------------------------------
// RF01: Registrar tareas (y RF03: editar, con el mismo formulario)
// ----------------------------------------------------------------------------
function leerFormulario() {
  const form = $("#formulario-tarea");
  return {
    nombre: form.nombre.value.trim(),
    descripcion: form.descripcion.value.trim() || null,
    prioridad: form.prioridad.value,
    estado: form.estado.value,
  };
}

function limpiarFormulario() {
  const form = $("#formulario-tarea");
  form.reset();
  form.prioridad.value = "Media";
  $("#error-nombre").textContent = "";
  form.nombre.removeAttribute("aria-invalid");
  estadoApp.editandoId = null;
  $("#titulo-formulario").textContent = "Nueva tarea";
  $("#boton-guardar").textContent = "Guardar tarea";
}

async function guardarTarea(evento) {
  evento.preventDefault();
  const datos = leerFormulario();
  const form = $("#formulario-tarea");
  if (!datos.nombre) {
    $("#error-nombre").textContent = "El nombre de la tarea es obligatorio.";
    form.nombre.setAttribute("aria-invalid", "true");
    form.nombre.focus();
    return;
  }
  try {
    let resultado;
      resultado = await peticion(API, { method: "POST", body: JSON.stringify(datos) });
    mostrarMensaje(resultado.mensaje);
    limpiarFormulario();
    await cargarTareas();
  } catch (e) {
    mostrarMensaje(e.message, "error");
  }
}

// ----------------------------------------------------------------------------
// Inicio
// ----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  $("#formulario-tarea").addEventListener("submit", guardarTarea);
  $("#nombre").addEventListener("input", () => {
    $("#error-nombre").textContent = "";
    $("#nombre").removeAttribute("aria-invalid");
  });
  const lista = $("#lista-tareas");
  lista.addEventListener("click", (evento) => {
    const control = evento.target.closest("button[data-accion]");
    if (!control) return;
    const id = Number(control.closest(".tarea").dataset.id);
  });
  cargarTareas();
});
