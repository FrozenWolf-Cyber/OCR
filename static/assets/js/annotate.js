var target_img_sentence = document.getElementById("sentence_target");
var target_img_word = document.getElementById("word_target");
var annotate_output_sentence = document.getElementById("sentence_output");
var annotate_output_word = document.getElementById("word_output");
var n_sentence_annotations = 0
var n_words_annotations = {}
target_img_sentence.src = JSON.parse(localStorage.getItem('img'))
target_img_word.src = JSON.parse(localStorage.getItem('img'))

var anno = Annotorious.init({
   image: 'sentence_target'
 });

 var anno_word = Annotorious.init({
   image: 'word_target'
 });
 
 var each_output_template = {

          "id": 0,
          "text": "Registration No.",
          "box": [94,169,191,186],
          "linking": [[0,1]],
          "label": "question",
          "words": [
              {
                  "text": "Registration",
                  "box": [94,169,168,186]
              },
              {
                  "text": "No.",
                  "box": [170,169,191,183]
              }
          ]
      }

  var word_output_template = {

               "text": "Registration",
               "box": [94,169,168,186]
}


 var basic_template = { 
   "@context": "http://www.w3.org/ns/anno.jsonld",
   "id": "#id",
   "type": "Annotation",

   //text and tags and LINKS
   "body": [
   {
     "type": "TextualBody",
     "purpose": "commenting",
     "value": "This is where text translations are stored"
   },
   {
      "type": "TextualBody",
      "purpose": "commenting",
      "value": "This is where id is shown"
    }
],

   // annotate box pos
   "target": {
     "selector": {
        "source":"",
       "type": "FragmentSelector",
       "conformsTo": "http://www.w3.org/TR/media-frags/",
       "value": "xywh=pixel:100,1000,100,200" // x, y, width, heigth origin from top-left
     }
   }
 }

 var link_template =    {
   "type": "TextualBody",
   "purpose": "tagging",
   "value": "1"
 }

var label_template = {
   "type": "TextualBody",
   "purpose": "tagging",
   "value": "Question"
 }


function create_sentence_Annotationformat(){
   var instance_data = JSON.parse(localStorage.getItem('temp_output'))["form"]
   var instance_annotate_format = []
   for (let i in instance_data){
      var temp = JSON.parse(JSON.stringify(basic_template))

      temp["id"] = "#" + instance_data[i]["id"].toString()
      temp["body"][0]["value"] = instance_data[i]["text"] 
      temp["body"][1]["value"] = "Element ID (for linking): "+instance_data[i]["id"].toString()
      temp["body"].push(JSON.parse(JSON.stringify(label_template)))
      temp["body"][2]["value"] = instance_data[i]["label"]
      temp["target"]["selector"]["source"] = target_img_sentence.src
      var x, y, width, height
      var coord = instance_data[i]['box'].map(Number)
      var links = instance_data[i]['linking']

      for (let j in links){
         var temp_linking = link_template
         temp_linking["value"] = links[j][1]
         temp["body"].push(JSON.parse(JSON.stringify(temp_linking)))
      }

      width = (coord[2] - coord[0])
      height = (coord[3] - coord[1])
      x = coord[0]
      y = coord[1]

      temp["target"]["selector"]["value"] = `xywh=pixel:${x},${y},${width},${height}`
      instance_annotate_format.push(JSON.parse(JSON.stringify(temp)))
   }
   return instance_annotate_format
}

