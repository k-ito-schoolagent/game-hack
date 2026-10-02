#!/usr/bin/env python3
"""仕様書ステータス（status: spec）のゲームについて、SPEC.md と プレースホルダ index.html を生成する。
使い方: python3 tools/build_specs.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 発想の型に沿った設計書。題材 / 物理化 / 技術 / 失敗の見せ場 / データ / 操作
SPECS = {
    "sakura-front": {
        "title": "桜前線お花見キャッチ",
        "theme": "お花見幹事の「満開の日に場所取りしたい」という全員が知る苦労",
        "physics": "桜前線＝地図上を北上する帯。ブルーシート＝ドラッグで動かす矩形。満開判定＝帯との重なり",
        "skill": "実開花データは年ごとに固定。前線の北上速度を読み、何日先のどの地点に置くかを先読みする技術。張りっぱなしで時間経過、満開当日に帯と重なれば成功",
        "fail": "「葉桜でした」「満開は昨日でした」「場所取りだけ完璧（桜なし）」の3パターンを画面いっぱいに表示",
        "data": "気象庁の桜開花・満開日データ（地点別・年別。観測事実データ）。年選択は typhoon-dodge と同じ型",
        "controls": "ドラッグでブルーシート移動。日付は自動経過（1日=約1秒）。予報帯は3日先まで表示",
    },
    "baiu-defense": {
        "title": "梅雨前線ディフェンス",
        "theme": "梅雨入りを1日でも遅らせたい洗濯民の願い",
        "physics": "プレイヤー＝太平洋高気圧（円）。梅雨前線＝北上してくる帯。円で帯を押し返すと湾曲して北上が遅れる",
        "skill": "実データの前線の動きは固定。押す角度・タイミング・強さの配分。押しすぎると別地域に大雨マスが出るトレードオフを読む",
        "fail": "気象庁テロップ風「◯◯地方 梅雨入り宣言」が画面を覆う",
        "data": "気象庁の梅雨入り・梅雨明け日（地方別・年別）＋前線帯の概略位置",
        "controls": "高気圧をドラッグで移動。長押しで勢力チャージ",
    },
    "dam-ops": {
        "title": "ダム放流オペレーション",
        "theme": "ダム管理者の「放流判断」の重さ（治水は両方向に失敗がある）",
        "physics": "ダム＝貯水ゲージ。雨＝実データの流入カーブ。放流＝スライダーで開くゲート。下流＝水位ライン",
        "skill": "実雨量データは固定。先の降雨を読んで事前放流する先読みバランス技術。満水=氾濫、放ちすぎ=渇水、両方を避ける",
        "fail": "下流氾濫（街のマスが水没）または渇水（取水制限テロップ）",
        "data": "国土交通省 川の防災情報（雨量・ダム流入量）または気象庁の降水実績",
        "controls": "放流量スライダー（親指操作）。貯水率・予報カーブ表示",
    },
    "shuden-rta": {
        "title": "終電乗り換えRTA",
        "theme": "飲み会後の「終電までに帰れるか」の緊張",
        "physics": "路線図＝ノードとエッジ。電車＝実時刻表通りに動く点。プレイヤー＝駅をタップして移動する点",
        "skill": "時刻表は完全固定＝最適ルートの暗記とタップ精度がそのままタイム。RTA的な習熟",
        "fail": "乗り遅れた瞬間に「タクシー代 ¥18,400」のレシートが印刷される演出",
        "data": "駅データ.jp 等のオープンデータ（路線・駅座標）＋簡略化した固定ダイヤ",
        "controls": "駅ノードをタップして乗り換え。走り（連打）でホーム移動時間を短縮",
    },
    "yukiyane": {
        "title": "屋根雪おろし",
        "theme": "雪国の冬の重労働と「落とす向き」の判断",
        "physics": "屋根の雪＝斜面上の物理ブロック群。落とす＝スワイプ方向に崩落。隣家・車・通行人＝当たり判定つき障害物",
        "skill": "実降雪データで積雪量は固定。雪庇の崩れ方（摩擦角・連鎖）を読み、落とす順序と向きを決める技術",
        "fail": "雪の塊が隣家に崩落して「ご近所トラブル発生」、自分に落ちて「生き埋め」",
        "data": "気象庁の積雪深データ（地点別・日別）",
        "controls": "スワイプで雪を落とす方向指定。長押しで雪おろし棒（精密）",
    },
    "hanabi": {
        "title": "花火打上げ職人",
        "theme": "打上げ職人の「間」と風読み",
        "physics": "花火＝放物線＋風で流される点。観客＝歓声メーター。演目＝固定プログラム（尺玉・スターマイン）",
        "skill": "実風データは固定。風速・風向の変化を読んで打上げタイミングと角度を合わせるリズム×読みの技術",
        "fail": "風に流されて観客の歓声がざわめきに変わる。最悪は「打上げ中止」テロップ",
        "data": "気象庁の風速・風向実績（地点別・時別）",
        "controls": "タイミングタップで打上げ。スワイプで角度微調整",
    },
    "ground-handling": {
        "title": "グランドハンドリング",
        "theme": "空港地上係員の同時進行オペレーション",
        "physics": "機体＝慣性のある車両（曲がりにくい・止まりにくい）。誘導路＝グラフ。到着便＝実ダイヤ固定",
        "skill": "実ダイヤは固定＝到着順を暗記し、誘導ルートを先に引く計画技術。同時進行の捌き",
        "fail": "滑走路上のニアミスで「運航停止」、誘導ミスで「スポット渋滞」",
        "data": "空港ダイヤ（公開時刻表）の簡略化版",
        "controls": "機体をタップ→行先スポットをタップで誘導線を引く",
    },
}

PLACEHOLDER_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}（仕様書） | GAME HACK</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22><rect x=%224%22 y=%224%22 width=%2256%22 height=%2256%22 rx=%226%22 fill=%22none%22 stroke=%22%23C8372D%22 stroke-width=%226%22/><text x=%2232%22 y=%2244%22 font-size=%2234%22 font-weight=%22700%22 text-anchor=%22middle%22 fill=%22%23C8372D%22>{mark}</text></svg>">
<style>
  :root{{--paper:#F3EFE4;--ink:#22201C;--ink2:#5E584D;--rule:#CDC3AC}}
  @media (prefers-color-scheme:dark){{:root{{--paper:#1D1B18;--ink:#ECE6D8;--ink2:#B4AC9C;--rule:#3B3730}}}}
  body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Hiragino Sans","BIZ UDGothic","Yu Gothic",sans-serif;line-height:1.85}}
  .wrap{{max-width:680px;margin:0 auto;padding:40px 20px 64px}}
  .no{{font-size:12.5px;letter-spacing:.14em;color:var(--ink2);margin:0 0 8px}}
  h1{{font-size:30px;line-height:1.35;margin:0 0 14px}}
  p{{color:var(--ink2)}}
  dl{{border-top:2px solid var(--ink);margin:28px 0}}
  dl div{{display:grid;grid-template-columns:7em 1fr;gap:12px;border-bottom:1px solid var(--rule);padding:12px 0;font-size:15px}}
  dt{{color:var(--ink2)}} dd{{margin:0}}
  a{{color:inherit;text-underline-offset:3px}}
</style>
</head>
<body>
<div class="wrap">
  <p class="no">{no} ・ 仕様書のみ ・ 制作者募集</p>
  <h1>{title}</h1>
  <p>{summary}</p>
  <dl>
    <div><dt>題材</dt><dd>{theme}</dd></div>
    <div><dt>物理化</dt><dd>{physics}</dd></div>
    <div><dt>権限</dt><dd>{power}</dd></div>
    <div><dt>技術</dt><dd>{skill}</dd></div>
    <div><dt>失敗の見せ場</dt><dd>{fail}</dd></div>
    <div><dt>データ</dt><dd>{data}</dd></div>
    <div><dt>操作</dt><dd>{controls}</dd></div>
  </dl>
  <p>つくってみたい人は <a href="https://github.com/k-ito-schoolagent/game-hack/issues">issue</a> で宣言してください。
  設計書は <a href="https://github.com/k-ito-schoolagent/game-hack/blob/main/games/{id}/SPEC.md">SPEC.md</a>、考え方は <a href="https://github.com/k-ito-schoolagent/game-hack/blob/main/METHOD.md">発想の型</a>。</p>
  <p><a href="../../">一覧へ戻る</a></p>
</div>
</body>
</html>
"""

