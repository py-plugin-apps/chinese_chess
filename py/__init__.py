import re

from typing import Literal, List
from .move import Move
from .board import MoveResult
from .engine import EngineError
from .game import Game, Player, AiPlayer
from core import Handler, Request, RequestIterator, Response, ResponseIterator

package = "chinese_chess"


async def AIHandler(
        request_iterator: RequestIterator,
        game: Game,
        first_selected: Literal["red", "black"],
        human_player: Player,
        ai_player: AiPlayer
) -> ResponseIterator:
    if first_selected == "black":
        move = await ai_player.get_move(game.position())
        move_chi = move.chinese(game)
        result = game.push(move)
        if result:
            yield Response("象棋引擎返回不正确，请检查设置")
            return

        yield Response(
            message=f"{ai_player} 下出 {move_chi},轮到你下棋",
            image=game.draw(),
            messageDict={"at": str(human_player.id)}
        )
    else:
        yield Response(
            message="请下棋",
            image=game.draw(),
            messageDict={"at": str(human_player.id)}
        )

    while True:
        request = await request_iterator.__anext__()
        msg = request.message

        if msg == "悔棋":
            if len(game.moves) >= 2:
                game.pop()
                game.pop()
                yield Response(
                    message="已悔棋，轮到你下棋",
                    image=game.draw(),
                    messageDict={"at": str(human_player.id)}
                )
                continue
            else:
                yield Response(
                    message="已是第一步，无法悔棋",
                    messageDict={"at": str(human_player.id)}
                )
                continue
        try:
            move = Move.from_ucci(msg)
        except ValueError:
            try:
                move = Move.from_chinese(game, msg)
            except ValueError:
                yield Response(
                    message="请发送正确的走法，如 “炮二平五” 或 “h2e2”",
                    messageDict={"at": str(human_player.id)}
                )
                continue
        try:
            move.chinese(game)
        except ValueError:
            yield Response(
                message="不正确的走法",
                messageDict={"at": str(human_player.id)}
            )
            continue

        result = game.push(move)

        if result == MoveResult.ILLEAGAL:
            yield Response(
                message="不正确的走法",
                messageDict={"at": str(human_player.id)}
            )
            continue
        elif result == MoveResult.CHECKED:
            yield Response(
                message="该走法将导致被将军或白脸将",
                messageDict={"at": str(human_player.id)}
            )
            continue

        if result == MoveResult.RED_WIN:
            game.close_engine()
            yield Response(
                message="恭喜你赢了！" if first_selected == "red" else "很遗憾你输了！",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break
        elif result == MoveResult.BLACK_WIN:
            game.close_engine()
            yield Response(
                message="恭喜你赢了！" if first_selected == "black" else "很遗憾你输了！",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break
        elif result == MoveResult.DRAW:
            game.close_engine()
            yield Response(
                message="本局游戏平局",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break

        move = await ai_player.get_move(game.position())
        move_chi = move.chinese(game)
        result = game.push(move)

        if result == MoveResult.ILLEAGAL:
            yield Response("象棋引擎出错，请结束游戏或稍后再试")
            continue

        if result == MoveResult.CHECKED:
            game.close_engine()
            yield Response(
                message="恭喜你赢了！",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break
        elif result == MoveResult.RED_WIN:
            game.close_engine()
            yield Response(
                message="恭喜你赢了！" if first_selected == "red" else "很遗憾你输了！",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break
        elif result == MoveResult.BLACK_WIN:
            game.close_engine()
            yield Response(
                message="恭喜你赢了！" if first_selected == "black" else "很遗憾你输了！",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break
        elif result == MoveResult.DRAW:
            game.close_engine()
            yield Response(
                message="本局游戏平局",
                image=game.draw(),
                messageDict={"at": str(human_player.id)}
            )
            break

        yield Response(
            message=f"{ai_player} 下出 {move_chi},轮到你下棋",
            image=game.draw(),
            messageDict={"at": str(human_player.id)}
        )


async def playerHandler(
        request_iterator: RequestIterator,
        game: Game,
        first_selected: Literal["red", "black"],
        player_list: List[Player],
) -> ResponseIterator:
    current = 0 if first_selected == "red" else 1
    player = player_list[current]

    yield Response(
        message=f"轮到{'红方' if game.moveside else '黑方'} {player}下棋",
        image=game.draw(),
        messageDict={"at": str(player.id)}
    )
    while True:
        request = await request_iterator.__anext__()
        msg = request.message
        if request.event.sender.qq != str(player_list[current].id):
            yield Response(
                message="还未到你的回合",
                messageDict={"at": str(request.event.sender.qq)}
            )
            continue

        try:
            move = Move.from_ucci(msg)
        except ValueError:
            try:
                move = Move.from_chinese(game, msg)
            except ValueError:
                yield Response(
                    message="请发送正确的走法，如 “炮二平五” 或 “h2e2”",
                    messageDict={"at": str(player.id)}
                )
                continue
        try:
            move.chinese(game)
        except ValueError:
            yield Response(
                message="不正确的走法",
                messageDict={"at": str(player.id)}
            )
            continue

        result = game.push(move)

        if result == MoveResult.ILLEAGAL:
            yield Response(
                message="不正确的走法",
                messageDict={"at": str(player.id)}
            )
            continue
        elif result == MoveResult.CHECKED:
            yield Response(
                message="该走法将导致被将军或白脸将",
                messageDict={"at": str(player.id)}
            )
            continue

        if result == MoveResult.RED_WIN:
            yield Response(
                message=f'{player_list[0] if first_selected == "red" else player_list[1]}获胜',
                image=game.draw(),
            )
            break
        elif result == MoveResult.BLACK_WIN:
            yield Response(
                message=f'{player_list[0] if first_selected == "black" else player_list[1]}获胜',
                image=game.draw(),
            )
            break
        elif result == MoveResult.DRAW:
            game.close_engine()
            yield Response(
                message="本局游戏平局",
                image=game.draw(),
            )
            break

        current += 1
        current %= 2
        former_player = player
        player = player_list[current]
        yield Response(
            message=f"{former_player} 下出,轮到{player.name}下棋",
            image=game.draw(),
            messageDict={"at": str(player.id)}
        )


@Handler.StreamToStream
async def handle_chess(request_iterator: RequestIterator) -> ResponseIterator:
    game = Game()
    await request_iterator.__anext__()

    while True:
        yield Response("请选择你所在方(红或黑)")
        request = await request_iterator.__anext__()

        if request.message.startswith("红"):
            game.player_red = first_player = Player(int(request.event.sender.qq), request.event.sender.name)
            first_selected: Literal["red", "black"] = "red"
            break

        if request.message.startswith("黑"):
            game.player_black = first_player = Player(int(request.event.sender.qq), request.event.sender.name)
            first_selected: Literal["red", "black"] = "black"
            break

    ai = False

    if request.event.group.qq:
        while True:
            yield Response("请选择你的对手，你可以@它或者与AI对战。如果与AI对战请输入AI+等级(1-8)，如AI4")

            request = await request_iterator.__anext__()
            if at := request.event.atList:
                if first_selected == "red":
                    game.player_black = second_player = Player(int(at[0].qq), at[0].name)
                else:
                    game.player_red = second_player = Player(int(at[0].qq), at[0].name)
                break

            if re.search('^AI[1-8]$', request.message.upper()):
                if first_selected == "red":
                    game.player_black = second_player = AiPlayer(int(request.message.upper().replace("AI", "")))
                else:
                    game.player_red = second_player = AiPlayer(int(request.message.upper().replace("AI", "")))
                ai = True
                break

    else:
        while True:
            yield Response("请选请输入AI+等级(1-8)，如AI4")

            request = await request_iterator.__anext__()
            if re.search('^AI[1-8]$', request.message.upper()):
                if first_selected == "red":
                    game.player_black = second_player = AiPlayer(int(request.message.upper().replace("AI", "")))
                else:
                    game.player_red = second_player = AiPlayer(int(request.message.upper().replace("AI", "")))
                ai = True
                break

    if ai:
        try:
            await second_player.engine.open()
            msg = f"{first_player}与AI(等级{second_player.level}) 发起了游戏 象棋！\n发送 中文纵线格式如“炮二平五” 或 起始坐标格式如“h2e2” 下棋"
        except Exception as e:
            yield Response(str(e))
            return
    else:
        msg = f"{first_player}与{second_player} 发起了游戏 象棋！\n发送 中文纵线格式如“炮二平五” 或 起始坐标格式如“h2e2” 下棋"

    yield Response(msg)

    if ai:
        handler = AIHandler(
            request_iterator,
            game,
            first_selected,
            first_player,
            second_player
        )
    else:
        handler = playerHandler(
            request_iterator,
            game,
            first_selected,
            [first_player, second_player]
        )

    async for response in handler:
        yield response