function create_word_Annotationformat(id){
   var instance_data = {};
   for (let j in JSON.parse(localStorage.getItem('temp_output'))["form"]){
      if (JSON.parse(localStorage.getItem('temp_output'))["form"][j]["id"] == id.toString()){
          instance_data = JSON.parse(localStorage.getItem('temp_output'))["form"][id]["words"]
          word_loc_ref = JSON.parse(localStorage.getItem('temp_output'))["form"][id]["box"].map(Number)
      }
   }

   var instance_annotate_format = []
   for (let i in instance_data){
      var temp = JSON.parse(JSON.stringify(basic_template))
      var coord = instance_data[i]['box'].map(Number)
      temp["id"] = "#"+id.toString()+"_" + i.toString()
      temp["body"][0]["value"] = instance_data[i]["text"]
      
      width = (coord[2] - coord[0])
      height = (coord[3] - coord[1])
      x = coord[0]
      y = coord[1]

      temp["target"]["selector"]["value"] = `xywh=pixel:${x},${y},${width},${height}`
      instance_annotate_format.push(JSON.parse(JSON.stringify(temp)))
   }
   return instance_annotate_format
}
function combine_annotations(sentence,word,subcreation=false){
   var temp_basic = each_output_template
   temp_basic["id"] = parseInt(sentence["id"].slice(1))
   temp_basic["text"] = sentence["body"][0]["value"]
   temp_basic["label"] = sentence["body"][1]["value"]
   temp_basic["linking"] = []

   for (var x=2;x<sentence["body"].length;x++){
      temp_basic["linking"].push([temp_basic["id"], sentence["body"][x]["value"]])
   }
   var x_min, y_min, x_max, y_max
   var values = sentence["target"]["selector"]["value"].slice(11).split(",").map(Number)
   x_min = values[0]
   y_min = values[1]
   x_max = x_min + values[2]
   y_max = y_min + values[3]

   temp_basic["box"] = [x_min,y_min,x_max,y_max]
   temp_basic["words"] = []
   for (y in word){
      var each_word = word_output_template
      if (!subcreation){
         each_word["text"] = word[y]["body"][0]["value"]
      }
      else{
         each_word["text"] = word[y]["body"]["value"]
      }
      var x_min, y_min, x_max, y_max
      var values = word[y]["target"]["selector"]["value"].slice(11).split(",").map(Number)
      x_min = values[0]
      y_min = values[1]
      x_max = x_min + values[2]
      y_max = y_min + values[3]
   
      each_word["box"] = [x_min,y_min,x_max,y_max]
      temp_basic["words"].push(JSON.parse(JSON.stringify(each_word)))
   }
   return temp_basic
}
function create_outputformat(type,id,annotatation,subcreation=false){
   id = parseInt(id.slice(1))
   var prev_data = JSON.parse(localStorage.getItem('temp_output'))["form"]
   instance_word_annotation = anno_word.getAnnotations()
   instance_sentence_annotatation = anno.getAnnotations()
   result = []
   map_dict = {}
   result = JSON.parse(JSON.stringify(prev_data))
   if (type == 2){ //modify no change in length
      for (i in instance_sentence_annotatation){
         for (j in result){
            if (parseInt(instance_sentence_annotatation[i]["id"].slice(1)) == id && result[j]["id"] == id){
               result[j] = combine_annotations(instance_sentence_annotatation[i],instance_word_annotation,subcreation)
               return {"form":result}
            }
         }

      }
   }

   if (type==1){ //addition
      new_word = JSON.parse(JSON.stringify(annotatation)) //self as starting
      new_word["body"] = new_word["body"][0]
      new_word["id"] = "#"+id.toString()+"_"+0
      n_words_annotations[id] = 1
      result.push(combine_annotations(annotatation,[new_word],subcreation=subcreation))
      return {"form":result}
   }

   if (type==0){ //deletion
         for (j in result){
            if (result[j]["id"] == id){ 
            result.splice(id, 1)
            return {"form":result}
            }
         }
   }

}

function updateForms(form){
   localStorage.setItem('temp_output',JSON.stringify(form,null,1))
   var starting_anno = create_sentence_Annotationformat()
   anno.setAnnotations(starting_anno)
   annotate_output_sentence.innerHTML = localStorage.getItem('temp_output')
   annotate_output_word.innerHTML = localStorage.getItem('temp_output_word')

}

