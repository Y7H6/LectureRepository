# Simple advisor skeleton for prototype.
# - Performs a lightweight deterministic heuristic to pick action.
# - For production: replace with EV engine + Monte Carlo + opponent model.
from typing import Dict, Any, List

def _rank_card(card: str) -> int:
    rank_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    return rank_map.get(card[0].upper(), 0)

def _is_pair(hand: List[str]) -> bool:
    return hand[0][0].upper() == hand[1][0].upper()

def _both_high_cards(hand: List[str]) -> bool:
    return _rank_card(hand[0]) >= 10 and _rank_card(hand[1]) >= 10

def advise_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    payload keys: hand, board, position, stack, pot, opponent_style, action_history, mode
    Returns:
      { action: "call"|"fold"|"raise", bet_size: "...", reasoning: [ ... ] }
    """
    hand = payload.get("hand", [])
    board = payload.get("board", [])
    position = payload.get("position", "BTN")
    stack = payload.get("stack", 100)
    pot = payload.get("pot", 1)
    opponent_style = payload.get("opponent_style", "TAG")
    mode = payload.get("mode", "beginner")

    reasoning = []
    # Basic analysis
    if _is_pair(hand):
        reasoning.append("ポケットペアを持っています（ペアはプリフロップ・ポストフロップで強い）。")
        action = "raise" if mode == "beginner" else "raise"
        bet_size = "3x"
        reasoning.append("初心者向け: ペアは価値があるため積極的にベット/レイズします。")
    elif _both_high_cards(hand):
        reasoning.append("両方高位カード（10以上）を持っています。ポストフロップでもトップペアやストレートの可能性がある。")
        action = "call"
        bet_size = "—"
        reasoning.append("相手のレンジとポジションによってはコールが妥当です。")
    else:
        reasoning.append("ハンドはミドル／弱めのレンジです。")
        action = "fold"
        bet_size = "—"
        reasoning.append("初心者向け: 安全策としてフォールドを推奨します。")

    # Note: real implementation should compute equities and pot odds here.

    return {
        "action": action,
        "bet_size": bet_size,
        "reasoning": reasoning
    }
