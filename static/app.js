/* MALLY CUTS v18 - CONTROLADOR DE HIPER-VELOCIDAD
   Lógica de Frontend para fragmentación asíncrona
*/

document.addEventListener('DOMContentLoaded', () => {
    console.log("⚡ MALLY ENGINE: Front-end listo.");
    
    // Si estamos en la página del editor, inicializamos el motor de corte
    const cutBtn = document.getElementById('start-cut-btn');
    if (cutBtn) {
        cutBtn.addEventListener('click', startMallyCut);
    }
});

/**
 * Ejecuta la fragmentación enviando la ruta al backend
 */
async function startMallyCut() {
    const statusLabel = document.getElementById('status');
    const videoPath = document.getElementById('video-path').value;
    const segmentSeconds = document.getElementById('seg').value;

    if (!videoPath) {
        alert("❌ ERROR: Falta la ruta del video maestro.");
        return;
    }

    // Cambiar estado a PROCESANDO (Estilo Neón)
    statusLabel.innerText = ">> STATUS: FRAGMENTANDO EN HI-SPEED...";
    statusLabel.style.color = "#bc13fe"; // Púrpura de proceso
    statusLabel.style.textShadow = "0 0 15px #bc13fe";

    try {
        const response = await fetch('/api/cut', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: videoPath,
                seconds: segmentSeconds
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // ÉXITO TOTAL
            statusLabel.innerText = ">> STATUS: ¡FRAGMENTACIÓN COMPLETADA!";
            statusLabel.style.color = "#00ff41"; // Verde Neón
            statusLabel.style.textShadow = "0 0 15px #00ff41";
            
            console.log("✅ Archivos generados en: " + data.folder);
            
            // Opcional: Mostrar alerta imperial
            showTerminalAlert(`ÉXITO: Clips creados en ${data.folder}`);
        } else {
            throw new Error("Fallo en el motor V10");
        }

    } catch (error) {
        console.error("❌ Error Crítico:", error);
        statusLabel.innerText = ">> STATUS: ERROR EN EL MOTOR V10";
        statusLabel.style.color = "#ff0000";
        statusLabel.style.textShadow = "0 0 15px #ff0000";
    }
}

/**
 * Una simple notificación estilo consola
 */
function showTerminalAlert(message) {
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.background = '#0a0a0a';
    notification.style.border = '1px solid #00ff41';
    notification.style.color = '#00ff41';
    notification.style.padding = '15px';
    notification.style.zIndex = '9999';
    notification.style.fontFamily = 'Courier New';
    notification.innerText = "[SYS]: " + message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}
