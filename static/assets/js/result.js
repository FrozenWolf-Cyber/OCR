var data = new FormData();
var xhr = new XMLHttpRequest();
var check_status_timer;
var result;
var id ;
var frcnn = document.getElementById("frcnn");
var craft = document.getElementById("craft");
var tess = document.getElementById("tess");
var siamese = document.getElementById("siamese");
var convert = document.getElementById("convert");
var annotate = document.getElementById("annotate");
var user_output_field = document.getElementById("user_output");
var response_text = document.getElementById("response_text");

if("upload_id" in localStorage){
    check_status_timer = setInterval(check_status,300);
    id = localStorage.getItem('upload_id')
}

function getResult(){
    data = new FormData()
    data.append('id',id)
    xhr = new XMLHttpRequest(); 
    xhr.open("POST", "http://192.168.174.11:5000/model_result");  
    xhr.send(data); 
    xhr.onreadystatechange = function() { 

     if(xhr.readyState == 4 && xhr.status == 200) {
        data = JSON.parse(xhr.response);

        console.log(data);
        console.log(data['user_output']);
        annotate.classList.remove("grey");
        annotate.classList.add("orange");
        convert.classList.remove("orange");
        convert.classList.add("green");
        
        user_output_field.innerHTML = JSON.stringify(data['user_output'],null,1);
        localStorage.setItem('output',JSON.stringify(data['user_output'],null,1))
        response_text.innerHTML = "✅ It is done !!"

   data = new FormData()
   data.append('id',id)
   var xhr_ = new XMLHttpRequest(); 
   xhr_.open("POST", "http://192.168.174.11:5000/get_model_img"); 
   xhr_.responseType = 'blob'; 
   xhr_.send(data);
   xhr_.onreadystatechange = function() { 
     // If the request completed, close the extension popup
     if(xhr_.readyState == 4 && xhr_.status == 200) {
       console.log(xhr_.response);
     localStorage.setItem('img',JSON.stringify(URL.createObjectURL(xhr_.response)));
     localStorage.setItem('fromscratch','False')
   };

   }
   
   localStorage.removeItem("upload_id");
     }
}}

function downloadString(text, fileType, fileName) {
   var blob = new Blob([text], { type: fileType });
 
   var a = document.createElement('a');
   a.download = fileName;
   a.href = URL.createObjectURL(blob);
   a.dataset.downloadurl = [fileType, a.download, a.href].join(':');
   a.style.display = "none";
   document.body.appendChild(a);
   a.click();
   document.body.removeChild(a);
   setTimeout(function() { URL.revokeObjectURL(a.href); }, 1500);
 }

function download_txt(){
   output_str = user_output_field.innerHTML;
   downloadString(output_str, '.txt', 'output');
}

function check_status(){
    data = new FormData()
    data.append('id',id)
    xhr = new XMLHttpRequest(); 
    xhr.open("POST", "http://192.168.174.11:5000/status");  
    xhr.send(data); 
    var status = 0;
    xhr.onreadystatechange = function() { 
     if(xhr.readyState == 4 && xhr.status == 200) {
     status =  parseInt(xhr.responseText);
     console.log(status);

     if (status==2){
        frcnn.classList.add("active");
     }
     if (status==3){
        frcnn.classList.add("active");
        craft.classList.add("active");
     }
     if (status==4){
        frcnn.classList.add("active");
        craft.classList.add("active");         
        tess.classList.add("active");
     }
     if (status==5){
        frcnn.classList.add("active");
        craft.classList.add("active");         
        tess.classList.add("active");         
        siamese.classList.add("active");
     }

     if (status == 6){
        frcnn.classList.add("active");
        craft.classList.add("active");         
        tess.classList.add("active");         
        siamese.classList.add("active");         
        clearInterval(check_status_timer);
        console.log("Over");
        getResult();
      }
   };
   }

}

function gotoannotate(){
   window.location.href = 'http://'+window.location.host+'/annotate';
}