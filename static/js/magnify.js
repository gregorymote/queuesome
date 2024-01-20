function magnify(imgID, zoom, background_image, x_mult, y_mult) {
    var img, glass, w, h, bw, fly_x, fly_y, rad;
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
    w = glass.offsetWidth / 2;
    h = glass.offsetHeight / 2;
    
    fly_x =  Math.ceil(x_mult * img.width);
    fly_y = Math.ceil(y_mult * img.height);
    rad = (10 / 75) * (img.width * .25);
    console.log(rad);
    /* Execute a function when someone moves the magnifier glass over the image: */
    glass.addEventListener("mousemove", moveMagnifier);
    img.addEventListener("mousemove", moveMagnifier);
  
    /*and also for touch screens:*/
    glass.addEventListener("touchmove", moveMagnifier);
    img.addEventListener("touchmove", moveMagnifier);
    
    var win = false;
    
    let hour = 0; 
    let minute = 0; 
    let second = 0; 
    let count = 0;
    let hrString = hour; 
    let minString = minute; 
    let secString = second; 
    let countString = count; 

    stopWatch();
    function moveMagnifier(e) {
      glass.style.visibility = "initial";
      var pos, x, y;
      /* Prevent any other actions that may occur when moving over the image */
      e.preventDefault();
      /* Get the cursor's x and y positions: */
      pos = getCursorPos(e);
      x = pos.x;
      y = pos.y;
      if(getDist([Math.floor(x), Math.floor(y)], [fly_x, fly_y]) < rad && !win){
        win = true;
        document.getElementById("copy-input").value = "🔎 🪰" + minString +':'+secString +':'+ countString;
        $('#resultModal').modal('show');
      }
      else{
        console.log("Keep Looking");
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

    function getDist(point1, point2){
        return Math.sqrt(Math.pow((point1[0] - point2[0]), 2) + Math.pow((point1[1] - point2[1]), 2));
    }

    function stopWatch() { 
        if (!win) { 
            count++; 
      
            if (count == 100) { 
                second++; 
                count = 0; 
            } 
      
            if (second == 60) { 
                minute++; 
                second = 0; 
            } 
      
            if (minute == 60) { 
                hour++; 
                minute = 0; 
                second = 0; 
            } 
            hrString = hour; 
            minString = minute; 
            secString = second; 
            countString = count; 

            if (hour < 10) { 
                hrString = "0" + hrString; 
            } 
      
            if (minute < 10) { 
                minString = "0" + minString; 
            } 
      
            if (second < 10) { 
                secString = "0" + secString; 
            } 
      
            if (count < 10) { 
                countString = "0" + countString; 
            } 
      
            document.getElementById('hr').innerHTML = hrString; 
            document.getElementById('min').innerHTML = minString; 
            document.getElementById('sec').innerHTML = secString; 
            document.getElementById('count').innerHTML = countString; 
            setTimeout(stopWatch, 10); 
        }
    }
  }