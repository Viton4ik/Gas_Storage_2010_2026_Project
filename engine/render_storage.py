"""Storage-specific hooks around the unchanged CO2 renderer.

Adds a lowest-positive monthly slot, adaptive time mapping and overall ranks.
All bar drawing, geometry, spring animation, flags and fonts are delegated to
the supplied render.py. The old 'min' layout slot is used only as a drawing
location for the genuine smallest positive eligible month-end report.
"""
from pathlib import Path
import runpy
import csv

module = runpy.run_path(str(Path(__file__).with_name('render.py')),
                       run_name='reference_renderer')
env = module['main'].__globals__
cfg = env['CFG']
with (env['ROOT']/cfg['comparison']['source_csv']).open() as handle:
    report_codes = {(r['month'],r['country']):r['assessment_code']
                    for r in csv.DictReader(handle)}
original_precompute = env['precompute']
original_frame = env['render_frame']
original_row = env['draw_row']
original_label = env['draw_block_label']
original_event = env['draw_event']
original_slot = env['draw_slot']

# Positive time increments, monotone PCHIP mapping, and explicit short plateaus
# keep every source month and spend more screen time on the dense years.
pacing = cfg.get('pacing', {})
year_weights = pacing.get('year_weights', {})
holds = set(pacing.get('holds_at_month_indices', []))
hold_seconds = pacing.get('hold_seconds', 0)
nm = env['NM']
weights = [float(year_weights.get(env['periods'][i][:4], 1))
           for i in range(nm-1)]
assert all(w > 0 for w in weights)
usable_time = env['T_RACE'] - hold_seconds * len(holds)
assert usable_time > 0
times, indices = [0.0], [0.0]
elapsed = 0.0
for i, weight in enumerate(weights):
    elapsed += usable_time * weight / sum(weights)
    times.append(elapsed)
    indices.append(float(i+1))
    if i+1 in holds:
        elapsed += hold_seconds
        times.append(elapsed)
        indices.append(float(i+1))
assert abs(elapsed-env['T_RACE']) < 1e-6
time_curve = env['PchipInterpolator'](times, indices)


def month_at(t):
    relative = min(max(t-env['T_INTRO'], 0.0), env['T_RACE'])
    return float(time_curve(relative))


def precompute():
    layout_slots = env['DYN']
    env['DYN'] = ['max']
    try:
        states = original_precompute()
    finally:
        env['DYN'] = layout_slots
    previous, previous_card, since = None, None, -1000000
    previous_value, previous_caution = None, False
    last_value, last_caution = None, False
    for frame, state in enumerate(states):
        index = min(round(state['m']),nm-1)
        candidates = {code:float(env['VALS'][env['SORT_COL']][code][index])
                      for code in env['codes'] if state['act'][code]
                      and env['VALS'][env['SORT_COL']][code][index] > 0}
        assert candidates
        minimum = min(candidates.values())
        tied = sorted(code for code,value in candidates.items() if value==minimum)
        current = previous if previous in tied else tied[0]
        caution = report_codes[env['periods'][index],current.split('_')[0]] == '2'
        if current != previous:
            previous_card, previous, since = previous, current, frame
            previous_value, previous_caution = last_value, last_caution
        last_value, last_caution = minimum, caution
        state['slot']['min'] = current
        state['slot_prev']['min'] = previous_card
        state['slot_since']['min'] = since
        state['minimum_report'] = dict(month=env['periods'][index],value=minimum,
            caution=caution,tied=tied,previous_value=previous_value,
            previous_caution=previous_caution)
        state['excluded'].add(current)
        live = [code for code in env['codes'] if state['act'][code]]
        ordered = sorted(live, key=lambda code:
                         (-state['vals'][env['SORT_COL']][code], code))
        state['overall_ranks'] = {code:i+1 for i,code in enumerate(ordered)}
    return states


current_state = None


def draw_row(canvas, code, y, vals, axis, alpha, t, grow,
             rank=None, lift=0.0, ring=None):
    if rank is not None and current_state is not None:
        rank = current_state['overall_ranks'][code]
    return original_row(canvas, code, y, vals, axis, alpha, t, grow,
                        rank=rank, lift=lift, ring=ring)


def draw_slot(canvas, state, key, y, vals, axis, rows_a, t, grow, frame, rank=None):
    if key != 'min':
        return original_slot(canvas,state,key,y,vals,axis,rows_a,t,grow,frame,rank=rank)
    report=state['minimum_report']
    since=state['slot_since']['min']
    k=env['ease_in_out'](min(1.0,(frame-since)/env['SLOT_FADE'])) if since>0 else 1.0
    selected=[(state['slot']['min'],report['value'],report['caution'],k,-18*env['U']*(1-k))]
    if state['slot_prev']['min'] and k<1:
        selected.insert(0,(state['slot_prev']['min'],report['previous_value'],
                           report['previous_caution'],1-k,18*env['U']*k))
    old_fmt=env['fmt']
    for code,value,caution,alpha,offset in selected:
        display={s:dict(by_code) for s,by_code in vals.items()}
        display[env['SORT_COL']][code]=value
        original_name=env['ENT'][code]['name']
        if caution and not original_name.endswith('*'):
            env['ENT'][code]['name']=original_name+'*'
        def precise(v,with_unit=False):
            number=f"{v:.{cfg['comparison']['decimals']}f}".rstrip('0').rstrip('.')
            return number+(' bcm' if with_unit else '')
        env['fmt']=precise
        try:
            original_row(canvas,code,y+offset,display,axis,rows_a*alpha,t,grow,
                         rank=None,ring=env['C_LOW'])
        finally:
            env['fmt']=old_fmt
            env['ENT'][code]['name']=original_name


def draw_block_label(canvas, y, label, color, alpha, icon=None):
    if label == cfg['text']['min_label']:
        icon = None
    return original_label(canvas, y, label, color, alpha, icon=icon)


def render_frame(canvas, frame, state):
    global current_state
    current_state = state
    return original_frame(canvas, frame, state)


def draw_event(canvas, t):
    if t <= env['T_INTRO']:
        virtual_time = t
    else:
        virtual_time = env['T_INTRO'] + month_at(t)/(nm-1)*env['T_RACE']
        virtual_time += max(0, t-env['T_INTRO']-env['T_RACE'])
    return original_event(canvas, virtual_time)


env.update(month_at=month_at, precompute=precompute, draw_row=draw_row,
           draw_block_label=draw_block_label, render_frame=render_frame,
           draw_event=draw_event,draw_slot=draw_slot)
if __name__ == '__main__':
    module['main']()
