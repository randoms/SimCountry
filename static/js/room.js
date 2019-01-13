(function() {
    var startFlag = false;
    // 判断是否是加入已有房间
    var url = new URL(document.location);
    var joinFlag = url.searchParams.get("join");
    var roomID = url.searchParams.get("room_id");
    var adminFlag = joinFlag == null || !joinFlag;
    var socketConnectionFlag = false;
    var gameState = "ENTER_NAME";
    var myCountry = null;
    // var gameState = "PLAY";
    var socket = null;
    var clientID = getUUID();

    var texReqID = null;
    var jobsReqID = null;
    var turn = "";

    function initSocket() {
        socket = new WebSocket("ws://bwbot.org:8000/");
        socket.onopen = function(evt) {
            socketConnectionFlag = true;
            if (adminFlag) {
                createRoom();
            } else {
                joinRoom(roomID);
            }
            render();
        };
        socket.onclose = function(evt) {
            socketConnectionFlag = false;
            render();
        };
        socket.onerror = function(evt) {
            socketConnectionFlag = false;
            render();
        };
        socket.onmessage = function(evt) {
            // console.log(JSON.parse(evt.data));
            socketConnectionFlag = true;
            processRecMessage(evt.data);
            render();
        };
    }

    function render() {
        if (gameState == "ENTER_NAME") {
            $(".game-scene").addClass("hide");
            $(".start-page").removeClass("hide");
            if (adminFlag) {
                $(".start-page .info").removeClass("hide");
                $(".start-page .room-name").removeClass("hide");
                $(".start-page .room-controller").addClass("hide");
                $(".start-page .player-list").addClass("hide");
                $(".start-page .btn-prepare").addClass("hide");
                $(".start-page .btn-start").addClass("hide");
            } else {
                $(".start-page .info").removeClass("hide");
                $(".start-page .room-name").removeClass("hide");
                $(".start-page .room-controller").addClass("hide");
                $(".start-page .player-list").addClass("hide");
                $(".start-page .btn-prepare").addClass("hide");
                $(".start-page .btn-start").addClass("hide");
            }
            if (socketConnectionFlag) {
                $(".start-page .info .status-icon").removeClass("error");
                $(".start-page .info .status-icon").addClass("ok");
            } else {
                $(".start-page .info .status-icon").removeClass("ok");
                $(".start-page .info .status-icon").addClass("error");
            }
            console.log(roomID);
            if (roomID != null) {
                $(".start-page .room-id").text(roomID);
            }
        }
        if (gameState == "WAIT_FOR_READY") {
            $(".game-scene").addClass("hide");
            $(".start-page").removeClass("hide");
            if (adminFlag) {
                $(".start-page .info").removeClass("hide");
                $(".start-page .room-name").addClass("hide");
                $(".start-page .room-controller").removeClass("hide");
                $(".start-page .player-list").removeClass("hide");
                $(".start-page .btn-prepare").addClass("hide");
                $(".start-page .btn-start").removeClass("hide");
            } else {
                $(".start-page .info").removeClass("hide");
                $(".start-page .room-name").addClass("hide");
                $(".start-page .room-controller").addClass("hide");
                $(".start-page .player-list").removeClass("hide");
                $(".start-page .btn-prepare").removeClass("hide");
                $(".start-page .btn-start").addClass("hide");
            }
        }
        if (gameState == "PLAY") {
            $(".start-page").addClass("hide");
            $(".game-scene").removeClass("hide");
            if (socketConnectionFlag) {
                $(".game-scene .info .status-icon").removeClass("error");
                $(".game-scene .info .status-icon").addClass("ok");
            } else {
                $(".game-scene .info .status-icon").removeClass("ok");
                $(".game-scene .info .status-icon").addClass("error");
            }
        }
    }

    function getUUID() {
        return new Date().valueOf() + "" + parseInt(Math.random() * 1000);
    }

    var reqRecords = {};
    function sendRequest(msg, cb) {
        if (!socketConnectionFlag) {
            alert("网络连接失败");
            return;
        }
        var uuid = getUUID();
        reqRecords[uuid] = cb;
        socket.send(
            JSON.stringify({
                req_id: uuid,
                type: "request",
                message: msg
            })
        );
    }

    var channelRecords = {};
    function subscribe(channel, cb) {
        if (!socketConnectionFlag) {
            alert("网络连接失败");
            return;
        }
        var subsID = getUUID();
        channelRecords[subsID] = {
            channel: channel,
            cb: cb
        };
    }

    function unsubscribe(subsID) {
        channelRecords[subsID] = null;
    }

    function processRecMessage(message) {
        // 检查是不是一个request
        var msg = JSON.parse(message);
        if (msg["type"] == "response") {
            reqRecords[msg["req_id"]](msg["message"]);
            reqRecords[msg["req_id"]] = null;
            return;
        }
        if (msg["type"] == "broadcast") {
            for (sub in channelRecords) {
                if (channelRecords[sub] == null) continue;
                if (channelRecords[sub]["channel"] == msg["channel"]) {
                    channelRecords[sub]["cb"](msg["message"]);
                }
            }
        }
        if (msg["type"] == "request") {
            if (msg["message"]["url"] == "set_tex") {
                texReqID = msg["req_id"];
            }
            if (msg["message"]["url"] == "set_jobs") {
                jobsReqID = msg["req_id"];
            }
        }
    }

    $(".btn-create-country").on("click", function(evt) {
        evt.preventDefault();
        // 开始创建国家
        sendRequest(
            {
                url: "create_country",
                room_id: roomID,
                client_id: clientID,
                country_name: $(".start-page .country-name").val()
            },
            function(res) {
                myCountry = res["country"];
                // 进入准备阶段
                gameState = "WAIT_FOR_READY";
                // 设置订阅频道
                var playersTmpl = $("#playersTmpl").html();
                subscribe("players", function(data) {
                    var content = juicer(playersTmpl, {
                        players: data.players,
                        myCountry: res["country"]
                    });
                    $(".player-list ul").html(content);
                });
                if (!adminFlag) {
                    subscribe("game", function(data) {
                        if (data["info"] == "start" && gameState != "PLAY") {
                            startGame();
                        }
                    });
                }
                render();
            }
        );
    });

    $(".start-page .add-robot").on("click", function(evt) {
        evt.preventDefault();
        sendRequest(
            {
                url: "add_robot",
                room_id: roomID,
                client_id: clientID
            },
            function(res) {
                render();
            }
        );
    });

    $(".start-page .btn-prepare").on("click", function(evt) {
        evt.preventDefault();
    });

    $(".start-page .btn-start").on("click", function(evt) {
        evt.preventDefault();
        sendRequest(
            {
                url: "start_game",
                room_id: roomID,
                client_id: clientID
            },
            function(res) {
                startGame();
            }
        );
    });

    $(".game-scene .submit-plan").on("click", function(evt) {
        evt.preventDefault();
        console.log("submit clicked");
        if (myCountry.id !== turn) {
            $(".game-scene .world-info").html(
                `<span class="status-error">还没轮到你</span>` +
                    $(".game-scene .world-info").html()
            );
            return;
        }
        if (texReqID != null) {
            socket.send(
                JSON.stringify({
                    type: "response",
                    req_id: texReqID,
                    message: {
                        tex: $(".game-scene .plan-editor .tex").val()
                    }
                })
            );
            texReqID = null;
        }
        setTimeout(function() {
            if (jobsReqID != null) {
                socket.send(
                    JSON.stringify({
                        type: "response",
                        req_id: jobsReqID,
                        message: {
                            jobs: $(".game-scene .plan-editor .jobs").val()
                        }
                    })
                );
                jobsReqID = null;
            }
        }, 500);
    });

    // 创建房间
    function createRoom() {
        sendRequest(
            {
                url: "create_room",
                client_id: clientID
            },
            function(res) {
                roomID = res["room"]["id"];
                render();
            }
        );
    }

    function joinRoom(room_id) {
        sendRequest(
            {
                url: "join_room",
                client_id: clientID,
                room_id: room_id
            },
            function(res) {
                roomID = res["room"]["id"];
                render();
            }
        );
    }

    function startGame() {
        gameState = "PLAY";
        // 设置订阅频道
        var playersTmpl = $("#playersTmpl").html();
        subscribe("players", function(data) {
            var content = juicer(playersTmpl, {
                players: data.players,
                myCountry: myCountry
            });
            $(".game-scene .country-list ul").html(content);
            $(`.game-scene li[data-name=${turn}]`).addClass("on-turn");
        });
        subscribe("system", function(data) {
            if (typeof data["info"] != "undefined") {
                $(".game-scene .world-info").html(
                    `<span class="status-info">${data["info"]}</span>` +
                        $(".game-scene .world-info").html()
                );
            }
            if (typeof data["warn"] != "undefined") {
                $(".game-scene .world-info").html(
                    `<span class="status-warn">${data["warn"]}</span>` +
                        $(".game-scene .world-info").html()
                );
            }
            if (typeof data["error"] != "undefined") {
                $(".game-scene .world-info").html(
                    `<span class="status-error">${data["error"]}</span>` +
                        $(".game-scene .world-info").html()
                );
            }
        });
        subscribe("turn", function(data) {
            turn = data["country"];
        });
        render();
    }

    initSocket();
    render();
    if (joinFlag == null || !joinFlag) {
        // 创建房间
    } else {
        // 加入以有房间
    }
})();
