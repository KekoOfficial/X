function uploadCut(){
    let files = document.getElementById("local_files").files;
    let dur = document.getElementById("cap_duration").value;
    let form = new FormData();
    for(let i=0;i<files.length;i++) form.append("files", files[i]);
    form.append("cap_duration", dur);
    fetch("/upload_cut", {method:"POST", body: form}).then(res=>res.json()).then(data=>{
        alert(data.message);
        setTimeout(refreshList,2000);
    });
}

function urlCut(){
    let url = document.getElementById("video_url").value;
    let dur = document.getElementById("cap_duration_url").value;
    fetch("/url_cut", {method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({url:url, cap_duration: dur})
    }).then(res=>res.json()).then(data=>{
        alert(data.message);
        setTimeout(refreshList,5000);
    });
}

function refreshList(){
    fetch("/").then(res=>res.text()).then(html=>{
        let parser = new DOMParser();
        let doc = parser.parseFromString(html,"text/html");
        document.getElementById("video_list").innerHTML = doc.getElementById("video_list").innerHTML;
    });
}

function clearFolder(){
    fetch("/clear_folder",{method:"POST"}).then(res=>res.json()).then(data=>{
        alert("Carpeta y historial limpiados!");
        refreshList();
    });
}