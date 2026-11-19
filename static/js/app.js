// Cierra automáticamente los mensajes de éxito después de 5 segundos
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".mensajes .alert-success, .mensajes .alert-info").forEach((el) => {
    setTimeout(() => bootstrap.Alert.getOrCreateInstance(el).close(), 5000);
  });
  // Activa los tooltips de Bootstrap
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => new bootstrap.Tooltip(el));
});
