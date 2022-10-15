async function scroll(element){
    var delay = 2500;
    var subtract = true;
    var wait = true;
    setTimeout(()=>{wait=false;}, delay);
    var scroll_text = setInterval(function () {
        setWidth(element);
        if(!wait){
            scrollText(element);
        }
    }, 28);

    function scrollText(element) {
        var pWidth = getWidth(element.parentElement);
        var cWidth = getWidth(element);
        if(pWidth < cWidth){
            //var left = getLeft(element);
            var left = getTranslateX(element);
            if(subtract && cWidth + left > pWidth){
                left--;
            }
            else if (!subtract && left < 0){
                left++;
            }
            if(cWidth + left == pWidth){
                subtract = false;
                wait = true;
                setTimeout(()=>{wait=false;}, delay);
            }
            else if(left == 0 && !subtract){
                subtract = true;
                wait = true;
                setTimeout(()=>{wait=false;}, delay);
            }
            //element.style.left = left.toString() + "px";
            element.style.transform = "translateX(" + left.toString() + "px)";
        }
        else{
            //element.style.left = "0px";
            element.style.transform = "translateX(0px)";
            subtract =true;
        }
    }
    function getWidth(e){
        var style = getComputedStyle(e);
        var width = style.getPropertyValue("width");
        width = parseInt(width.split("px")[0]);
        return width;
    }
    function getLeft(e){
        var style = getComputedStyle(element);
        var left = style.getPropertyValue("left");
        left = parseInt(left.split("px")[0]);
        return left;
    }
    function getTranslateX(e){
        var style = window.getComputedStyle(e);
        var matrix = new WebKitCSSMatrix(style.transform);
        return matrix.m41;
     }
    function setWidth(e){
        element.style.width = "auto";
        var pWidth = getWidth(element.parentElement);
        var cWidth = getWidth(element);
        if(cWidth < pWidth){
            element.style.width = "100%";
        }
    }
}
