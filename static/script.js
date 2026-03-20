const btnClearHist = document.getElementById("btnClearHist");
const btnClearFolder = document.getElementById("btnClearFolder");
const progressBar = document.getElementById("progressBar");
const form = document.getElementById("formCortar");

btnClearHist.onclick = () => {
    if(confirm("⚠️ Seguro quieres borrar todo el historial?")) {
        window.location.href="/borrar_historial";
    }
};
btnClearFolder.onclick = () => {
    if(confirm("⚠️ Seguro quieres borrar toda la carpeta de cortados?")) {
        window.location.href="/borrar_carpeta";
    }
};

// Barra de progreso (demo)
form.onsubmit = () => {
    progressBar.style.width = "0%";
    let percent = 0;
    const interval = setInterval(() => {
        percent += 5;
        progressBar.style.width = percent + "%";
        if(percent>=100) clearInterval(interval);
    }, 200);
};