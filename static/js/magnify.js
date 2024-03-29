function magnify(imgID, zoom, background_image, x_mult, y_mult, play_x_mult, play_y_mult, color, time) {  
  var img, glass, w, h, bw, fly_x, fly_y, rad, glass_place, found;
    var proportion = .4;
    img = document.getElementById(imgID);
    glass_place = document.getElementById('glass_place');

      /* Create Cursor: */
    rad = (img.width * proportion) / (zoom * 2.5);
    cursor = document.createElement("DIV");
    cursor.setAttribute("class", "cursor");
    cursor.style.width = rad + 2 +  'px';
    cursor.style.height = rad + 2 + 'px';
    img.parentElement.insertBefore(cursor, img);

    /* Create magnifier glass: */
    glass = document.createElement("div");
    glass.setAttribute("class", "img-magnifier-glass");
    
    /* Insert magnifier glass: */
    glass_place.parentElement.insertBefore(glass, glass_place);
    glass.style.width =  (img.width * proportion) + "px"; 
    glass.style.height =  (img.height * proportion) + "px";
    glass.style.margin = 'auto';

    /* Set background properties for the magnifier glass: */
    
    //document.getElementById('cache').innerHTML = is_cached(background_image);   
    glass.style.backgroundImage = "url('" + background_image + "')"; 
    glass.style.backgroundRepeat = "no-repeat";
    glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
    glass.style.display = 'block';
    bw = 3;
    w = glass.offsetWidth / 2;
    h = glass.offsetHeight / 2;

    var xOff = (document.getElementById('art_parent').offsetWidth - img.offsetWidth) / 2;
    var cw = cursor.offsetWidth / 2;

    fly_x =  Math.ceil(x_mult * img.width);
    fly_y = Math.ceil(y_mult * img.height);
    play_x = Math.ceil(play_x_mult * img.width);
    play_y = Math.ceil(play_y_mult * img.width);
    
    if(!give_up){
      glass.style.backgroundPosition = "-" + ((play_x * zoom) - w + bw) + "px -" + ((play_y * zoom) - h + bw) + "px";
      cursor.style.left = play_x + xOff - cw + "px";
      cursor.style.top = play_y - cw + "px";
    }
    else{
      glass.style.backgroundPosition = "-" + ((fly_x * zoom) - w + bw) + "px -" + ((fly_y * zoom) - h + bw) + "px";
      cursor.style.left = fly_x + xOff - cw + "px";
      cursor.style.top = fly_y - cw + "px";
    }

    
    if(!win){
      pathm = [];
      if(start == 'None'){
        d = new Date();
        start = d.toISOString().slice(11,23);
      }
      var d_start = new Date();
      d_start.setUTCHours(start.slice(0,2));
      d_start.setUTCMinutes(start.slice(3,5));
      d_start.setUTCSeconds(start.slice(6,8));
      d_start.setUTCMilliseconds(start.slice(9,11));
      var d_now = new Date();
      var diff = msToTime(d_now - d_start); 
      stopWatch(diff);
      img.addEventListener("mousemove", moveMagnifier);
      img.addEventListener("touchmove", moveMagnifier);
      cursor.addEventListener("mousemove", moveMagnifier);
      cursor.addEventListener("touchmove", moveMagnifier);
      document.getElementById('give_up_button').addEventListener("click", giveUp);
    }
    else{
      setWatch(time);
      setFly(time);
      displayPath(pathm);
    }

    function giveUp(){
      console.log("HERE");
      $('#giveModal').modal('hide');
      give_up=true;
      setWin(fly_x,fly_y);
      glass.style.backgroundPosition = "-" + ((fly_x * zoom) - w + bw) + "px -" + ((fly_y * zoom) - h + bw) + "px";
      cursor.style.left = fly_x + xOff - cw + "px";
      cursor.style.top = fly_y - cw + "px";
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
      found = getDist([Math.floor(x), Math.floor(y)], [fly_x, fly_y]) < rad
      if(found || give_up){
        setTimeout(function(){
          if((found || give_up) && !win){
            setWin(x, y); 
          }
        }, 1000);  
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
      cursor.style.left = x + xOff - cw + "px";
      cursor.style.top = y - cw + "px";
      /* Display what the magnifier glass "sees": */
      glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
    }

    function setWin(x, y){
      var date = new Date();
      var finish = date.toISOString().slice(11,23);
      win = true;
      getPath(x, y, finish, give_up, function(saved_path, time){
        displayPath(saved_path);
        setWatch(time);
        setFly(time);
      });
      $('#resultModal').modal('show');
      img.removeEventListener("touchmove", moveMagnifier);
      img.removeEventListener("mousemove", moveMagnifier);
      cursor.removeEventListener("mousemove", moveMagnifier);
      cursor.removeEventListener("touchmove", moveMagnifier);
    }


    function setFly(time_str){
      var fly = document.getElementById("fly_icon");
      var resultTitle = document.getElementById("resultTitle");    
      var hr_str = '';
      if(time_str.slice(0,2) != '00'){
         hr_str = time_str.slice(0,2) + ':'
      }

      var share_str = "🔎 🪰" + hr_str + time_str.slice(3,5) +':'+ time_str.slice(6,8) +'.'+ time_str.slice(9,11);
      if(!give_up){
        fly.style.color = '#1ed760';
      }
      else{
        fly.style.color = 'gray';
        share_str += '🏳️';
        resultTitle.innerText = "Oh hmm...well at least you tried 🏳️"
      }
      document.getElementById("copy-input").value = share_str;
      fly.addEventListener("click", function(){ $('#resultModal').modal('show'); });

      document.getElementById("fly").style.display = 'initial';
      document.getElementById("flag").style.display = 'none';
    }

    function setTime(time_str){
      var time = getTimeProps(time_str);
      time[3]++;
      if (time[3] == 100) { 
        time[2]++; 
        time[3] = 0; 
      } 
      if (time[2] == 60) { 
          time[1]++; 
          time[2] = 0; 
      } 
      if (time[1] == 60) { 
          time[0]++; 
          time[1] = 0; 
          time[2] = 0; 
      }
      var hrString = time[0]; 
      var minString = time[1]; 
      var secString = time[2]; 
      var countString = time[3]; 
      if (time[0] < 10) { 
          hrString = "0" + hrString; 
      } 
      if (time[1] < 10) { 
          minString = "0" + minString; 
      } 
      if (time[2] < 10) { 
          secString = "0" + secString; 
      } 
      if (time[3] < 10) { 
          countString = "0" + countString; 
      }
      return hrString + ':' + minString + ':' + secString + '.' + countString;
    }
    
    function msToTime(duration) {
      var milliseconds = Math.floor((duration % 1000) / 100),
        seconds = Math.floor((duration / 1000) % 60),
        minutes = Math.floor((duration / (1000 * 60)) % 60),
        hours = Math.floor((duration / (1000 * 60 * 60)) % 24);
    
      hours = (hours < 10) ? "0" + hours : hours;
      minutes = (minutes < 10) ? "0" + minutes : minutes;
      seconds = (seconds < 10) ? "0" + seconds : seconds;
    
      return hours + ":" + minutes + ":" + seconds + "." + milliseconds + '0';
    }

    function getTimeProps(time){
      var t_hr, t_min, t_sec, t_ms;
      t_hr = parseInt(time.slice(0,2));
      t_min = parseInt(time.slice(3,5));
      t_sec = parseInt(time.slice(6,8));
      t_ms = parseInt(time.slice(9,11));

      return [t_hr, t_min, t_sec, t_ms];
    }

    function storeCoordinate(xVal, yVal, array) {
      if(xVal && yVal){
        array.push([xVal,yVal]);
      }
    }
  
    function getCursorPos(e) {
      var a, x = 0, y = 0;
      e = e || window.event;
      /* Account for Android touchEvent issue */
      var pageX, pageY;
      if (e.type == 'mousemove'){
        pageX = e.pageX;
        pageY = e.pageY;
      }
      else{
        pageX = e.touches[0].pageX;
        pageY = e.touches[0].pageY;
      }
      /* Get the x and y positions of the image: */
      a = img.getBoundingClientRect();
      /* Calculate the cursor's x and y coordinates, relative to the image: */
      x = pageX - a.left;
      y = pageY - a.top;
      /* Consider any page scrolling: */
      x = x - window.pageXOffset;
      y = y - window.pageYOffset;
      return {x : x, y : y};
    }

    function getDist(point1, point2){
        return Math.sqrt(Math.pow((point1[0] - point2[0]), 2) + Math.pow((point1[1] - point2[1]), 2));
    }

    function stopWatch(time) { 
        if (!win) {
            time = setTime(time);
            setWatch(time);
            setTimeout(stopWatch, 10, time); 
        }
    }
    function setWatch(time_str){
      document.getElementById('hr').innerHTML = time_str.slice(0,2); 
      document.getElementById('min').innerHTML = time_str.slice(3,5);
      document.getElementById('sec').innerHTML = time_str.slice(6,8); 
      document.getElementById('count').innerHTML = time_str.slice(9,11);

      if(time_str.slice(0,2) != '00'){
        document.getElementById('hr').style.display= 'initial';
        document.getElementById('hr_colon').style.display= 'initial';
      }
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

    async function getPath(x, y, finish, give_up, callback) { 
      $.ajax({
          url: '/spot/get_path',
          data: {
            'x' : x / img.width, 
            'y' : y / img.width,
            'finish' : finish,
            'give_up': give_up 
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

function is_cached(src) {
  var image = new Image();
  image.src = src;

  return image.complete;
}