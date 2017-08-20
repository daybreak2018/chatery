/**
 * Created by Shaurya on 17-07-2017.
 */

$(document).ready(function() {

    function set_send_user(data){
        $("#message").val("@"+data+":");
    }

    function tweet(){
        $('#message').val("tweet:");
    }

    messageJson["tweet"] = tweet;

    rivets.formatters.eq = function(value, checkAgainst)
    {
      return (value == checkAgainst);
    };

    rivets.formatters.neq = function(value, checkAgainst)
    {
      return (value != checkAgainst);
    };

    rivets.formatters.sanitize = function(value)
    {
      return value.split("Twitter's ").join("");
    };

    rivets.formatters.isTwitter = function(value)
    {
      return value.indexOf("Twitter's ")>-1;
    };

    rivets.binders.src = function(el,value){
        el.src = value;
    };

    rivets.binders.value = function(el,value){
        el.value=value;
    }
    rivets.binders.click = function(el,value){
        el.onclick = function(){
            set_send_user(value);
        };
    };

    rivets.bind($('#msgList'), messageJson);
    rivets.bind($('.panel-footer'), messageJson);

    function scrollSmoothToBottom (id) {
       var div = document.getElementById(id);
       $('#' + id).animate({
          scrollTop: div.scrollHeight - div.clientHeight
       }, 500);
    }
	
	$('#next').click(function() {
            window.location.href = window.location.href.split("?")[0] + "?start=" + (start+100)
          });
		  
		  $('#previous').click(function() {
            window.location.href = window.location.href.split("?")[0] + "?start="+(start>0 ? start-100 : 0)
          });

    if (window.WebSocket && websocket) {
            ws = new WebSocket(websocket, ['mytest']);
          }
          else if (window.MozWebSocket) {
            ws = MozWebSocket(websocket);
          }
          else {
            console.log('WebSocket Not Supported');
            return;
          }

          window.onbeforeunload = function(e) {
            $('#chat').val($('#chat').val() + 'Bye bye...\n');
              var message = 'Bye bye...\n'+username+' left the room';
              ws.send(message);
            ws.close(1000, username+' left the room');




            if(!e) e = window.event;
            e.stopPropagation();
            e.preventDefault();
          };
          ws.onmessage = function (evt) {
              messageJson["messages"].push(JSON.parse(evt.data));
              scrollSmoothToBottom("msgListContainer");
          };
          ws.onopen = function() {
             ws.send(username+" entered the room");
          };
          ws.onclose = function(evt) {
             var message = 'Connection closed by server: ' + evt.code + ' \"' + evt.reason + '\". Refresh to reconnect.\n';
              var now = new Date()
              var msgObj = {"message":message,"time":now.getTime(),"username":"System Administrator"}
              messageJson["messages"].push(msgObj);
          };

          $(document).on('click', '.retweet',function(event) {
             ws.send("RT:"+event.target.value.toString());
             return false;
          });

            $('#send').click(function() {
                if($('#message').val()) {
                    ws.send($('#message').val());
                }
             $('#message').val("");
             return false;
          });
        });