function gotoannotate(){
    window.location.href = 'http://'+window.location.host+'/upload_annotate';
 }

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
    output_str = localStorage.getItem('temp_output');
    downloadString(output_str, '.txt', 'output');
 }

 function updateWordannotate(id){
   var temp_form = JSON.parse(localStorage.getItem('temp_output'))["form"][id]
   localStorage.setItem('temp_output_word',JSON.stringify(temp_form,null,1))
   annotate_output_word.innerHTML = localStorage.getItem('temp_output_word')
 }

anno.on('selectAnnotation', function(annotation, element) {
   word_annotations = create_word_Annotationformat(parseInt(annotation["id"].slice(1)))
   anno_word.setAnnotations(word_annotations)
   if(word_annotations.length!=0){
      anno_word.selectAnnotation(word_annotations[0])
   }
   updateWordannotate(parseInt(annotation["id"].slice(1)))
 });


 anno.on('createAnnotation', function(annotation, overrideId) {
   overrideId("#"+n_sentence_annotations.toString());
   annotation["id"] = "#"+n_sentence_annotations.toString()
   if (annotation["body"].length == 1){
      annotation["body"].push(JSON.parse(JSON.stringify(annotation["body"][0])))
      annotation["body"].push(JSON.parse(JSON.stringify(annotation["body"][0])))
      annotation["body"][1]["purpose"] = "tagging"
      annotation["body"][2]["value"] = "others"
   }
   if (annotation["body"].length == 2){
      annotation["body"].push(JSON.parse(JSON.stringify(annotation["body"][0])))
      annotation["body"][1]["purpose"] = "tagging"
      annotation["body"][2]["value"] = "others"
   }

   n_words_annotations[n_sentence_annotations] = 0
   n_sentence_annotations+=1
   updateForms(create_outputformat(1,"#"+(n_sentence_annotations-1).toString(),JSON.parse(JSON.stringify(annotation)),true)) //creation
      //update forms //add a test child and increment
 });

 anno.on('deleteAnnotation', function(annotation) {
   updateForms(create_outputformat(0,annotation["id"],JSON.parse(JSON.stringify(annotation)))) //deletion
   
 });

 anno.on('updateAnnotation', function(annotation, previous) {
  updateForms(create_outputformat(2,annotation["id"],JSON.parse(JSON.stringify(annotation)))) //modification
   //update forms
 });

 anno_word.on('createAnnotation', function(annotation, overrideId) {
    var a = anno_word.getAnnotations()
    var parent_annotation = annotation;
    if (a.lenght>1){
      parent_annotation = anno.getAnnotationById(a[1]["id"].split('_')[0])
    }
    else{
       var b = anno.getSelected()
       if (b.length!=0){
          parent_annotation = b
       }
    }
   updateForms(create_outputformat(2,parent_annotation["id"],JSON.parse(JSON.stringify(parent_annotation)),true))
   overrideId("#"+n_words_annotations[parseInt(parent_annotation["id"].slice(1))])
   n_words_annotations[parseInt(parent_annotation["id"].slice(1))] +=1
   updateWordannotate(parseInt(parent_annotation["id"].slice(1)))
    //update forms
  });

  anno_word.on('deleteAnnotation', function(annotation) {
   var a = anno_word.getAnnotations()
   var parent_annotation = annotation;
   if (a.lenght!=0){
     parent_annotation = anno.getAnnotationById(a[0]["id"].split('_')[0])
   }
   else{
      var b = anno.getSelected()
      if (b.length!=0){
         parent_annotation = b
      }
   }
  updateForms(create_outputformat(2,parent_annotation["id"],JSON.parse(JSON.stringify(parent_annotation))))
  fillEmptyBoxes()
  updateWordannotate(parseInt(parent_annotation["id"].slice(1)))
 });

 anno_word.on('updateAnnotation', function(annotation, previous) {
   var a = anno_word.getAnnotations()
   var parent_annotation = annotation;
   if (a.lenght!=0){
     parent_annotation = anno.getAnnotationById(a[0]["id"].split('_')[0])
   }
   else{
      var b = anno.getSelected()
      if (b.length!=0){
         parent_annotation = b
      }
   }
  updateForms(create_outputformat(2,parent_annotation["id"],JSON.parse(JSON.stringify(parent_annotation))))
  updateWordannotate(parseInt(parent_annotation["id"].slice(1)))
   //update forms
 });


 if (localStorage.getItem('fromscratch')=='False'){
   localStorage.setItem('temp_output',localStorage.getItem('output'))
}
else {
   localStorage.setItem('temp_output',JSON.stringify({"form":[each_output_template]},null,1))
   
}
localStorage.setItem('temp_output_word',"Select a sentence")

