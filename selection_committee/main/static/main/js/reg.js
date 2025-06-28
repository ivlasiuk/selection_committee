window.onload = function(){
    if(document.getElementById('lolka'))
    OpenBootstrapPopup();
};
function OpenBootstrapPopup(){
    $('#mymodal').modal('show');
}

first = document.getElementsByClassName('first-section')
errors = document.getElementsByClassName('error')
newLength = 105 + errors.length * 5
first[0].style.height = newLength.toString() + 'vh'