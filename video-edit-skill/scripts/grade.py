#!/usr/bin/env python3
"""Bake a colour grade into the assembled cut AND the cutout, identically, so behind-head words still blend.

Usage:  PY grade.py <project_dir> [grade.txt]
  grade.txt holds one ffmpeg filter chain (default: SK/assets/template-kaneko/grade.txt, the approved "neutro"
  grade: white wall stays white, slightly cooled phone footage, firmer contrast, light vignette).
Writes assets/aroll_graded.mp4 and assets/subject_graded.webm (VP9 + alpha, alpha passed through untouched) and
checks both still have the same frame count as aroll.mp4. Point the build's <video> tags at the *_graded files.

Why ffmpeg and not CSS filters: CSS filter() grades were too subtle to see; curves/colorbalance per tonal range are not
possible in CSS. Run it after cutout.py (and again after any re-assemble).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skillenv  # noqa: E402

FF, FP = skillenv.tool('ffmpeg'), skillenv.tool('ffprobe')


def frames(f, vp9=False):
    dec = ['-c:v', 'libvpx-vp9'] if vp9 else []
    out = subprocess.run([FP, '-v', 'error', *dec, '-count_frames', '-select_streams', 'v:0', '-show_entries',
                          'stream=nb_read_frames', '-of', 'csv=p=0', f], **skillenv.TEXT).stdout
    return int(out.strip().split(',')[0])


def main():
    skillenv.utf8_stdio()
    proj = skillenv.path_arg(sys.argv[1])
    gfile = skillenv.path_arg(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(skillenv.SKILL_DIR, 'assets', 'template-kaneko', 'grade.txt')
    with open(gfile, encoding='utf-8') as fh:
        g = fh.read().strip()
    a = os.path.join(proj, 'assets')
    aroll, subj = os.path.join(a, 'aroll.mp4'), os.path.join(a, 'subject.webm')
    out_a, out_s = os.path.join(a, 'aroll_graded.mp4'), os.path.join(a, 'subject_graded.webm')
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', aroll, '-vf', g, '-c:v', 'libx264', '-crf', '14', '-preset', 'medium',
                    '-g', '30', '-pix_fmt', 'yuv420p', '-c:a', 'copy', out_a], check=True)
    if os.path.isfile(subj):
        fc = (f'[0:v]format=yuva420p,split[c][a];[c]format=yuv420p,{g}[g];[a]alphaextract[al];'
              '[g][al]alphamerge,format=yuva420p[o]')
        subprocess.run([FF, '-loglevel', 'error', '-y', '-c:v', 'libvpx-vp9', '-i', subj, '-filter_complex', fc, '-map', '[o]',
                        '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-crf', '18', '-b:v', '0', '-auto-alt-ref', '0',
                        '-row-mt', '1', out_s], check=True)
    n = frames(aroll)
    got = [frames(out_a)] + ([frames(out_s, vp9=True)] if os.path.isfile(subj) else [])
    print(f'grade: {os.path.basename(gfile)}  aroll {n} frames -> graded {got}' + ('' if all(x == n for x in got) else '  << MISMATCH'))


if __name__ == '__main__':
    main()