function fillEmptyBoxes(){
var result = JSON.parse(localStorage.getItem('temp_output'))["form"]
for (n_sentences in result){
   if (result[n_sentences]["words"].length == 0){
      result[n_sentences]["words"].push({"box":result[n_sentences]["box"], "text":result[n_sentences]["text"]})
   }
}
updateForms({"form":result})
}

fillEmptyBoxes()

annotate_output_sentence.innerHTML = localStorage.getItem('temp_output')
annotate_output_word.innerHTML = localStorage.getItem('temp_output_word')

 var starting_anno = create_sentence_Annotationformat()
 anno.setAnnotations(starting_anno)

 n_sentence_annotations = starting_anno.length

 for (i in starting_anno){
    n_words_annotations[parseInt(starting_anno[i]["id"].slice(1))] = create_word_Annotationformat(parseInt(starting_anno[i]["id"].slice(1))).length 
 }

n_sentence_annotations = anno.getAnnotations().length





// var target_img_sentence = document.getElementById("sentence_target");
// var target_img_word = document.getElementById("word_target");
// var annotate_output_sentence = document.getElementById("sentence_output");
// var annotate_output_word = document.getElementById("word_output");
// var n_sentence_annotations = 0
// var n_words_annotations = {}
// target_img_sentence.src = JSON.parse(localStorage.getItem('img'))
// target_img_word.src = JSON.parse(localStorage.getItem('img'))

// var anno = Annotorious.init({
//    image: 'sentence_target'
//  });

//  var anno_word = Annotorious.init({
//    image: 'word_target'
//  });
 
//  var each_output_template = {

//           "id": 0,
//           "text": "Registration No.",
//           "box": [94,169,191,186],
//           "linking": [[0,1]],
//           "label": "question",
//           "words": [
//               {
//                   "text": "Registration",
//                   "box": [94,169,168,186]
//               },
//               {
//                   "text": "No.",
//                   "box": [170,169,191,183]
//               }
//           ]
//       }

//   var word_output_template = {

//                "text": "Registration",
//                "box": [94,169,168,186]
// }


//  var basic_template = { 
//    "@context": "http://www.w3.org/ns/anno.jsonld",
//    "id": "#id",
//    "type": "Annotation",

//    //text and tags and LINKS
//    "body": [
//    {
//      "type": "TextualBody",
//      "purpose": "commenting",
//      "value": "This is where text translations are stored"
//    }],

//    // annotate box pos
//    "target": {
//      "selector": {
//         "source":"",
//        "type": "FragmentSelector",
//        "conformsTo": "http://www.w3.org/TR/media-frags/",
//        "value": "xywh=pixel:100,1000,100,200" // x, y, width, heigth origin from top-left
//      }
//    }
//  }

//  var link_template =    {
//    "type": "TextualBody",
//    "purpose": "tagging",
//    "value": "1"
//  }

// var label_template = {
//    "type": "TextualBody",
//    "purpose": "tagging",
//    "value": "Question"
//  }


// function create_sentence_Annotationformat(){
//    var instance_data = JSON.parse(localStorage.getItem('temp_output'))["form"]
//    var instance_annotate_format = []
//    for (let i in instance_data){
//       var temp = JSON.parse(JSON.stringify(basic_template))

