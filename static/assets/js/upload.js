var reader = new FileReader();
var data = new FormData();
var xhr = new XMLHttpRequest(); 
var check_status_timer;

function readURL(input) {
    if (input.files && input.files[0]) {
  
      reader.onload = function(e) {
        $('.image-upload-wrap').hide();
  
        $('.file-upload-image').attr('src', e.target.result);
        $('.file-upload-content').show();
  
        $('.image-title').html(input.files[0].name);
      };
  
      reader.readAsDataURL(input.files[0]);
      data = new FormData()
      data.append("images", input.files[0])
  
    } else {
      removeUpload();
    }
  }
  
  function removeUpload() {
    $('.file-upload-input').replaceWith($('.file-upload-input').clone());
    $('.file-upload-content').hide();
    $('.image-upload-wrap').show();
  }
  $('.image-upload-wrap').bind('dragover', function () {
      $('.image-upload-wrap').addClass('image-dropping');
    });
    $('.image-upload-wrap').bind('dragleave', function () {
      $('.image-upload-wrap').removeClass('image-dropping');
  });

  function upload() {
    var xhr = new XMLHttpRequest(); 
  xhr.open("POST", 'http://'+window.location.host+"/predict");  
  xhr.send(data);
  xhr.onreadystatechange = function() { 
    // If the request completed, close the extension popup
    console.log(xhr.readyState,xhr.status,xhr.responseText)
    if(xhr.readyState == 4 && xhr.status == 200) {
    localStorage.setItem('upload_id',xhr.responseText);
    window.location.href = 'http://'+window.location.host+'/result';

  };
}
  }

  function upload_annotate() {
    var xhr = new XMLHttpRequest(); 
    xhr.open("POST", 'http://'+window.location.host+"/convert_annotate"); 
    xhr.responseType = 'blob'; 
    xhr.send(data);
    xhr.onreadystatechange = function() { 
      // If the request completed, close the extension popup
      if(xhr.readyState == 4 && xhr.status == 200) {
        console.log(xhr.response);
      localStorage.setItem('img',JSON.stringify(URL.createObjectURL(xhr.response)));
      localStorage.setItem('fromscratch','True')
      window.location.href = 'http://'+window.location.host+'/annotate';
  
    };
  }
    }




