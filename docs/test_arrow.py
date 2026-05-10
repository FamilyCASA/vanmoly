#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

f = 'D:/desktop/VANMOLY-SYS-V3.0/frontend/src/views/Home.vue'
c = open(f, 'r', encoding='utf-8').read()

# Add arrow connector CSS before .holo-sphere
old = '''.holo-sphere {
  display: flex;'''

new = '''/* 箭头连接线 */
.arrow-connector {
  position: absolute;
  right: -30px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 24px;
  color: var(--phase-color, #4A90D9);
  opacity: 0.6;
  animation: arrow-pulse 1.5s infinite;
}

@keyframes arrow-pulse {
  0%, 100% { opacity: 0.4; transform: translateY(-50%) translateX(0); }
  50% { opacity: 1; transform: translateY(-50%) translateX(8px); }
}

.holo-sphere {
  display: flex;
  position: relative;
  flex-shrink: 0;'''

if old in c:
    c = c.replace(old, new)
    open(f, 'w', encoding='utf-8').write(c)
    print('Added arrow connector CSS')
else:
    # Try alternative
    old2 = '''.holo-sphere {
  display: flex;
  flex-direction: column;'''
    if old2 in c:
        new2 = new.replace('.holo-sphere {\n  display: flex;', old2)
        c = c.replace(old2, new2)
        open(f, 'w', encoding='utf-8').write(c)
        print('Added arrow connector CSS (alternative)')
    else:
        print('OLD TEXT NOT FOUND')