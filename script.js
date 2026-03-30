// ─────────────────────────────────────────────────────────────────────────────
//  Rustic Garden — script.js
//  Lives in your GitHub Pages repo alongside index.html
//  Connects the frontend to your Azure Function App backend.
// ─────────────────────────────────────────────────────────────────────────────

// 🔧 Replace this with your actual Azure Function App URL after deployment.
//    Find it in Azure Portal → Function App → Overview → URL
//    It looks like: https://rustic-garden.azurewebsites.net
const AZURE_BASE_URL = "https://rustic-garden-api-bzhbh0gxf2ayh6ev.ukwest-01.azurewebsites.net/api";


// ─────────────────────────────────────────────
//  CONTACT FORM
//  Reads from a <form id="contactForm"> in your HTML.
//  Expects inputs with name="name", name="email", name="message"
// ─────────────────────────────────────────────
async function submitContact(event) {
  event.preventDefault();
  const form   = event.target;
  const btn    = form.querySelector("button[type=submit]");
  const status = document.getElementById("contactStatus");

  const payload = {
    name:    form.name.value.trim(),
    email:   form.email.value.trim(),
    message: form.message.value.trim(),
  };

  if (!payload.name || !payload.email || !payload.message) {
    showStatus(status, "Please fill in all fields.", "error");
    return;
  }

  btn.disabled    = true;
  btn.textContent = "Sending…";

  try {
    const res  = await fetch(`${AZURE_BASE_URL}/contact`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      showStatus(status, data.message || "Message sent!", "success");
      form.reset();
    } else {
      showStatus(status, data.error || "Something went wrong.", "error");
    }
  } catch (err) {
    console.error("Contact error:", err);
    showStatus(status, "Could not reach the server. Please try again.", "error");
  } finally {
    btn.disabled    = false;
    btn.textContent = "Send Message";
  }
}


// ─────────────────────────────────────────────
//  VOLUNTEER / JOIN PROGRAM FORM
//  Reads from a <form id="volunteerForm"> in your HTML.
//  Expects inputs with name="name", name="email",
//  name="role" (select), name="note" (optional textarea)
// ─────────────────────────────────────────────
async function submitVolunteer(event) {
  event.preventDefault();
  const form   = event.target;
  const btn    = form.querySelector("button[type=submit]");
  const status = document.getElementById("volunteerStatus");

  const payload = {
    name:  form.name.value.trim(),
    email: form.email.value.trim(),
    role:  form.role?.value || "General Volunteer",
    note:  form.note?.value.trim() || "",
  };

  if (!payload.name || !payload.email) {
    showStatus(status, "Name and email are required.", "error");
    return;
  }

  btn.disabled    = true;
  btn.textContent = "Applying…";

  try {
    const res  = await fetch(`${AZURE_BASE_URL}/volunteer`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      showStatus(status, data.message || "Application sent!", "success");
      form.reset();
    } else {
      showStatus(status, data.error || "Something went wrong.", "error");
    }
  } catch (err) {
    console.error("Volunteer error:", err);
    showStatus(status, "Could not reach the server. Please try again.", "error");
  } finally {
    btn.disabled    = false;
    btn.textContent = "Apply";
  }
}


// ─────────────────────────────────────────────
//  HELPER: show a status message below a form
// ─────────────────────────────────────────────
function showStatus(el, message, type) {
  if (!el) return;
  el.textContent        = message;
  el.style.marginTop    = "12px";
  el.style.padding      = "10px 16px";
  el.style.borderRadius = "6px";
  el.style.fontSize     = "0.9rem";
  el.style.fontWeight   = "500";

  if (type === "success") {
    el.style.background = "rgba(104, 147, 104, 0.15)";
    el.style.color      = "#689368";
    el.style.border     = "1px solid rgba(104, 147, 104, 0.4)";
  } else {
    el.style.background = "rgba(220, 80, 80, 0.12)";
    el.style.color      = "#e07070";
    el.style.border     = "1px solid rgba(220, 80, 80, 0.3)";
  }

  // Auto-clear after 6 seconds
  setTimeout(() => { el.textContent = ""; el.style = ""; }, 6000);
}


// ─────────────────────────────────────────────
//  BIND FORMS ON PAGE LOAD
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const contactForm   = document.getElementById("contactForm");
  const volunteerForm = document.getElementById("volunteerForm");

  if (contactForm)   contactForm.addEventListener("submit", submitContact);
  if (volunteerForm) volunteerForm.addEventListener("submit", submitVolunteer);
});