//       temp["id"] = "#" + instance_data[i]["id"].toString()
//       temp["body"][0]["value"] = instance_data[i]["text"] 
//       temp["body"].push(JSON.parse(JSON.stringify(label_template)))
//       temp["body"][1]["value"] = instance_data[i]["label"]
//       temp["target"]["selector"]["source"] = target_img_sentence.src
//       var x, y, width, height
//       var coord = instance_data[i]['box'].map(Number)
//       var links = instance_data[i]['linking']

//       for (let j in links){
//          var temp_linking = link_template
//          temp_linking["value"] = links[j][1]
//          temp["body"].push(JSON.parse(JSON.stringify(temp_linking)))
//       }

//       width = (coord[2] - coord[0])
//       height = (coord[3] - coord[1])
//       x = coord[0]
//       y = coord[1]

//       temp["target"]["selector"]["value"] = `xywh=pixel:${x},${y},${width},${height}`
//       instance_annotate_format.push(JSON.parse(JSON.stringify(temp)))
//    }
//    return instance_annotate_format
// }

// function create_word_Annotationformat(id){
//    var instance_data = {};
//    for (let j in JSON.parse(localStorage.getItem('temp_output'))["form"]){
//       if (JSON.parse(localStorage.getItem('temp_output'))["form"][j]["id"] == id.toString()){
//           instance_data = JSON.parse(localStorage.getItem('temp_output'))["form"][id]["words"]
//           word_loc_ref = JSON.parse(localStorage.getItem('temp_output'))["form"][id]["box"].map(Number)
//       }
//    }

//    var instance_annotate_format = []
//    for (let i in instance_data){
//       var temp = JSON.parse(JSON.stringify(basic_template))
//       var coord = instance_data[i]['box'].map(Number)
//       temp["id"] = "#"+id.toString()+"_" + i.toString()
//       temp["body"][0]["value"] = instance_data[i]["text"]
      
//       width = (coord[2] - coord[0])
//       height = (coord[3] - coord[1])
//       x = coord[0]
//       y = coord[1]

//       temp["target"]["selector"]["value"] = `xywh=pixel:${x},${y},${width},${height}`
//       instance_annotate_format.push(JSON.parse(JSON.stringify(temp)))
//    }
//    return instance_annotate_format
// }
// function combine_annotations(sentence,word,subcreation=false){
//    var temp_basic = each_output_template
//    temp_basic["id"] = parseInt(sentence["id"].slice(1))
//    temp_basic["text"] = sentence["body"][0]["value"]
//    temp_basic["label"] = sentence["body"][1]["value"]
//    temp_basic["linking"] = []

//    for (var x=2;x<sentence["body"].length;x++){
//       temp_basic["linking"].push([temp_basic["id"], sentence["body"][x]["value"]])
//    }
//    var x_min, y_min, x_max, y_max
//    var values = sentence["target"]["selector"]["value"].slice(11).split(",").map(Number)
//    x_min = values[0]
//    y_min = values[1]
//    x_max = x_min + values[2]
//    y_max = y_min + values[3]

//    temp_basic["box"] = [x_min,y_min,x_max,y_max]
//    temp_basic["words"] = []
//    for (y in word){
//       var each_word = word_output_template
//       if (!subcreation){
//          each_word["text"] = word[y]["body"][0]["value"]
//       }
//       else{
//          each_word["text"] = word[y]["body"]["value"]
//       }
//       var x_min, y_min, x_max, y_max
//       var values = word[y]["target"]["selector"]["value"].slice(11).split(",").map(Number)
//       x_min = values[0]
//       y_min = values[1]
//       x_max = x_min + values[2]
//       y_max = y_min + values[3]
   
//       each_word["box"] = [x_min,y_min,x_max,y_max]
//       temp_basic["words"].push(JSON.parse(JSON.stringify(each_word)))
//    }
//    return temp_basic
// }
// function create_outputformat(type,id,annotatation,subcreation=false){
//    id = parseInt(id.slice(1))
//    var prev_data = JSON.parse(localStorage.getItem('temp_output'))["form"]
//    instance_word_annotation = anno_word.getAnnotations()
//    instance_sentence_annotatation = anno.getAnnotations()
//    result = []
//    map_dict = {}
//    result = JSON.parse(JSON.stringify(prev_data))
//    if (type == 2){ //modify no change in length
//       for (i in instance_sentence_annotatation){
//          for (j in result){
//             if (parseInt(instance_sentence_annotatation[i]["id"].slice(1)) == id && result[j]["id"] == id){
//                result[j] = combine_annotations(instance_sentence_annotatation[i],instance_word_annotation,subcreation)
//                return {"form":result}
//             }
//          }

