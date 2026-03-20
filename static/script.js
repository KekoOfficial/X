const cutBtn = document.getElementById("cut_btn");
const fileInput = document.getElementById("file");
const capDuration = document.getElementById("cap_duration");
const progressFill = document.getElementById("progress_fill");
const progressText = document.getElementById("progress_text");
const progressStatus = document.getElementById("progress_status");
const histList = document.getElementById("hist_list");

async function loadHist() {
    const res = await fetch("/get_hist");
    const data = await res.json();
    histList.innerHTML = "";
    data.hist.forEach(line => {
        const li = document.createElement("li");
        li.textContent = line.trim();
        histList.appendChild(li);
    });
}

cutBtn.onclick = async () => {
    if(!fileInput.files[0]) return alert("Selecciona un vídeo");
    const fd = new FormData();
    fd.append("file", fileInput.files[0]);
    fd.append("cap_duration", capDuration.value);

    progressFill.style.width = "0%";
    progressText.textContent = "0%";
    progressStatus.textContent = "";

    await fetch("/cut", {method:"POST", body:fd});

    // Polling para progreso
    const interval = setInterval(async ()=>{
        const res = await fetch("/progress");
        const data = await res.json();
        progressFill.style.width = data.percent + "%";
        progressText.textContent = data.percent + "%";
        progressStatus.textContent = data.status;

        if(data.status === "Listo"){
            clearInterval(interval);
            loadHist();
        }
    }, 500);
};

document.getElementById("clear_hist").onclick = async () => {
    await fetch("/clear_hist");
    loadHist();
};

document.getElementById("clear_folder").onclick = async () => {
    await fetch("/clear_folder");
    loadHist();
};

loadHist();