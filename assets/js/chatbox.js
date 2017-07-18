/**
 * Created by Shaurya on 17-07-2017.
 */

function set_send_user(data){
        $("#message").val("@"+data+":");
}

$(document).ready(function() {
    rivets.formatters.eq = function(value, checkAgainst)
    {
      return (value == checkAgainst);
    };

    rivets.formatters.neq = function(value, checkAgainst)
    {
      return (value != checkAgainst);
    };

    rivets.binders.src = function(el,value){
        el.src = value;
    };
    rivets.binders.click = function(el,value){
        el.onclick = function(){
            set_send_user(value);
        };
    };

    rivets.bind($('#msgList'), messageJson);

    function scrollSmoothToBottom (id) {
       var div = document.getElementById(id);
       $('#' + id).animate({
          scrollTop: div.scrollHeight - div.clientHeight
       }, 500);
    }

    if (window.WebSocket) {
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
             $('#chat').val($('#chat').val() + 'Connection closed by server: ' + evt.code + ' \"' + evt.reason + '\". Refresh to reconnect.\n');
          };

          $('#send').click(function() {
             ws.send($('#message').val());
             $('#message').val("");
             return false;
          });
          //var textarea = document.getElementById('chat');
          //textarea.scrollTop = textarea.scrollHeight;
        });