export function loadCSS(id, path) {
  const old = document.querySelectorAll("link[data-page-css]");
  old.forEach(link => link.remove());

  if (!document.getElementById(id)) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = path +"?v="+new Date().getTime();
    link.id = id;
    link.setAttribute("data-page-css", "true");
    document.head.appendChild(link);
  }
}