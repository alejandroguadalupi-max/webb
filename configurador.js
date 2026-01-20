document.getElementById("saveBtn").addEventListener("click", () => {
  const name = document.getElementById("restaurantInput").value.trim();
  const color = document.getElementById("primaryColor").value;

  if (name) {
    localStorage.setItem("restaurantName", name);
  }

  localStorage.setItem("primaryColor", color);

  // Ir a la web real
  window.location.href = "principal.html";
});
