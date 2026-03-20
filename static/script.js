function cutVideo() {
    const url = document.getElementById("url").value;
    const duration = document.getElementById("duration").value;
    const chapters = document.getElementById("chapters").value;
    const progress = document.getElementById("progress");

    progress.innerText = "⏳ Procesando...";

    fetch("/cut", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `url=${encodeURIComponent(url)}&duration=${duration}&chapters=${chapters}`
    })
    .then(res => res.json())
    .then(data => {
        progress.innerText = "✅ Cortado correctamente!";
        updateHist();
    });
}

function updateHist() {
    fetch("/historial")
        .then(res => res.json())
        .then(data => {
            const ul = document.getElementById("historial");
            ul.innerHTML = "";
            data.historial.forEach(line => {
                const li = document.createElement("li");
                li.innerHTML = line;
                ul.appendChild(li);
            });
        });
}

function clearHist() {
    fetch("/clear_historial")
        .then(() => updateHist());
}

function clearFolder() {
    fetch("/clear_folder")
        .then(() => updateHist());
}

// Actualizar historial al cargar la página
updateHist();