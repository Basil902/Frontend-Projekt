const userFeedbackMsg = document.getElementById("flashMsgDiv");


if (userFeedbackMsg){
    console.log(userFeedbackMsg)
    setTimeout(() => {
        userFeedbackMsg.style.display = "none";
    }, 5000);
    
}