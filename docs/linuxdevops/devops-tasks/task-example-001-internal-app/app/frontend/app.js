const TOKEN_KEY = "access_token";
const USER_KEY = "username";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUsername() {
  return localStorage.getItem(USER_KEY);
}

function setSession(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, username);
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/";
    return false;
  }
  return true;
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(path, { ...options, headers });
  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }

  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : "Request failed";
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return data;
}

function formatDate(iso) {
  return new Date(iso).toLocaleString();
}

function renderHeader(active) {
  const user = getUsername();
  const el = document.getElementById("site-header");
  if (!el) return;

  el.innerHTML = `
    <div><strong>Internal Messages</strong></div>
    <nav>
      ${user ? `<span class="nav-user">${user}</span>` : ""}
      ${user ? `<a href="/compose.html"${active === "compose" ? ' aria-current="page"' : ""}>New message</a>` : ""}
      ${user ? `<a href="/messages.html"${active === "messages" ? ' aria-current="page"' : ""}>My messages</a>` : ""}
      ${user ? `<a href="#" id="logout-link">Logout</a>` : ""}
    </nav>
  `;

  const logout = document.getElementById("logout-link");
  if (logout) {
    logout.addEventListener("click", (e) => {
      e.preventDefault();
      clearSession();
      window.location.href = "/";
    });
  }
}
