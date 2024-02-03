function magnify(imgID, zoom, background_image, x_mult, y_mult, play_x_mult, play_y_mult, color) {
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
    play_x = Math.ceil(play_x_mult * img.width);
    play_y = Math.ceil(play_y_mult * img.width);
    rad = (img.width * proportion) / (zoom * 2.5);
    glass.style.backgroundPosition = "-" + ((play_x * zoom) - w + bw) + "px -" + ((play_y * zoom) - h + bw) + "px";
    
    let hour = 0; 
    let minute = 0; 
    let second = 0; 
    let count = 0;
    let hrString = '0' + hour; 
    let minString = '0' + minute; 
    let secString = '0' + second; 
    let countString = '0' + count;

    if(!win){
      pathm = [];
      d = new Date();
      if(start == 'None'){
        console.log("Not Start");
        start = d.toISOString().slice(11,23);
      }
      else{
        var d_start = new Date(start);
        var d_now = new Date();
        var diff = d_now - d_start; 
        //var now = diff.toISOString().slice(11,23);
        console.log(d_now + ' ' + d_start);
      }
      stopWatch();
      img.addEventListener("mousemove", moveMagnifier);
      img.addEventListener("touchmove", moveMagnifier);
    }
    else{
      setTime(time);
      setWatch(hrString,minString,secString,countString);
      setFly();
      displayPath(pathm);
    }

    function moveMagnifier(e) {
      var pos, x, y;
      /* Prevent any other actions that may occur when moving over the image */
      e.preventDefault();
      /* Get the cursor's x and y positions: */
      pos = getCursorPos(e);
      x = pos.x;
      y = pos.y;
      storeCoordinate(x / img.width, y / img.width, pathm);
      if(getDist([Math.floor(x), Math.floor(y)], [fly_x, fly_y]) < rad && !win){
        var date = new Date();
        var finish = date.toISOString().slice(11,23);
        win = true;
        getPath(x, y, finish, function(saved_path, time){
          displayPath(saved_path);
          setTime(time);
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
      document.getElementById("copy-input").value = "🔎 🪰" + minString +':'+secString +':'+ countString;
      fly.addEventListener("click", function(){ $('#resultModal').modal('show'); });
    }

    function setTime(time){
      //console.log(time)
      min = parseInt(time.slice(3,5));
      second = parseInt(time.slice(6,8));
      count = parseInt(time.slice(9,11));
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
            setTime(hrString+':'+minString+':'+secString+':'+countString);
            setWatch(hrString,minString,secString,countString);
            setTimeout(stopWatch, 10); 
        }
    }
    function setWatch(hrString,minString,secString,countString){
      document.getElementById('hr').innerHTML = hrString; 
      document.getElementById('min').innerHTML = minString; 
      document.getElementById('sec').innerHTML = secString; 
      document.getElementById('count').innerHTML = countString; 
    }

    function displayPath(coords){
        var offscreenCanvas = document.createElement('canvas');
        var offscreenC = offscreenCanvas.getContext('2d');

        offscreenCanvas.width = img.width;
        offscreenCanvas.height = img.height;
        offscreenC.strokeStyle = 'white';
        offscreenC.beginPath();
        offscreenC.moveTo(coords[0][0] * img.width, coords[0][1] * img.width);

        for(let i of coords){
                offscreenC.lineTo(i[0] * img.width, i[1] * img.width);
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

    async function getPath(x, y, finish, callback) { 
      console.log("Finish: " + finish);
      $.ajax({
          url: '/spot/get_path',
          data: {
            'x' : x / img.width, 
            'y' : y / img.width,
            'finish' : finish 
          },
          dataType: 'json',
          success: function (data) {
              saved_path = data.pathm;
              time = data.time;
              if(time.length == 14){
                time = '0' + time;
              }
          }
      }).done(function(){callback(saved_path, time)});
    }
}