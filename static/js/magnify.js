function magnify(imgID, zoom, background_image, x_mult, y_mult, color) {
    var img, glass, w, h, bw, fly_x, fly_y, rad, glass_place;
    var proportion = .4;
    img = document.getElementById(imgID);
    glass_place = document.getElementById('glass_place');
    /* Create magnifier glass: */
    glass = document.createElement("div");
    glass.setAttribute("class", "img-magnifier-glass");
  
    /* Insert magnifier glass: */
    glass_place.parentElement.insertBefore(glass, glass_place);
    glass.style.width =  (img.width * proportion) + "px"; 
    glass.style.height =  (img.height * proportion) + "px";
    glass.style.margin = 'auto';

    /* Set background properties for the magnifier glass: */
    glass.style.backgroundImage = "url('" + background_image + "')"; 
    glass.style.backgroundRepeat = "no-repeat";
    glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
    glass.style.display = 'block';
    bw = 3;
    w = glass.offsetWidth / 2;
    h = glass.offsetHeight / 2;
    
    fly_x =  Math.ceil(x_mult * img.width);
    fly_y = Math.ceil(y_mult * img.height);
    rad = (img.width * proportion) / (zoom * 2.5);
    
    let hour = 0; 
    let minute = 0; 
    let second = 0; 
    let count = 0;
    let hrString = hour; 
    let minString = minute; 
    let secString = second; 
    let countString = count;

    if(!win){
      path = [];
      stopWatch();
      img.addEventListener("mousemove", moveMagnifier);
      img.addEventListener("touchmove", moveMagnifier);
    }
    else{
      setFly();
      displayPath(path);
    }

    function moveMagnifier(e) {
      var pos, x, y;
      /* Prevent any other actions that may occur when moving over the image */
      e.preventDefault();
      /* Get the cursor's x and y positions: */
      pos = getCursorPos(e);
      x = pos.x;
      y = pos.y;
      storeCoordinate(Math.floor(x), Math.floor(y), path);
      //console.log(fly_x + ', ' + fly_y + ' | ' + Math.floor(x) + ', ' + Math.floor(y) + ' | ' + getDist([Math.floor(x), Math.floor(y)], [fly_x, fly_y]) + ' - ' + rad);
      if(getDist([Math.floor(x), Math.floor(y)], [fly_x, fly_y]) < rad && !win){
        win = true;
        getPath(x, y, function(saved_path){
          displayPath(saved_path);
        });
        setFly();
        $('#resultModal').modal('show');
        img.removeEventListener("touchmove", moveMagnifier);
        img.removeEventListener("mousemove", moveMagnifier);
      }
      /* Prevent the magnifier glass from being positioned outside the image: */
      if (x > img.width - (w / zoom)) {
        x = img.width - (w / zoom);
      }
      if (x < w / zoom) {
        x = w / zoom;
      }
      if (y > img.height - (h / zoom)) {
        y = img.height - (h / zoom);
      }
      if (y < h / zoom) {
        y = h / zoom;
      }
      /* Display what the magnifier glass "sees": */
      glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
    }

    function setFly(){
      var fly = document.getElementById("fly_icon");
      fly.style.color = '#1ed760';
      fly.addEventListener("click", function(){ $('#resultModal').modal('show'); });
      document.getElementById("copy-input").value = "🔎 🪰" + minString +':'+secString +':'+ countString;
    }

    function storeCoordinate(xVal, yVal, array) {
        array.push([xVal,yVal]);
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

    function displayPath(path){
        var offscreenCanvas = document.createElement('canvas');
        var offscreenC = offscreenCanvas.getContext('2d');

        offscreenCanvas.width = img.width;
        offscreenCanvas.height = img.height;
        offscreenC.strokeStyle = 'white';
        offscreenC.beginPath();
        offscreenC.moveTo(path[0][0], path[0][1]);

        for(let i of path){
                offscreenC.lineTo(i[0], i[1]);
                offscreenC.stroke();
        }
        var canvas = document.getElementById("myCanvas");
        canvas.width = img.width;
        canvas.height = img.height;
        var context = canvas.getContext('2d');
        context.fillStyle = color;
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.drawImage(offscreenCanvas, 0, 0);
    }

    async function getPath(x, y, callback) {  
      $.ajax({
          url: '/spot/get_path',
          data: {
            'x' : x / img.width, 
            'y' : y / img.width 
          },
          dataType: 'json',
          success: function (data) {
              saved_path = data.path;
          },
          complete: function(data){
              console.log("complete");
          }
      }).done(function(){callback(saved_path)});
    }
}