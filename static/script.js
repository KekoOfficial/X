const btnCortar = document.getElementById("btn_cortar");
const videosInput = document.getElementById("videos");
const capSelect = document.getElementById("cap_duration");
const progressFill = document.getElementById("progress_fill");
const progressText = document.getElementById("progress_text");
const videoList = document.getElementById("video_list");
const clearHistoryBtn = document.getElementById("clear_history");
const clearFolderBtn = document.getElementById("clear_folder");

btnCortar.addEventListener("click", () => {
    const files = videosInput.files;
    if(files.length === 0) return alert("Selecciona al menos un vídeo");
    
    const formData = new FormData();
    for(let f of files) formData.append("files", f);
    formData.append("cap_duration", capSelect.value);

    fetch("/upload", {method:"POST", body: formData})
    .then(res => res.json())
    .then(data => {
        alert("Vídeos cortados correctamente!");
        refreshList();
    });

    // Iniciar barra de progreso
    const interval = setInterval(() => {
        fetch("/progress").then(r=>r.json()).then(p=>{
            const percent = Math.round((p.done/p.total)*100) || 0;
            progressFill.style.width = percent + "%";
            progressText.textContent = p.status + ` (${percent}%)`;
            if(p.status === "Listo") clearInterval(interval);
        });
    }, 500);
});

function refreshList(){
    fetch("/").then(r=>r.text()).then(html=>{
        const parser = new DOMParser();
        const doc = parser.parseFromString(html,"text/html");
        const items = doc.querySelectorAll("#video_list li");
        videoList.innerHTML = "";
        items.forEach(i=>videoList.appendChild(i));
    });
}

clearHistoryBtn.addEventListener("click", ()=>{
    fetch("/clear_history").then(()=>refreshList());
});

clearFolderBtn.addEventListener("click", ()=>{
    fetch("/clear_folder").then(()=>refreshList());
});