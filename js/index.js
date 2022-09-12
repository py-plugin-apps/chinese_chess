import { StreamToStream, createEvent } from "../../../core/client/client.js";
import { segment } from "oicq";

export const rule = {
  chinese_chess_start: {
    reg: "^#下象棋",
    priority: 700,
    describe: "开始下象棋",
  },
  chinese_chess_listener: {
    reg: "noCheck",
    priority: 800,
    describe: "开始下象棋",
  },
  chinese_chess_cancel: {
    reg: "^#取消下象棋",
    priority: 701,
    describe: "取消下象棋",
  },
};

let group_call = {};
let private_call = {};

async function createGame(e) {
  let call = StreamToStream({
    _package: "chinese_chess",
    _handler: "handle_chess",
    onData: (errors, response) => {
      if (errors) {
        console.log(errors.stack);
      } else {
        let msg = [];

        if (response.message) {
          msg.push(response.message);
        }
        if (response.image.length) {
          msg.push(segment.image(response.image));
        }

        if (response.messageDict.at) {
          msg.push(segment.at(response.messageDict.at));
        }

        e.reply(msg);
      }
    },
    onEnd: () => {
      if (e.isGroup) {
        clearTimeout(group_call[e.group_id].timer);
        delete group_call[e.group_id];
      } else {
        clearTimeout(private_call[e.sender.user_id].timer);
        delete private_call[e.sender.user_id];
      }
    },
  });

  call.send({
    event: await createEvent(e),
    message: e.msg.replace("#象棋", ""),
  });

  return {
    participant: {
      owner: e.sender.user_id,
      rival: null,
    },
    timer: null,
    call: call,
  };
}

async function timer(e, is_group, id) {
  let current;
  if (is_group) {
    current = group_call[id];
  } else {
    current = private_call[id];
  }

  if (current.timer) {
    clearTimeout(current.timer);
  }

  return setTimeout(() => {
    e.reply("象棋已自动结束");
    current["call"].end();

  }, 5 * 60 * 1000);
}

function valid(e) {
  if (e.isGroup) {
    let qq = e.sender.user_id;
    let current = group_call[e.group_id].participant;
    return current.owner === qq || current.rival === qq;
  } else {
    return true;
  }
}

export async function chinese_chess_start(e) {
  if (e.isGroup) {
    if (group_call[e.group_id]) {
      e.reply("象棋进行中！");
    } else {
      group_call[e.group_id] = await createGame(e);
      group_call[e.group_id].timer = await timer(e, true, e.group_id);
    }
  } else {
    if (private_call[e.sender.user_id]) {
      e.reply("象棋进行中！");
    } else {
      private_call[e.sender.user_id] = await createGame(e);
      private_call[e.sender.user_id].timer = await timer(e, false, e.sender.user_id);
    }
  }
  return true;
}

export async function chinese_chess_listener(e) {
  if (e.isGroup && group_call[e.group_id]) {
    let current = group_call[e.group_id];

    let msg = e.msg?.replace("#", "");
    if (valid(e)) {
      let event = await createEvent(e);
      if (msg?.match(/^[红黑]$/g)) {
        current["call"].send({
          event: event,
          message: msg,
        });
        current.timer = await timer(e, true, e.group_id);
        return true;
      } else if (msg?.match(/^([a-i][0-9]){2}$|^[帥將将帅仕士相象傌馬马俥車车炮砲兵卒].[平进上退下].$/g)) {
        current["call"].send({
          event: event,
          message: msg,
        });
        current.timer = await timer(e, true, e.group_id);
        return true;
      } else if (msg?.match(/^[Aa][Ii][1-8]$/g)) {
        current.participant.rival = "ai";
        current["call"].send({
          event: await createEvent(e),
          message: msg,
        });
      } else if (!current.participant.rival && event.atList.length) {
        current["call"].send({
          event: event,
        });
        current.participant.rival = Number(event.atList[0].qq);
      } else if (msg === "悔棋") {
        if(current.participant.rival==="ai"){
          current["call"].send({
          event: await createEvent(e),
          message: msg,
        });
        }else {
          e.reply("人人对战不允许悔棋");
        }
      }
    }
  } else if (!e.isGroup && private_call[e.sender.user_id]) {
    let current = private_call[e.sender.user_id];
    let msg = e.msg.replace("#", "");
    if (msg.match(/^[红黑]|^[Aa][Ii][1-8]$|^悔棋$/g)) {
      current["call"].send({
        event: await createEvent(e),
        message: msg,
      });
      current.timer = await timer(e, false, e.sender.user_id);
      return true;
    } else if (msg.match(/^([a-i][0-9]){2}$|^[帥將将帅仕士相象傌馬马俥車车炮砲兵卒].[平进上退下].$/g)) {
      current["call"].send({
        event: await createEvent(e),
        message: msg,
      });
      current.timer = await timer(e, false, e.sender.user_id);
      return true;
    }
  }
}

export async function chinese_chess_cancel(e) {
  if (e.isGroup) {
    if (group_call[e.group_id]) {
      if (e.sender.user_id === group_call[e.group_id].participant.owner || e.isMaster) {
        group_call[e.group_id]["call"].end();
        e.reply("已取消");
      } else {
        e.reply("只有发起人能取消");
      }
    } else {
      e.reply("象棋未开始");
    }
  } else {
    if (private_call[e.sender.user_id]) {
      private_call[e.sender.user_id]["call"].end();
      e.reply("已取消");
    } else {
      e.reply("象棋未开始");
    }
  }
  return true;
}
