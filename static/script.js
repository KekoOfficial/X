let uploadedFile = null;

document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('videoInput');
    if (!fileInput.files.length) return alert('Selecciona un vídeo');
    const file = fileInput.files[0];
    let formData = new FormData();
    formData.append('video', file);

    const res = await fetch('/upload', {method: 'POST', body: formData});
    const data = await res.json();
    if(data.filename) {
        uploadedFile = data.filename;
        alert('Vídeo subido correctamente');
    }
});

document.getElementById('cutBtn').addEventListener('click', async () => {
    if (!uploadedFile) return alert('Sube primero un vídeo');
    const duration = document.getElementById('chapterDuration').value;
    const res = await fetch('/cut', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({filename: uploadedFile, chapter_duration: duration})
    });
    const data = await res.json();
    if (data.status === 'success') {
        const downloadsDiv = document.getElementById('downloads');
        downloadsDiv.innerHTML = '';
        data.files.forEach(f => {
            const link = document.createElement('a');
            link.href = `/download/${f}`;
            link.textContent = f;
            link.download = f;
            downloadsDiv.appendChild(link);
            downloadsDiv.appendChild(document.createElement('br'));
        });
        alert('Vídeos cortados correctamente');
    }
});

document.getElementById('clearBtn').addEventListener('click', async () => {
    await fetch('/clear', {method: 'POST'});
    document.getElementById('downloads').innerHTML = '';
    alert('Descargas limpiadas');
});