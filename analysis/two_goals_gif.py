"""Render the "two goals, one chain" animation as a standalone GIF.

The design mirrors site/assets/two-goals.svg: a four-node chain X -> A -> M -> Y.
Under prediction the credit pools on the mediator M and the deep cause X goes
to near zero; under intervention a do() pulse walks the chain and the credit
returns upstream. The phase label, its underline, the bar colours, and the
highlighted node all switch together so the change of goal is legible.

Usage:  python analysis/two_goals_gif.py [--fps 20] [--seconds 12] [--scale 2]
Writes: docs/images/two-goals.gif and site/assets/two-goals.gif
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = [ROOT / "docs" / "images" / "two-goals.gif", ROOT / "site" / "assets" / "two-goals.gif"]

W, H = 760, 300
INK = (26, 24, 20)
MUTE = (138, 129, 120)
LINE = (185, 176, 161)
CYAN = (0, 119, 168)
CYAN_SOFT = (211, 232, 242)
ORANGE = (224, 112, 32)
ORANGE_SOFT = (251, 227, 208)
PAPER = (255, 255, 255)

NODES = [(110, "X", "deep cause"), (290, "A", "intermediate"), (470, "M", "mediator"), (650, "Y", "outcome")]
NODE_Y, NODE_R = 140, 26
BAR_Y, BAR_H, BAR_W = 204, 60, 48
LABEL_X, LABEL_Y, CAP_Y, RULE_Y = 40, 30, 58, 82
RULE_W = 680


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ["Inter-SemiBold.ttf", "Inter-Medium.ttf", "segoeuib.ttf", "segoeuisb.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["Inter-Regular.ttf", "segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    )
    dirs = [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts", Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
            Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts"), Path("/System/Library/Fonts")]
    for name in candidates:
        for d in dirs:
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def kf(t: float, frames: list[tuple[float, float]]) -> float:
    """Piecewise ease-in-out between (percent, value) keyframes; t in [0, 1)."""
    p = t * 100
    if p <= frames[0][0]:
        return frames[0][1]
    for (p0, v0), (p1, v1) in zip(frames, frames[1:]):
        if p0 <= p <= p1:
            if p1 == p0:
                return v1
            return v0 + (v1 - v0) * smoothstep((p - p0) / (p1 - p0))
    return frames[-1][1]


def mix(c0: tuple, c1: tuple, u: float) -> tuple:
    u = max(0.0, min(1.0, u))
    return tuple(round(a + (b - a) * u) for a, b in zip(c0, c1))


# Phase weights: 1 in prediction, 0 in intervention, eased through the switch.
def phase_p(t):  # visible 4-46 %
    return kf(t, [(0, 0), (1, 0), (6, 1), (45, 1), (50, 0), (100, 0)])


def phase_i(t):  # visible 54-96 %
    return kf(t, [(0, 0), (51, 0), (56, 1), (95, 1), (100, 0)])


def bar_height(t, rest, pred, inter):
    return kf(t, [(0, rest), (2, rest), (12, pred), (46, pred), (50, rest), (62, inter), (94, inter), (100, rest)])


def bar_colour(t):
    # mute -> cyan (prediction) -> mute (switch) -> orange (intervention) -> mute
    wp = kf(t, [(0, 0), (2, 0), (12, 1), (46, 1), (50, 0), (100, 0)])
    wi = kf(t, [(0, 0), (50, 0), (62, 1), (94, 1), (100, 0)])
    c = mix(MUTE, CYAN, wp)
    return mix(c, ORANGE, wi)


def draw_frame(t: float, scale: int) -> Image.Image:
    S = scale
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    f_label = font(19 * S, bold=True)
    f_cap = font(15 * S)
    f_node = font(15 * S, bold=True)
    f_small = font(11 * S)
    f_tiny = font(10 * S)

    def text(x, y, s, fnt, fill, anchor="la", spacing=0.0):
        if spacing:
            # manual letter-spacing
            cx = x
            for ch in s:
                d.text((cx, y), ch, font=fnt, fill=fill, anchor=anchor)
                cx += d.textlength(ch, font=fnt) + spacing
        else:
            d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)

    # --- phase label, caption, rule ---
    for weight, label, cap, colour in (
        (phase_p(t), "PREDICTION", "Once the mediator is in view, the deep cause adds nothing. Its credit goes to zero.", CYAN),
        (phase_i(t), "INTERVENTION", "Set the deep cause and the outcome still moves. Structural attribution can return the credit upstream.", ORANGE),
    ):
        if weight <= 0.001:
            continue
        dy = (1 - weight) * 8 * S  # slides up as it appears
        lab_col = mix(PAPER, colour, weight)
        cap_col = mix(PAPER, INK, weight)
        text(LABEL_X * S, LABEL_Y * S - dy, label, f_label, lab_col, spacing=0.16 * 19 * S)
        text(LABEL_X * S, CAP_Y * S - dy, cap, f_cap, cap_col)
    # rule wipes in with the phase
    wp = kf(t, [(0, 0), (1, 0), (8, 1), (45, 1), (50, 0), (100, 0)])
    wi = kf(t, [(0, 0), (51, 0), (58, 1), (95, 1), (100, 0)])
    for w, colour in ((wp, CYAN), (wi, ORANGE)):
        if w > 0:
            d.rectangle([LABEL_X * S, RULE_Y * S, (LABEL_X + RULE_W * w) * S, (RULE_Y + 2) * S], fill=colour)

    # --- edges ---
    for (x0, _, _), (x1, _, _) in zip(NODES, NODES[1:]):
        y = NODE_Y * S
        d.line([(x0 + NODE_R) * S, y, (x1 - NODE_R) * S, y], fill=LINE, width=max(1, round(1.5 * S)))
        ax = (x1 - NODE_R - 4) * S
        d.polygon([(ax - 10 * S, y - 5 * S), (ax, y), (ax - 10 * S, y + 5 * S)], fill=LINE)

    # --- nodes ---
    n_m = kf(t, [(0, 0), (4, 0), (12, 1), (46, 1), (54, 0), (100, 0)])
    n_x = kf(t, [(0, 0), (56, 0), (66, 1), (94, 1), (100, 0)])
    halo = kf(t, [(0, 0), (54, 0), (58, 1), (94, 1), (100, 0)])
    halo_r = kf(t, [(0, 26), (54, 26), (58, 30), (76, 34), (94, 34), (100, 26)])
    for i, (x, name, sub) in enumerate(NODES):
        cx, cy, r = x * S, NODE_Y * S, NODE_R * S
        if name == "Y":
            fill, outline, txt = INK, INK, PAPER
        elif name == "M":
            fill, outline, txt = mix(PAPER, CYAN_SOFT, n_m), mix(LINE, CYAN, n_m), INK
        elif name == "X":
            fill, outline, txt = mix(PAPER, ORANGE_SOFT, n_x), mix(LINE, ORANGE, n_x), INK
            if halo > 0:
                hr = halo_r * S
                d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], outline=mix(PAPER, ORANGE, halo), width=max(1, round(1.5 * S)))
        else:
            fill, outline, txt = PAPER, LINE, INK
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=max(1, round(1.5 * S)))
        text(cx, cy, name, f_node, txt, anchor="mm")
        text(cx, (NODE_Y + 46) * S, sub, f_small, MUTE, anchor="mm")

    # --- the do() pulse ---
    pulse_pos = kf(t, [(0, 0), (54, 0), (72, 1), (100, 1)])
    pulse_op = kf(t, [(0, 0), (54, 0), (56, 1), (72, 1), (74, 0), (100, 0)])
    if pulse_op > 0:
        px = (110 + (616 - 110) * pulse_pos) * S
        pr = 6 * S
        d.ellipse([px - pr, NODE_Y * S - pr, px + pr, NODE_Y * S + pr], fill=mix(PAPER, ORANGE, pulse_op))

    # --- credit bars ---
    text(40 * S, 272 * S, "CREDIT", f_tiny, MUTE, spacing=0.14 * 10 * S)
    colour = bar_colour(t)
    heights = [bar_height(t, .30, .04, .70), bar_height(t, .40, .22, .74), bar_height(t, .50, .96, .78)]
    for (x, _, _), h in zip(NODES[:3], heights):
        bx0, bx1 = (x - BAR_W / 2) * S, (x + BAR_W / 2) * S
        # dotted track
        by0, by1 = BAR_Y * S, (BAR_Y + BAR_H) * S
        step = 5 * S
        for yy in range(int(by0), int(by1), step):
            d.line([bx0, yy, bx0, min(yy + 2 * S, by1)], fill=LINE, width=S)
            d.line([bx1, yy, bx1, min(yy + 2 * S, by1)], fill=LINE, width=S)
        for xx in range(int(bx0), int(bx1), step):
            d.line([xx, by0, min(xx + 2 * S, bx1), by0], fill=LINE, width=S)
            d.line([xx, by1, min(xx + 2 * S, bx1), by1], fill=LINE, width=S)
        top = by1 - BAR_H * S * h
        d.rounded_rectangle([bx0, top, bx1, by1], radius=3 * S, fill=colour)

    if S > 1:
        img = img.resize((W, H), Image.LANCZOS)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--seconds", type=float, default=12.0)
    ap.add_argument("--scale", type=int, default=2)
    args = ap.parse_args()
    n = int(args.fps * args.seconds)
    frames = [draw_frame(i / n, args.scale) for i in range(n)]
    # quantise every frame with one shared palette, built from frames in both
    # phases and a switch, so the loop neither flickers nor loses a colour
    sample = [frames[int(n * p)] for p in (0.25, 0.48, 0.60, 0.80)]
    strip = Image.new("RGB", (W, H * len(sample)), PAPER)
    for i, f in enumerate(sample):
        strip.paste(f, (0, H * i))
    pal = strip.quantize(colors=128, method=Image.MEDIANCUT)
    quant = [f.quantize(colors=128, palette=pal, dither=Image.NONE) for f in frames]
    for out in OUTPUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        quant[0].save(out, save_all=True, append_images=quant[1:], duration=int(1000 / args.fps), loop=0, optimize=True, disposal=2)
        print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB, {n} frames)")


if __name__ == "__main__":
    main()
