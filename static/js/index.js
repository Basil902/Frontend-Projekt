document.addEventListener("DOMContentLoaded", () => {
    const closeBtn = document.querySelector(".closeBtn");
    const flashDiv = document.getElementById("flashMsgDiv");

    if (closeBtn && flashDiv){
        closeBtn.addEventListener("click", () => flashDiv.remove());
    }
})