//       }
//    }

//    if (type==1){ //addition
//       new_word = JSON.parse(JSON.stringify(annotatation)) //self as starting
//       new_word["body"] = new_word["body"][0]
//       new_word["id"] = "#"+id.toString()+"_"+0
//       n_words_annotations[id] = 1
//       result.push(combine_annotations(annotatation,[new_word],subcreation=subcreation))
//       return {"form":result}
//    }

//    if (type==0){ //deletion
//          for (j in result){
//             if (result[j]["id"] == id){ 
//             result.splice(id, 1)
//             return {"form":result}
//             }
//          }
//    }

// }

// function updateForms(form){
//    localStorage.setItem('temp_output',JSON.stringify(form,null,1))
//    var starting_anno = create_sentence_Annotationformat()
//    anno.setAnnotations(starting_anno)
//    annotate_output_sentence.innerHTML = localStorage.getItem('temp_output')
//    annotate_output_word.innerHTML = localStorage.getItem('temp_output_word')

// }

// function gotoannotate(){
//     window.location.href = 'http://'+window.location.host+'/upload_annotate';
//  }

//  function downloadString(text, fileType, fileName) {
//     var blob = new Blob([text], { type: fileType });
  
//     var a = document.createElement('a');
//     a.download = fileName;
//     a.href = URL.createObjectURL(blob);
//     a.dataset.downloadurl = [fileType, a.download, a.href].join(':');
//     a.style.display = "none";
//     document.body.appendChild(a);
//     a.click();
//     document.body.removeChild(a);
//     setTimeout(function() { URL.revokeObjectURL(a.href); }, 1500);
//   }
 
//  function download_txt(){
//     output_str = localStorage.getItem('temp_output');
//     downloadString(output_str, '.txt', 'output');
//  }

//  function updateWordannotate(id){
//    var temp_form = JSON.parse(localStorage.getItem('temp_output'))["form"][id]
//    localStorage.setItem('temp_output_word',JSON.stringify(temp_form,null,1))
//    annotate_output_word.innerHTML = localStorage.getItem('temp_output_word')
//  }

// anno.on('selectAnnotation', function(annotation, element) {
//    word_annotations = create_word_Annotationformat(parseInt(annotation["id"].slice(1)))
//    anno_word.setAnnotations(word_annotations)
//    if(word_annotations.length!=0){
//       anno_word.selectAnnotation(word_annotations[0])
//    }
//    updateWordannotate(parseInt(annotation["id"].slice(1)))
//  });


//  anno.on('createAnnotation', function(annotation, overrideId) {
//    overrideId("#"+n_sentence_annotations.toString());
//    annotation["id"] = "#"+n_sentence_annotations.toString()
//    if (annotation["body"].length == 1){
//       annotation["body"].push(JSON.parse(JSON.stringify(annotation["body"][0])))
//       annotation["body"].push(JSON.parse(JSON.stringify(annotation["body"][0])))
//       annotation["body"][1]["purpose"] = "tagging"
//       annotation["body"][2]["value"] = "others"
//    }
//    if (annotation["body"].length == 2){
//       annotation["body"].push(JSON.parse(JSON.stringify(annotation["body"][0])))
//       annotation["body"][1]["purpose"] = "tagging"
//       annotation["body"][2]["value"] = "others"
//    }

//    n_words_annotations[n_sentence_annotations] = 0
//    n_sentence_annotations+=1
//    updateForms(create_outputformat(1,"#"+(n_sentence_annotations-1).toString(),JSON.parse(JSON.stringify(annotation)),true)) //creation
//       //update forms //add a test child and increment
//  });

