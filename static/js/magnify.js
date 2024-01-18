function magnify(imgID, zoom, background_image, x_mult, y_mult) {
    var img, glass, w, h, bw, fly_x, fly_y;
    img = document.getElementById(imgID);
  
    /* Create magnifier glass: */
    glass = document.createElement("DIV");
    glass.setAttribute("class", "img-magnifier-glass");
  
    /* Insert magnifier glass: */
    img.parentElement.insertBefore(glass, img);
    glass.style.width =  (img.width * .25) + "px"; 
    glass.style.height =  (img.height * .25) + "px";

    /* Set background properties for the magnifier glass: */
    glass.style.backgroundImage = "url('" + background_image + "')"; 
    glass.style.backgroundRepeat = "no-repeat";
    glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
    glass.style.visibility = "hidden";

    bw = 3;
    console.log(glass.offsetWidth);
    w = glass.offsetWidth / 2;
    h = glass.offsetHeight / 2;
    
    fly_x =  Math.ceil(x_mult * img.width);
    fly_y = Math.ceil(y_mult * img.height);

    /* Execute a function when someone moves the magnifier glass over the image: */
    glass.addEventListener("mousemove", moveMagnifier);
    img.addEventListener("mousemove", moveMagnifier);
  
    /*and also for touch screens:*/
    glass.addEventListener("touchmove", moveMagnifier);
    img.addEventListener("touchmove", moveMagnifier);
    
    function moveMagnifier(e) {
      glass.style.visibility = "initial";
      var pos, x, y;
      /* Prevent any other actions that may occur when moving over the image */
      e.preventDefault();
      /* Get the cursor's x and y positions: */
      pos = getCursorPos(e);
      x = pos.x;
      y = pos.y;
      //console.log(Math.ceil(x) + " , " + Math.ceil(y) + ' : ' + fly_x + ', ' + fly_y);
      if(Math.ceil(x) == fly_x && Math.ceil(y) == fly_y){
        console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
      }
      /* Prevent the magnifier glass from being positioned outside the image: */
      if (x > img.width - (w / zoom)) {
        x = img.width - (w / zoom);
        glass.style.visibility = "hidden";
    }
      if (x < w / zoom) {
        x = w / zoom;
        glass.style.visibility = "hidden";
    }
      if (y > img.height - (h / zoom)) {
        y = img.height - (h / zoom);
        glass.style.visibility = "hidden";
    }
      if (y < h / zoom) {
        y = h / zoom;
        glass.style.visibility = "hidden";
    }
      /* Set the position of the magnifier glass: */
      glass.style.left = (x) + "px";
      glass.style.top = (y - h) + "px";
      /* Display what the magnifier glass "sees": */
      glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
      
    }
  
    function getCursorPos(e) {
      var a, x = 0, y = 0;
      e = e || window.event;
      /* Get the x and y positions of the image: */
      a = img.getBoundingClientRect();
      /* Calculate the cursor's x and y coordinates, relative to the image: */
      x = e.pageX - a.left;
      y = e.pageY - a.top;
      /* Consider any page scrolling: */
      x = x - window.pageXOffset;
      y = y - window.pageYOffset;
      return {x : x, y : y};
    }
  }