const source = new EventSource("/api/status");
source.onmessage = (e) => {
    document.getElementById('status-box').style.display = 'block';
    document.getElementById('msg').innerText = e.data;
    if(e.data.includes("✅")) setTimeout(() => location.reload(), 3000);
};

async function upload() {
    const file = document.getElementById('vid').files[0];
    const formData = new FormData();
    formData.append("video", file);
    
    document.getElementById('msg').innerText = "SUBIENDO AL SERVIDOR...";
    await fetch("/api/upload", { method: "POST", body: formData });
}