SPEC_MD = """# {title}（仕様書）

> ステータス: **制作者募集**。issue で宣言してから作業してください。はじめての PR 歓迎。

## 発想の型

| 要素 | 内容 |
|---|---|
| 題材（みんなが知っている現実） | {theme} |
| 物理化（概念→物理オブジェクト） | {physics} |
| ありえない権限（一つだけ） | {power} |
| 技術（習熟でクリア可能にするもの） | {skill} |
| 失敗の見せ場 | {fail} |
| データ（実データ＝固定パターン） | {data} |
| 操作（一つだけ・親指） | {controls} |

考え方は [METHOD.md](../../METHOD.md) を参照。

## 実装の約束（GAME HACK 共通）

- 乱数で勝敗を決めない。出現パターンは実データか固定シーケンス（＝覚えられる・RTAが成立）
- 失敗は必ずプレイヤーの操作・判断に帰因できる（理不尽な死なし）
- スマホ縦持ち・親指操作を基本に（タップ領域 44px 以上・safe-area 対応）
- 単一ファイル `index.html`（このディレクトリに置く）。外部依存なし・ビルド不要
- 共有ボタン（𝕏）とポータルへの導線を入れる
- データの出典をゲーム内に明記する
- 雛形は `_template/` をコピーして始めると早い
"""


def main():
    games = json.load(open(os.path.join(ROOT, "games.json")))
    for g in games:
        if g["status"] != "spec":
            continue
        spec = SPECS[g["id"]]
        d = os.path.join(ROOT, g["dir"])
        os.makedirs(d, exist_ok=True)
        fields = dict(spec)
        fields["id"] = g["id"]
        fields["summary"] = g["summary"]
        fields["no"] = g.get("no", "")
        fields["mark"] = g.get("mark", g["title"][0])
        fields["power"] = g.get("power", "")
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(PLACEHOLDER_HTML.format(**fields))
        with open(os.path.join(d, "SPEC.md"), "w") as f:
            f.write(SPEC_MD.format(**fields))
        print("generated:", g["dir"])


if __name__ == "__main__":
    main()
