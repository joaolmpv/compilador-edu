const BACKEND_URL = "http://localhost:5000";

async function loadMessage() {
  const el = document.getElementById("message");
  try {
    const response = await fetch(`${BACKEND_URL}/api/hello`);
    const data = await response.json();
    el.textContent = data.message;
  } catch (err) {
    el.textContent = "Não foi possível falar com o backend.";
    console.error(err);
  }
}

loadMessage();
