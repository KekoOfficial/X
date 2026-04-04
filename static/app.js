/**
 * MALLY CUTS V2000 - FRONTEND CORE
 * Gestiona la interacción entre la UI y el Motor de Termux
 */

const V2000 = {
    // --- SELECTORES ---
    form: document.getElementById('v2k-form'),
    input: document.getElementById('file-picker'),
    button: document.getElementById('launch-btn'),
    engineRoom: document.getElementById('engine-room'),
    statusText: document.querySelector('.status-msg'),

    // --- INICIALIZACIÓN ---
    init() {
        console.log("⚡ V2000 Core Initialized");
        this.checkSystemHealth();
    },

    // --- DISPARO DE PROCESO ---
    async ignite() {
        const file = this.input.files[0];
        if (!file) return;

        // 1. Optimización Visual
        this.button.style.display = 'none';
        this.engineRoom.style.display = 'block';
        this.updateStatus("🚀 PAQUETE RECIBIDO... SUBIENDO AL BUFFER");

        // 2. Preparar Datos (FormData para enviar el archivo)
        const formData = new FormData();
        formData.append('video_file', file);

        try {
            // Enviamos el video vía Fetch para no recargar la página y mantener el control
            const response = await fetch('/api/brutal-process', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.updateStatus("✅ MOTOR V2000 EN MARCHA<br>FRAGMENTANDO Y DISPARANDO A TELEGRAM");
                
                // Reset automático tras éxito
                setTimeout(() => this.resetUI(), 8000);
            } else {
                throw new Error("Fallo en la comunicación con el Core");
            }
        } catch (error) {
            this.updateStatus("❌ ERROR CRÍTICO: REVISA TERMUX");
            console.error(error);
            setTimeout(() => this.resetUI(), 5000);
        }
    },

    // --- TELEMETRÍA (Opcional: Consulta si el sistema está vivo) ---
    async checkSystemHealth() {
        try {
            const res = await fetch('/api/v2000/system-info');
            const data = await res.json();
            console.log("📊 System Health:", data);
        } catch (e) {
            console.warn("⚠️ No se pudo conectar con la telemetría");
        }
    },

    // --- UTILIDADES ---
    updateStatus(html) {
        this.statusText.innerHTML = html;
    },

    resetUI() {
        this.button.style.display = 'block';
        this.engineRoom.style.display = 'none';
        this.form.reset();
        this.updateStatus("<span class='blink'>PROCESO ASÍNCRONO ACTIVADO</span><br>FRAGMENTANDO EN 60s...<br>SUBIENDO A TELEGRAM...");
    }
};

// Arrancar sistema
document.addEventListener('DOMContentLoaded', () => V2000.init());
