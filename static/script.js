document.addEventListener("DOMContentLoaded", () => {

    // ===================================
    // PROGRESS BAR
    // ===================================
    function updateProgress(percent) {
        const bar = document.querySelector(".progress-bar");
        if(bar){
            bar.style.width = percent + "%";
            bar.textContent = percent + "%";
        }
    }

    // ===================================
    // NOTIFICATIONS
    // ===================================
    function showNotification(message, type="success") {
        const notif = document.createElement("div");
        notif.className = `notification ${type}`;
        notif.textContent = message;
        document.body.appendChild(notif);
        setTimeout(()=>{ notif.style.opacity=1; notif.style.transform="translateY(0)"; },50);
        setTimeout(()=>{ notif.style.opacity=0; notif.style.transform="translateY(-20px)";
            setTimeout(()=>notif.remove(),600);
        },3000);
    }

    // ===================================
    // FORM SUBMISSION
    // ===================================
    const forms = ["linkForm","fileForm"];
    forms.forEach(id => {
        const form = document.getElementById(id);
        if(form){
            form.addEventListener("submit", e=>{
                e.preventDefault();
                updateProgress(0);
                showNotification("Procesando video...");
                let progress=0;
                const interval = setInterval(()=>{
                    if(progress>=100){
                        clearInterval(interval);
                        showNotification("Proceso completado!", "success");
                    }else{
                        progress += Math.floor(Math.random()*12);
                        if(progress>100) progress=100;
                        updateProgress(progress);
                    }
                },250);
                form.submit();
            });
        }
    });

    // ===================================
    // CLEAR HISTORY
    // ===================================
    const clearBtn = document.querySelector(".clear-btn");
    if(clearBtn){
        clearBtn.addEventListener("click", ()=>{
            if(confirm("¿Limpiar historial?")){
                fetch("/history",{method:"POST"})
                .then(()=>showNotification("Historial limpiado","success"))
                .catch(()=>showNotification("Error","error"));
            }
        });
    }

    // ===================================
    // BUTTON EFFECTS
    // ===================================
    document.querySelectorAll("button").forEach(btn=>{
        btn.addEventListener("mouseenter", ()=> btn.classList.add("pulse"));
        btn.addEventListener("mouseleave", ()=> btn.classList.remove("pulse"));
    });

});