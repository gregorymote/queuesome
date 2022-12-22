function setActiveProperties(active, type, name){
    var device_continue = document.getElementById("button_submit");
    var device_name = document.getElementById("name");
    var message = document.getElementById('message');
    var icon = document.getElementById('device');
    var c = getIconClass(type);
    icon.className = '';
    icon.classList.add('device', c['glyph'], c['sub']);
    if(active){
        icon.style.color = '#1ed760';
        device_continue.disabled = false;
        message.style.display = 'none';
    }
    else{
        icon.style.color = 'gray';
        device_continue.disabled = true;
        message.style.display = 'block';
    }
    device_name.innerHTML = name;
}

function setDeviceCard(active, type, name){
    var device_name = document.getElementById("name");
    var message = document.getElementById('message');
    var icon = document.getElementById('device');
    var c = getIconClass(type);
    icon.className = '';
    icon.classList.add('device', c['glyph'], c['sub']);
    if(active){
        icon.style.color = '#1ed760';
        message.style.display = 'none';
    }
    else{
        icon.style.color = 'gray';
        message.style.display = 'block';
    }
    device_name.innerHTML = name;
}

function setDeviceIcon(active, type, name){
    
    var icon = document.getElementById('device');
    var c = getIconClass(type);
    icon.className = '';
    icon.classList.add('device', c['glyph'], c['sub']);
    if(active){
        icon.style.color = '#1ed760';
    }
    else{
        icon.style.color = 'red';
    }
}


function getIconClass(type){
    sub = "fas";
    if (type == null || type == 'None'){
        glyph = "fa-exclamation-circle";
    }
    else if(type =="smartphone" ){
        glyph = "fa-mobile-alt";
    }
    else if(type =="tablet" ){
        glyph = "fa-tablet-alt";
    }
    else if(type =="computer" ){
        glyph = "fa-desktop";
    }
    else if(type =="castvideo" ){
        glyph = "fa-chromecast";
        sub="fab";
    }
    else if(type =="tv" ){
        glyph = "fa-tv";
    }
    else{
        glyph = "fa-spotify";
        sub = "fab";
    }
    return {glyph:glyph, sub:sub};
}