//  anno.on('deleteAnnotation', function(annotation) {
//    updateForms(create_outputformat(0,annotation["id"],JSON.parse(JSON.stringify(annotation)))) //deletion
   
//  });

//  anno.on('updateAnnotation', function(annotation, previous) {
//   updateForms(create_outputformat(2,annotation["id"],JSON.parse(JSON.stringify(annotation)))) //modification
//    //update forms
//  });

//  anno_word.on('createAnnotation', function(annotation, overrideId) {
//     var a = anno_word.getAnnotations()
//     var parent_annotation = annotation;
//     if (a.lenght>1){
//       parent_annotation = anno.getAnnotationById(a[1]["id"].split('_')[0])
//     }
//     else{
//        var b = anno.getSelected()
//        if (b.length!=0){
//           parent_annotation = b
//        }
//     }
//    updateForms(create_outputformat(2,parent_annotation["id"],JSON.parse(JSON.stringify(parent_annotation)),true))
//    overrideId("#"+n_words_annotations[parseInt(parent_annotation["id"].slice(1))])
//    n_words_annotations[parseInt(parent_annotation["id"].slice(1))] +=1
//    updateWordannotate(parseInt(parent_annotation["id"].slice(1)))
//     //update forms
//   });

//   anno_word.on('deleteAnnotation', function(annotation) {
//    var a = anno_word.getAnnotations()
//    var parent_annotation = annotation;
//    if (a.lenght!=0){
//      parent_annotation = anno.getAnnotationById(a[0]["id"].split('_')[0])
//    }
//    else{
//       var b = anno.getSelected()
//       if (b.length!=0){
//          parent_annotation = b
//       }
//    }
//   updateForms(create_outputformat(2,parent_annotation["id"],JSON.parse(JSON.stringify(parent_annotation))))
//   fillEmptyBoxes()
//   updateWordannotate(parseInt(parent_annotation["id"].slice(1)))
//  });

//  anno_word.on('updateAnnotation', function(annotation, previous) {
//    var a = anno_word.getAnnotations()
//    var parent_annotation = annotation;
//    if (a.lenght!=0){
//      parent_annotation = anno.getAnnotationById(a[0]["id"].split('_')[0])
//    }
//    else{
//       var b = anno.getSelected()
//       if (b.length!=0){
//          parent_annotation = b
//       }
//    }
//   updateForms(create_outputformat(2,parent_annotation["id"],JSON.parse(JSON.stringify(parent_annotation))))
//   updateWordannotate(parseInt(parent_annotation["id"].slice(1)))
//    //update forms
//  });


//  if (localStorage.getItem('fromscratch')=='False'){
//    localStorage.setItem('temp_output',localStorage.getItem('output'))
// }
// else {
//    localStorage.setItem('temp_output',JSON.stringify({"form":[each_output_template]},null,1))
   
// }
// localStorage.setItem('temp_output_word',"Select a sentence")

// function fillEmptyBoxes(){
// var result = JSON.parse(localStorage.getItem('temp_output'))["form"]
// for (n_sentences in result){
//    if (result[n_sentences]["words"].length == 0){
//       result[n_sentences]["words"].push({"box":result[n_sentences]["box"], "text":result[n_sentences]["text"]})
//    }
// }
// updateForms({"form":result})
// }

// fillEmptyBoxes()

// annotate_output_sentence.innerHTML = localStorage.getItem('temp_output')
// annotate_output_word.innerHTML = localStorage.getItem('temp_output_word')

//  var starting_anno = create_sentence_Annotationformat()
//  anno.setAnnotations(starting_anno)

//  n_sentence_annotations = starting_anno.length

//  for (i in starting_anno){
//     n_words_annotations[parseInt(starting_anno[i]["id"].slice(1))] = create_word_Annotationformat(parseInt(starting_anno[i]["id"].slice(1))).length 
//  }

// n_sentence_annotations = anno.getAnnotations().length





