ul = document.getElementsByClassName('pagination')
page = window.location.href.substring(window.location.href.lastIndexOf('/') + 7)
if (page == '')
    window.location.href += '?page=1'

for (i=0; i<ul[0].children.length; i++) {
    if (window.location.href.substring(window.location.href.lastIndexOf('/') + 7) == ul[0].children[i].innerText)
        ul[0].children[i].classList.add('active')
}