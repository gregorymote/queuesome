async function pan(element, parent, delay){
    var animation = 5000;
    var speed = 28;
    var wait = true;
    var refresh = false;
    setTimeout(()=>{wait=false;}, delay);
    setInterval(function () {
        if(!wait){
            panText(element, parent);
        }
        else if(refresh){
            refreshElement(parent);
            refresh = false;
        }
        else{
            initializePos(element);
        }
    }, 1);

    function initializePos(element){
        var pWidth = getWidth(element.parentElement);
        var cWidth = getWidth(element);
        if ((pWidth >= cWidth) && getTranslateX(element) != 0) {
            element.style.transitionDuration = '0s';
            element.style.transform = "translateX(0px)";
            refreshElement(parent);
        }
    }

    function panText(element, parent) {
        var pWidth = getWidth(element.parentElement);
        var cWidth = getWidth(element);
        var translateX = getTranslateX(element);
        if(pWidth < cWidth){
            animation = (cWidth - pWidth) * speed
            element.style.transitionDuration = (animation / 1000).toString() + 's';
            if(translateX >= 0){
                width = pWidth - cWidth
                element.style.transform = "translateX(" + width +"px)";
                refreshElement(parent);
                wait = true;
                setTimeout(()=>{wait=false;}, animation + delay);
                setTimeout(()=>{refresh=true;}, animation - 5);
            }
            else{
                element.style.transform = "translateX(0px)";
                refreshElement(parent);
                wait = true;
                setTimeout(()=>{wait=false;}, animation + delay);
                setTimeout(()=>{refresh=true;}, animation - 5);
            }
        }
        else if (getTranslateX(element) != 0){
            console.log(getTranslateX(element));
            element.style.transitionDuration = '0s';
            element.style.transform = "translateX(0px)";
            refreshElement(parent);
        }
    }
}
function setWidth(element){
    element.style.width = "auto";
    var pWidth = getWidth(element.parentElement);
    var cWidth = getWidth(element);
    console.log(pWidth + " : " + cWidth);
    if(cWidth < pWidth){
        element.style.width = "100%";
    }
}
function getWidth(element){
        var style = getComputedStyle(element);
        var width = style.getPropertyValue("width");
        width = parseInt(width.split("px")[0]);
        return width;
}
function getTranslateX(element){
        var style = window.getComputedStyle(element);
        var matrix = new WebKitCSSMatrix(style.transform);
        return matrix.m41;
}
function refreshElement(element){
    element.style.border = 'dotted 0px transparent';
    setTimeout(function(){
        element.style.border = 'solid 0px transparent';
    },1);
}

function forceRedraw(element){
    if (!element) { return; }

    var n = document.createTextNode(' ');
    var disp = element.style.display;  // don't worry about previous display style

    element.appendChild(n);
    element.style.display = 'none';

    setTimeout(function(){
        element.style.display = disp;
        n.parentNode.removeChild(n);
    },1);
}