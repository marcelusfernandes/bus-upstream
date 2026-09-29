#!/usr/bin/env python3
import argparse, subprocess
LABELS = [
("problem:explore","BFDADC","Problem — Vague + Unknown"),
("problem:frame","7BC8F6","Problem — Vague + Known"),
("problem:investigate","4F86F7","Problem — Concrete + Unknown"),
("problem:ready","2DA44E","Problem — Concrete + Known"),
("solution:explore","E6CCFF","Solution — Vague + Unknown"),
("solution:shape","C9A7FF","Solution — Vague + Known"),
("solution:validate","8C7AE6","Solution — Concrete + Unknown"),
("solution:deliver","1F883D","Solution — Concrete + Known"),
("type:investigation","D4C5F9","Upstream investigation"),
("type:framing","C5DEF5","Problem framing"),
("type:design","BFD4F2","Solution design"),
("type:experiment","F9D0C4","Validation / experiment"),
("type:decision","FBCA04","Explicit decision / gate"),
("human","D93F0B","Requires explicit human decision/action"),
]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--apply',action='store_true'); args=ap.parse_args()
    for name,color,desc in LABELS:
        cmd=['gh','label','create',name,'--color',color,'--description',desc,'--force']
        print('$ '+' '.join(cmd))
        if args.apply: subprocess.run(cmd,check=True)
if __name__=='__main__': main()
