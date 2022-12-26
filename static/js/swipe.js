function initSwipeButton(button, carousel){
    var button = document.getElementById('button');
    var carousel = document.getElementById('swipe');
    if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
        button.style.display = 'none';
        carousel.style.display = 'block';
    }
    else{
        button.style.display = 'block';
        carousel.style.display = 'none';
    }
    var main_viewport = document.getElementById('main_viewport');
    initPos(main_viewport);
    main_viewport.addEventListener('scroll', scrollVisible);
}


async function scrollSubmit(){
    var slide = document.getElementById('carousel__slide1');
    var swipe = document.getElementById('swipe');
    var main_viewport = document.getElementById('main_viewport');
    var swipe_content = document.getElementById('swipe_content');
    var loader = document.getElementById('loader');
    loader.style.display = '';
    var iWidth = getWidth(loader);
    var sWidth = getWidth(swipe);
    iWidth += getMarginLeft(loader);
    var debug = document.getElementById("debug");
    debug.innerHTML = main_viewport.scrollLeft + " : " + iWidth;
    if(main_viewport.scrollLeft < iWidth){
        main_viewport.classList.remove('scroll-snap-man');
        main_viewport.style.overflow = "hidden";
        swipe.style.width = getHeight(main_viewport) + 'px';
        swipe_content.style.display = 'none';
        main_viewport.scrollLeft = iWidth;
        main_viewport.removeEventListener('scroll', scrollSubmit);
        await delay(setSwipeIconMargin, 'auto', 1000);
        loader.style.visibility = 'visible';
        await delay(setSwipeIconMargin, 'auto', 2000);
        if (await delay(validateInput, '', 0)){
            swipeSubmit();
        }
        else {
            loader.style.visibility = 'hidden';
            main_viewport.classList.add('scroll-snap-man');
            initPos(main_viewport);
            swipe.style.width = sWidth + 'px';
            setSwipeIconMargin('');
            await delay(getWidth, main_viewport, 1000);
            main_viewport.style.overflow = "";
            swipe_content.style.display = 'block';
            main_viewport.addEventListener('scroll', scrollSubmit);
        }
    }
    else{
        loader.style.display = 'none';
    }
}

function scrollAnimate(){
    var slide = document.getElementById('carousel__slide1');
    var width = getWidth(slide);
    var main_viewport = document.getElementById('main_viewport');
    var text = document.getElementById('swipe_content');
    text.style.opacity = (((main_viewport.scrollLeft / width) * 100) / 2) + '%';
}

function scrollVisible(){
    var slide = document.getElementById('carousel__slide1');
    var width = getWidth(slide);
    var main_viewport = document.getElementById('main_viewport');
    var swipe_icon = document.getElementById('swipe_icon');
    var debug = document.getElementById("debug");
    debug.innerHTML = main_viewport.scrollLeft + " : " + width;
    if(width == main_viewport.scrollLeft){
        swipe_icon.style.visibility = 'visible';
        main_viewport.removeEventListener('scroll', scrollVisible);
        main_viewport.addEventListener('scroll', scrollSubmit);
        main_viewport.addEventListener('scroll', scrollAnimate);
    }
}

function initPos(viewport){
    var slide = document.getElementById('carousel__slide1');
    var width = getWidth(slide);
    var debug = document.getElementById("debug");
    debug.innerHTML = "INIT POSITION Width: " + width;
    viewport.scroll(width, 0);
}

function getWidth(element){
    var style = getComputedStyle(element);
    var width = style.getPropertyValue("width");
    width = parseFloat(width);
    return width;
}

function getHeight(element){
    var style = getComputedStyle(element);
    var height = style.getPropertyValue("height");
    height = parseFloat(height);
    return height;
}

function getMarginLeft(element){
    var style = getComputedStyle(element);
    var marginLeft = style.marginLeft;
    return parseFloat(marginLeft);
}

function setSwipeIconMargin(margin){
    document.getElementById('swipe_icon').style.margin = margin;
    document.getElementById('loader').style.margin = margin;
}

function delay(funct, param, ms){
    var x = new Promise((resolve, reject) => {
          setTimeout(function(){resolve(funct(param));}, ms);
        }
    );
    return x;
}