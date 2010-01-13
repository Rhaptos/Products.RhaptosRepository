String.prototype.trim = function () {
    return this.replace(/^\s*(\S*(\s+\S+)*)\s*$/, "$1");
}; 


function checkOption(element){
  if (element.parentNode.className) {
    if (element.parentNode.className == 'search_option') {
      element.parentNode.className = 'selected search_option';
    } else {
      element.parentNode.className = 'search_option';
    }
  } else if (element.parentNode.getAttribute) {
    if (element.parentNode.getAttribute('class') == 'search_option') {
      element.parentNode.setAttribute('class','selected search_option');
    } else {
      element.parentNode.setAttribute('class','search_option');
    }
  }
}


function showOptions(clickedElement){
    var showopts=document.getElementById('showopts');
    var title_box=document.getElementById('title_box');
    var author_box=document.getElementById('author_box');
    var collection_box=document.getElementById('collection_box');
    var module_box=document.getElementById('module_box');
    var subject_simple=document.getElementById('simple_subject');
    var subject_advanced=document.getElementById('advanced_subject');
    var collection_advanced=document.getElementById('collection_advanced');
    var module_advanced=document.getElementById('module_advanced');

	if (showopts) {
            showopts.value=1; 
	    }
        clickedElement.removeAttribute("iscollapsed");
        if (title_box.checked || author_box.checked) {
            words_input=document.getElementById('words_input');
            if (title_box.checked) {
                title_input=document.getElementById('title_input');
                title_input.value=words_input.value
            }
            if (author_box.checked) {
                author_input=document.getElementById('author_input');
                author_input.value=words_input.value
            }
            words_input.value=''
            }

        if (module_box.checked && !collection_box.checked) {
            module_advanced.checked='checked';
            }
        if (collection_box.checked && !module_box.checked) {
            collection_advanced.checked='checked';
            }

        module_box.checked='';
        collection_box.checked='';

        subject_advanced.name='subject';
        subject_simple.name='hidden_subject';

        document.getElementById('advanced_search').style.display = 'block';
        document.getElementById('simple_search').style.display = 'none';
}

function hideOptions(clickedElement){
    var showopts=document.getElementById('showopts');
    var title_box=document.getElementById('title_box');
    var author_box=document.getElementById('author_box');
    var collection_box=document.getElementById('collection_box');
    var module_box=document.getElementById('module_box');
    var subject_simple=document.getElementById('simple_subject');
    var subject_advanced=document.getElementById('advanced_subject');

	if (showopts) {
            showopts.value=0; 
	    }
        title_input=document.getElementById('title_input');
        author_input=document.getElementById('author_input');
        words_input=document.getElementById('words_input');
        collection_advanced=document.getElementById('collection_advanced');
        module_advanced=document.getElementById('module_advanced');

        if (module_advanced.checked && !collection_advanced.checked) {
            module_box.checked='checked';
            module_advanced.checked='';
            collection_advanced.checked='';
            }
        if (collection_advanced.checked & !module_advanced.checked) {
            collection_box.checked='checked';
            module_advanced.checked='';
            collection_advanced.checked='';
            }

        if (title_input.value) {
            words_input.value = (words_input.value + ' '+ title_input.value).trim();
            title_input.value = '';
            title_box.checked='checked';
            } else {
            title_box.checked='';
            }
        if (author_input.value) {
            if (words_input.value != author_input.value) {
                words_input.value = (words_input.value + ' ' + author_input.value).trim();
            }
            author_input.value = '';
            author_box.checked='checked';
            } else {
            author_box.checked='';
            }
        subject_advanced.name='hidden_subject';
        subject_simple.name='subject';

        document.getElementById('advanced_search').style.display = 'none';
        document.getElementById('simple_search').style.display = 'block';
}


function syncSelect( first, second ) {
var first = (typeof first == "string") ? document.getElementById( first ) : first;
var second = (typeof second == "string") ? document.getElementById( second ) : second;
second.selectedIndex = first.selectedIndex;
}
